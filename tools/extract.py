"""extract.py: dump every Japanese string on the disc to script/*.tsv (columns: id, jp, en, notes).

    python -X utf8 tools/extract.py [--disc work/disc/tree] [--force]

Sources (docs/re/text.md, events.md):
    script/events/<SECTOR>.tsv  event-script text (GDATA.BIN), one file per script, id <SECTOR>.<file byte offset>
    script/exe.tsv              PSX.EXE strings (two text regions + the name-entry grids), id PSX.<offset>
    script/staff.tsv            DATA/STAFF.TXT credits, one row per text line, id STAFF.<line>
    script/sjis.tsv             Shift-JIS memory-card titles in the EXEs, id <EXE>.<offset>
Ids are original addresses and never change. Re-running keeps `en` and `notes` of existing rows; it refuses to drop a
row that has an `en` unless --force. The `jp` column round-trips byte-exact through the codecs here (`encode_row`),
which tests/test_extract.py checks for every row, along with coverage of the text ranges.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import evscript  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"
COLS = ["id", "jp", "en", "notes"]

# --- tables ---------------------------------------------------------------------------------------------------------


def _lines(path):
    return Path(path).read_text(encoding="utf-8-sig").splitlines()


def exe_table():
    return Table.load(ROOT / "tbl/jp.tbl")


def event_table():
    """jp.tbl glyphs + tbl/ev.tbl printer codes (the two printers give FFxx different meanings)."""
    glyphs = [ln for ln in _lines(ROOT / "tbl/jp.tbl") if not ln.startswith("#") and "={" not in ln]
    return Table(glyphs + _lines(ROOT / "tbl/ev.tbl"))


def has_text(codes):
    """at least one font code that isn't a blank: rows without any are codes-only and stay out of the TSVs"""
    return any(0 < c < evscript.NCODES and c != 0x5E9 for c in codes)


# --- event scripts --------------------------------------------------------------------------------------------------


def event_rows(exe, gdata, table=None):
    """{sector: [row]} with row = dict(id, jp, raw, notes); raw = original bytes. Also returns the parsed scripts."""
    table = table or event_table()
    out, scripts = {}, {}
    for sec, size, data, where in evscript.script_files(exe, gdata):
        sc = evscript.Script(data)
        scripts[sec] = (sc, where)
        msg_starts = {s for kind, s, e in sc.items if kind == "msg"}
        rows = []
        for seg in sc.segments:
            a, b = seg
            if not has_text(sc.code[a:b]):
                continue
            raw = sc.seg_bytes(seg)
            text, used = table.decode(raw, 0, len(raw))
            notes = []
            if a not in msg_starts:
                notes.append("entry point inside the previous row's message")
            if where == "orphan":
                notes.append("orphan script (no file table sizes it)")
            rows.append(dict(id=f"{sec:04X}.{sc.byte(a):04X}", jp=text, raw=raw, notes="; ".join(notes)))
        out[sec] = rows
    return out, scripts


# --- PSX.EXE --------------------------------------------------------------------------------------------------------

EXE_REGIONS = [(0x155F3C, 0x15CAB0), (0x164E7A, 0x16667E)]  # docs/re/text.md
EXE_GRIDS = [(0x17DA4, 0x17E0A), (0x17E64, 0x1801A)]  # name-entry character grids (fixed layout)
# Non-text inside EXE_REGIONS (u32 pointer tables, layout records, a palette): the coverage test allows these only.
EXE_DATA = [(0x156818, 0x156A94), (0x159F78, 0x15A858), (0x15C7D8, 0x15C968), (0x1656D6, 0x1660E0)]
EXE_ARGS = {0xFFFE: 0, 0xFFFC: 0, 0xFFFD: 0, 0xFFFB: 0, 0xFF00: 1, 0xFF10: 1, 0xFF20: 1, 0xFF90: 2, 0xFFE0: 2}
EXE_VA = 0x80010000 - 0x800  # vaddr = file offset + EXE_VA


