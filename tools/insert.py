"""insert.py: put the English (or marker) text into PSX.EXE and the GDATA event scripts. build.py calls edits().

    python -X utf8 tools/insert.py stats [--mode en|marker|ruler]   scripts changed and the tightest files

Modes: 'en' writes each row's `en` cell (rows with an empty `en` stay Japanese); 'marker' writes `[id]` + filler
into every row (the phase 5 marker build), keeping each row's control codes and its glyph count x 2 letters, so a
line keeps its width; 'ruler' puts RULER (44 letters) in each row's first line for the width gate (a script it
doesn't fit gets markers); 'torture' puts TORTURE (every glyph, three lines) in each event row the same way.
DATA/STAFF.TXT (credits) gets full-width text: FIN.EXE draws only double-byte characters.

Event scripts (docs/re/events.md): a row is a text segment; new text may grow or shrink it. The script's code is
rebuilt piece by piece and every reference argument (Script.refs, incl. the pc-0 goto) is remapped to the new pc of
its target. A file that outgrows its sector-rounded slot moves to the end of GDATA.BIN and its table entry is
repointed in all five EXEs (event_edits/repoint); no file may pass 0x7000 bytes, the cap of the buffer the loader
packs up to 10 scripts into (0x800C82E8, cap 0x3800 halfwords at 0x800C8380). PSX.EXE strings are written in place (FFFF-terminated, the rest of the slot zero-filled): they must
not grow until repointing exists. The pair-glyph hook is assembled into PSX.EXE by armips (asm/font.asm)."""
import argparse
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import en  # noqa: E402
import evscript  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402
from tbl import TOKEN  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "work" / "disc" / "tree"
ARMIPS = ROOT / "tools" / "armips" / "armips.exe"
FILLER = "The quick brown fox jumps over the lazy dog. "
SECTOR = 2048


class FitError(ValueError):
    pass


# --- text -----------------------------------------------------------------------------------------------------------


def runs(jp):
    """split a row's markup into [(is_text, piece)]: text = glyph characters, else one control/escape token"""
    out, i, buf = [], 0, []
    while i < len(jp):
        m = TOKEN.match(jp, i)
        if m:
            if buf:
                out.append((True, "".join(buf)))
                buf = []
            out.append((False, m[0]))
            i = m.end()
        else:
            buf.append(jp[i])
            i += 1
    if buf:
        out.append((True, "".join(buf)))
    return out


def marker(row_id, jp):
    """`[id]` + filler in place of the row's glyphs: each run of k glyphs becomes 2k letters (the same cells), the
    first run at least long enough for the id; control codes stay."""
    tag = "[" + row_id.replace(".", "").replace("PSX", "") + "]"
    out, first, k = [], True, 0
    for is_text, piece in runs(jp):
        if not is_text:
            out.append(piece)
            continue
        n = 2 * len(piece)
        if first:
            s = (tag + FILLER * 4)[:max(n, len(tag))]
            first = False
        else:
            s = (FILLER * 4)[k % len(FILLER):][:n]
            k += n
        out.append(s)
    return "".join(out)


RULER = "1234567890ABCDEFGHIJ1234567890abcdefghij+-*/"  # 44 letters: the last one visible = the line's limit


# every glyph of fonts/en6x12.txt plus double spaces, as three 40-letter dialogue lines (the glyph torture line)
TORTURE = ("{n}".join([" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFG",
                       "HIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmno",
                       "pqrstuvwxyz{|}~…—♥♪é  A  B   C  Ww Mm"]))


def ruler(row_id, jp, first=RULER):
    """the width gate: the row's first text run becomes RULER (one full line), the rest as in marker()"""
    out, done = [], False
    for is_text, piece in runs(marker(row_id, jp)):
        if is_text and not done:
            piece, done = first, True
        out.append(piece)
    return "".join(out)


def row_text(row, mode):
    if mode == "marker":
        return marker(row["id"], row["jp"])
    if mode == "ruler":
        return ruler(row["id"], row["jp"])
    if mode == "torture":
        return ruler(row["id"], row["jp"], TORTURE)
    return row["en"] or None


# --- event scripts --------------------------------------------------------------------------------------------------


def rebuild(sc, repl):
    """new code halfwords for Script `sc` with segments replaced: repl = {segment start pc: new bytes}."""
    code, n = sc.code, sc.n
    seg_end = dict(sc.segments)
    pieces, pc, new = [], 0, []  # (old start, old end, new start, replaced)
    for s in sorted(repl):
        e = seg_end[s]
        if s > pc:
            pieces.append((pc, s, len(new), False))
            new.extend(code[pc:s])
        data = repl[s]
        pieces.append((s, e, len(new), True))
        new.extend(struct.unpack("<%dH" % (len(data) // 2), data))
        pc = e
    if pc < n:
        pieces.append((pc, n, len(new), False))
        new.extend(code[pc:n])

    def newpos(t):
        for a, b, ns, replaced in pieces:
            if a <= t < b:
                if replaced and t != a:
                    raise FitError(f"reference to pc {t:#x} inside a replaced segment {a:#x}-{b:#x}")
                return ns + (t - a)
        raise FitError(f"reference to pc {t:#x} outside the code")

    for op, i, t in sc.refs:
        new[newpos(op) + 1 + i] = 0x8000 | newpos(t)
    if len(new) > 0x7FFF:
        raise FitError("code past the 15-bit reference range")
    return new


def script_bytes(sc, size, repl):
    new = rebuild(sc, repl)
    out = sc.data[:sc.code_off] + struct.pack("<%dH" % len(new), *new)
    if len(out) > size:
        raise FitError(f"{len(out):#x} bytes > its {size:#x}-byte slot")
    return out + bytes(size - len(out))


EVENT_BUFFER = 0x7000  # the loader's cap (0x3800 halfwords at 0x800C8380): no script may be larger
EXE_COPIES = ("PSX.EXE", "GOVER.EXE", "FD_BALL.EXE", "PS_MOV.EXE", "TITLE/EPILOG.EXE")  # each holds the GDATA tables


def event_edits(gdata, exe, mode, table, report=None, relocs=None):
    """GDATA with the new scripts. A script that outgrows its slot (en/marker) is moved to the end of GDATA.BIN when
    `relocs` is a list: each move is appended as (old sector, old size, new sector, new size) for repoint(). The
    loader (0x800C82E8) reads a script's size from the table, appends it to the buffer while it fits under the cap
    and compacts the buffer otherwise, so a moved file only needs a sector-rounded size <= EVENT_BUFFER."""
    rows_by_sec = {}
    for path in sorted((extract.SCRIPT / "events").glob("*.tsv")):
        rows_by_sec[int(path.stem, 16)] = extract.read_tsv(path)
    out = bytearray(gdata)
    out += bytes(-len(out) % SECTOR)
    hi = 0
    for sec, size, data, where in evscript.script_files(exe, gdata):
        sc = evscript.Script(data)

        def replacements(m):
            repl = {}
            for row in rows_by_sec.get(sec, []):
                text = row_text(row, m)
                if text is not None:
                    repl[(int(row["id"].split(".")[1], 16) - sc.code_off) // 2] = en.encode(text, table)
            return repl

        repl = replacements(mode)
        if not repl:
            continue
        try:
            new = script_bytes(sc, size, repl)
        except FitError as e:
            if mode in ("ruler", "torture"):
                new = script_bytes(sc, size, replacements("marker"))  # ruler doesn't fit: this file gets markers
            elif relocs is not None and where != "orphan" and "slot" in str(e):
                body = script_bytes(sc, EVENT_BUFFER, repl).rstrip(b"\0")
                nsize = -(-len(body) // SECTOR) * SECTOR
                nsec = len(out) // SECTOR
                out += body + bytes(nsize - len(body))
                relocs.append((sec, size, nsec, nsize))
                if report is not None:
                    report.append((sec, nsize, sc.code_off + 2 * sc.n, len(body)))
                continue
            else:
                raise FitError(f"script {sec:04X}: {e}") from None
        if report is not None:
            used = len(new.rstrip(b"\0"))
            report.append((sec, size, sc.code_off + 2 * sc.n, used))
        out[sec * SECTOR:sec * SECTOR + size] = new
        hi = max(hi, sec * SECTOR + size)
    if not relocs:
        out = out[:max(len(gdata), hi)]  # nothing moved: no sector padding (the last file may run past the end)
    return bytes(out)


def repoint(exe, relocs, name):
    """`exe` with each moved script's (u32 sector, u32 size) table entry rewritten; every move must match exactly one
    4-aligned entry (all five EXEs carry the same tables)."""
    out = bytearray(exe)
    for sec, size, nsec, nsize in relocs:
        old = struct.pack("<II", sec, size)
        hits = [i for i in range(0, len(out) - 7, 4) if out[i:i + 8] == old]
        if len(hits) != 1:
            raise FitError(f"{name}: script {sec:04X} table entry found {len(hits)} times")
        out[hits[0]:hits[0] + 8] = struct.pack("<II", nsec, nsize)
    return bytes(out)


# --- PSX.EXE --------------------------------------------------------------------------------------------------------


def fit_slot(row, mode, size, table):
    """marker/ruler text for an in-place PSX.EXE slot of `size` bytes: shorten the first text run two letters at a
    time; every control code and its arguments stay (a byte cut once dropped the {wait}{end} and hung the opening)"""
    pieces = runs(row_text(row, mode))
    first = next(i for i, (is_text, _) in enumerate(pieces) if is_text)
    while True:
        new = en.encode("".join(p for _, p in pieces), table)
        if len(new) <= size or not pieces[first][1]:
            break
        pieces[first] = (True, pieces[first][1][:-2])
    if len(new) > size:
        raise FitError(f"{row['id']}: control codes alone need {len(new)} bytes > {size}")
    return new


# Grown PSX.EXE strings move here: the end of the zero run 0x80124E5D-0x80125AF0 that also holds the font hook
# (asm/font.asm stops the hook at REPOINT[0]); a 48-letter test string at 0x80125900 drew fine (docs/re/space.md).
REPOINT = (0x80125500, 0x80125AF0)


def exe_text(exe, mode, table, report=None):
    """PSX.EXE strings in place; in `en` mode a string longer than its slot moves to REPOINT when the pointer tables
    point straight at it (extract.table_pointers), and its old slot keeps a cut copy. `report` gets one line per move."""
    out = bytearray(exe)
    mode = "marker" if mode == "torture" else mode  # torture: event dialogue only
    cursor = REPOINT[0]
    for row in extract.read_tsv(extract.SCRIPT / "exe.tsv"):
        if "name-entry grid" in row["notes"]:
            continue  # fixed cells, not a string (phase 7: Latin grid)
        text = row_text(row, mode)
        if text is None:
            continue
        off = int(row["id"].split(".")[1], 16)
        old = table.encode(row["jp"])
        new = en.encode(text, table)
        if len(new) > len(old):
            ptrs = extract.table_pointers(exe, off) if mode == "en" else []
            if mode == "en" and not ptrs:
                raise FitError(f"{row['id']}: {len(new)} bytes > {len(old)} and no table pointer to move it")
            if ptrs:
                moved = new + bytes(-len(new) % 4)
                if cursor + len(moved) > REPOINT[1]:
                    raise FitError(f"{row['id']}: repoint space 0x{REPOINT[0]:08X}-0x{REPOINT[1]:08X} is full")
                at = cursor - extract.EXE_VA
                out[at:at + len(moved)] = moved
                for p in ptrs:
                    out[p:p + 4] = struct.pack("<I", cursor)
                if report is not None:
                    report.append(f"{row['id']} -> 0x{cursor:08X} ({len(new)} bytes, {len(ptrs)} pointer(s))")
                cursor += len(moved)
            new = fit_slot(row, mode, len(old), table)
        out[off:off + len(old)] = new + bytes(len(old) - len(new))
    return bytes(out)


# --- DATA/STAFF.TXT (credits) ---------------------------------------------------------------------------------------


def fullwidth(s):
    """ASCII -> Shift-JIS full-width forms (FIN.EXE draws only double-byte characters: docs/re/text.md §Credits)"""
    return "".join(chr(ord(c) + 0xFEE0) if "!" <= c <= "~" else "　" if c == " " else c for c in s)


def staff_text(row, mode):
    """a credits line: marker/ruler keep the line's leading indent and glyph count; en = the `en` cell, full-width.
    A leading '&' (the closing cards, STAFF.457-460) is a single-byte code and stays single-byte."""
    jp = row["jp"]
    code = jp[:len(jp) - len(jp.lstrip("&"))]
    if mode == "en":
        return code + fullwidth(row["en"].lstrip("&")) if row["en"] else None
    body = jp[len(code):].lstrip("　")
    indent = jp[:len(jp) - len(body)]  # the code and the full-width spaces
    if mode == "ruler":
        return indent + fullwidth(RULER[:24])
    tag = "[" + row["id"].split(".")[1] + "]"
    return indent + fullwidth((tag + FILLER * 2)[:max(len(body), len(tag))])


def staff_edit(data, mode):
    lines = extract.staff_lines(data)
    for row in extract.read_tsv(extract.SCRIPT / "staff.tsv"):
        text = staff_text(row, mode)
        if text is not None:
            lines[int(row["id"].split(".")[1])] = extract.staff_encode(text)
    return extract.STAFF_NL.join(lines)


def assemble(exe, asm="font.asm"):
    """EXE bytes with asm/<asm> applied (font.asm: PSX.EXE, epilog.asm: TITLE/EPILOG.EXE)"""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "in.exe").write_bytes(exe)
        (d / "font.bin").write_bytes(font_en.binary())
        r = subprocess.run([str(ARMIPS), str(ROOT / "asm" / asm), "-strequ", "EXE_IN", str(d / "in.exe"),
                            "-strequ", "EXE_OUT", str(d / "out.exe"), "-strequ", "FONT_BIN", str(d / "font.bin")],
                           capture_output=True, text=True, cwd=ROOT / "asm")  # .include resolves from the cwd
        if r.returncode != 0:
            raise RuntimeError(f"armips failed:\n{r.stdout}\n{r.stderr}")
        return (d / "out.exe").read_bytes()


def edits(mode="en", report=None):
    exe = (TREE / "PSX.EXE").read_bytes()
    gdata = (TREE / "GDATA.BIN").read_bytes()
    relocs = []
    new_gdata = event_edits(gdata, exe, mode, extract.event_table(), report, relocs)
    out = {"PSX.EXE": assemble(exe_text(exe, mode, extract.exe_table())),
           "TITLE/EPILOG.EXE": assemble((TREE / "TITLE" / "EPILOG.EXE").read_bytes(), "epilog.asm")}
    if relocs:
        for name in EXE_COPIES:
            out[name] = repoint(out[name] if name in out else (TREE / name).read_bytes(), relocs, name)
    if new_gdata != gdata:
        out["GDATA.BIN"] = new_gdata
    staff = (TREE / "DATA" / "STAFF.TXT").read_bytes()
    new_staff = staff_edit(staff, mode)
    if new_staff != staff:
        out["DATA/STAFF.TXT"] = new_staff
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["stats"])
    ap.add_argument("--mode", choices=["en", "marker", "ruler", "torture"], default="en")
    a = ap.parse_args()
    rep = []
    edits(a.mode, rep)
    rep.sort(key=lambda r: r[3] - r[1], reverse=True)
    print(f"{len(rep)} scripts changed")
    for sec, size, old, used in rep[:10]:
        print(f"  {sec:04X}: slot {size:#06x}, was {old:#06x}, now {used:#06x} ({size - used:+#x} left)")