def exe_strings(exe, lo, hi):
    """[(start, end)] FFFF-terminated strings in exe[lo:hi]. A string that ends 2 bytes off a 4-byte boundary is
    followed by one 0x0000 pad (verified: 347 pointers land just after it). Non-string halfwords are skipped."""
    hw = struct.unpack_from("<%dH" % ((hi - lo) // 2), exe, lo)
    out, i, s = [], 0, 0
    while i < len(hw):
        v = hw[i]
        if v == 0xFFFF:
            out.append((lo + 2 * s, lo + 2 * i + 2))
            i += 1
            if (lo + 2 * i) % 4 == 2 and i < len(hw) and hw[i] == 0:
                i += 1
            s = i
        elif v < evscript.NCODES:
            i += 1
        elif v in EXE_ARGS:
            i += 1 + EXE_ARGS[v]
        else:
            i += 1
            s = i
    return out


def exe_pointers(exe):
    """{file offset: [offsets of u32 words pointing at it]} for targets in the text regions"""
    out = {}
    for o in range(0x800, len(exe) - 3, 4):
        f = struct.unpack_from("<I", exe, o)[0] - EXE_VA
        if any(lo <= f < hi for lo, hi in EXE_REGIONS + EXE_GRIDS):
            out.setdefault(f, []).append(o)
    return out


def exe_rows(exe, table=None):
    table = table or exe_table()
    ptrs = exe_pointers(exe)
    rows = []
    for lo, hi in EXE_REGIONS:
        for s, e in exe_strings(exe, lo, hi):
            codes = struct.unpack_from("<%dH" % ((e - s) // 2), exe, s)
            if not has_text(codes):
                continue
            raw = exe[s:e]
            text, _ = table.decode(raw, 0, len(raw))
            rows.append(dict(id=f"PSX.{s:06X}", jp=text, raw=raw, notes="" if s in ptrs else "no direct pointer"))
    for lo, hi in EXE_GRIDS:  # one row each: {end} here marks an empty cell, not the end of a string
        raw = exe[lo:hi]
        text, _ = table.decode(raw, 0, len(raw))
        rows.append(dict(id=f"PSX.{lo:06X}", jp=text, raw=raw,
                         notes=f"name-entry grid: exactly {len(raw) // 2} cells, {{end}} = empty cell"))
    return rows


# --- DATA/STAFF.TXT -------------------------------------------------------------------------------------------------

STAFF_NL = b"\x0e\x0b"


def staff_decode(b):
    """Shift-JIS with both bytes of a double-byte character +1; single bytes stay (ASCII, '$')."""
    out, i = [], 0
    while i < len(b):
        c = b[i]
        if (0x82 <= c <= 0xA0 or 0xE1 <= c <= 0xF0) and i + 1 < len(b):
            out.append(bytes([c - 1, b[i + 1] - 1]).decode("cp932"))
            i += 2
        elif 0x20 <= c < 0x7F:
            out.append(chr(c))
            i += 1
        else:
            out.append("[%02X]" % c)
            i += 1
    return "".join(out)


def staff_encode(s):
    out = bytearray()
    i = 0
    while i < len(s):
        if s[i] == "[" and i + 3 < len(s) and s[i + 3] == "]":
            out.append(int(s[i + 1:i + 3], 16))
            i += 4
            continue
        ch = s[i]
        if ord(ch) < 0x80:
            out.append(ord(ch))
        else:
            out += bytes(x + 1 for x in ch.encode("cp932"))
        i += 1
    return bytes(out)


def staff_lines(data):
    """the file split at 0E 0B; the last piece holds the 0xFF terminator"""
    return data.split(STAFF_NL)


def staff_rows(data):
    rows = []
    for n, line in enumerate(staff_lines(data)):
        text = staff_decode(line)
        if text.strip("　 $[FF]"):
            rows.append(dict(id=f"STAFF.{n:03d}", jp=text, raw=line, notes=""))
    return rows


# --- Shift-JIS memory-card titles -----------------------------------------------------------------------------------

SJIS = [("PSX.EXE", 0x1D770), ("TITLE/EPILOG.EXE", 0x48330), ("FD_BALL.EXE", 0x11A4), ("PS_MOV.EXE", 0x11A4),
        ("TITLE/EPILOG.EXE", 0x11A4)]


def sjis_rows(tree):
    rows = []
    for name, off in SJIS:
        data = (Path(tree) / name).read_bytes()
        end = data.index(b"\0", off)
        raw = data[off:end]
        field = 64  # memory-card header title: 64 bytes, NUL-padded
        note = f"memory-card title, Shift-JIS, at most {field} bytes"
        if "TEST" in raw.decode("cp932"):
            note += "; debug leftover (save title of a test build)"
        rows.append(dict(id=f"{Path(name).stem}.{off:06X}", jp=raw.decode("cp932"), raw=raw, notes=note))
    return rows


# --- TSV ------------------------------------------------------------------------------------------------------------


def read_tsv(path):
    """plain tab-separated, no quoting (the text has \" stand-ins); every row must have len(COLS) fields"""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    head = lines[0].split("\t")
    if head != COLS:
        raise ValueError(f"{path}: header {head} != {COLS}")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        rec = line.rstrip("\r").split("\t")
        if len(rec) != len(COLS):
            raise ValueError(f"{path}:{n}: {len(rec)} columns, want {len(COLS)}")
        rows.append(dict(zip(COLS, rec)))
    return rows


def write_tsv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = ["\t".join(COLS)]
    for r in rows:
        rec = [r.get(c, "") for c in COLS]
        if any("\t" in v or "\n" in v or "\r" in v for v in rec):
            raise ValueError(f"{r['id']}: tab or newline in a field")
        out.append("\t".join(rec))
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def merge(path, rows, force):
    """keep en/notes of existing rows; refuse to lose a translated row unless force"""
    old = {r["id"]: r for r in read_tsv(path)} if path.exists() else {}
    new_ids = {r["id"] for r in rows}
    lost = [i for i, r in old.items() if i not in new_ids and r["en"]]
    if lost and not force:
        raise SystemExit(f"{path}: would drop translated rows {lost[:5]}... (use --force)")
    out = []
    for r in rows:
        o = old.get(r["id"])
        out.append(dict(id=r["id"], jp=r["jp"], en=o["en"] if o else "",
                        notes=o["notes"] if o and o["notes"] else r["notes"]))
    write_tsv(path, out)
    return len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disc", default=str(ROOT / "work/disc/tree"))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    tree = Path(a.disc)
    exe = (tree / "PSX.EXE").read_bytes()
    gdata = (tree / "GDATA.BIN").read_bytes()
    ev, _ = event_rows(exe, gdata)
    n = 0
    for sec, rows in ev.items():
        if rows:
            n += merge(SCRIPT / "events" / f"{sec:04X}.tsv", rows, a.force)
    print(f"events: {n} rows in {sum(1 for r in ev.values() if r)} files")
    print(f"exe: {merge(SCRIPT / 'exe.tsv', exe_rows(exe), a.force)} rows")
    print(f"staff: {merge(SCRIPT / 'staff.tsv', staff_rows((tree / 'DATA/STAFF.TXT').read_bytes()), a.force)} rows")
    print(f"sjis: {merge(SCRIPT / 'sjis.tsv', sjis_rows(tree), a.force)} rows")


if __name__ == "__main__":
    main()
