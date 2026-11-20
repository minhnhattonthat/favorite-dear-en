"""Phase 5 gate for tools/insert.py, en.py and font_en.py.

- the English font: every glyph fits its 5-px half cell, every printable ASCII has a glyph;
- en.encode: pair codes stay between the Japanese font and the printer codes;
- script rebuild: replacing every segment with its own bytes gives the original file; the marker build (segments
  grown and shrunk) re-parses, keeps every item, and every reference still lands on the same item or segment start;
- PSX.EXE in place: the marker never writes outside the original string slots.
"""
import string
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import en  # noqa: E402
import evscript  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402
import insert  # noqa: E402

TREE = ROOT / "work" / "disc" / "tree"
disc_only = pytest.mark.skipif(not (TREE / "PSX.EXE").is_file(), reason="disc not unpacked to work/disc/tree")


def test_font_fits_half_cell():
    g = font_en.glyphs()
    assert set(map(ord, string.printable[:95])) <= set(g)
    for code, rows in g.items():
        assert all(r < 1 << font_en.WIDTH for r in rows), f"glyph {code:#x} wider than {font_en.WIDTH} px"
    assert len(font_en.binary()) == 12 * (font_en.LAST - font_en.FIRST + 1)


def test_pair_codes_clear_of_font_and_printer():
    t = extract.event_table()
    data = en.encode("{spk:0080}" + "".join(font_en.chars().values()) + "{n}x{end}", t)
    hws = [h for (h,) in struct.iter_unpack("<H", data)]
    nl = hws.index(0xFFF0)
    text = hws[2:nl] + hws[nl + 1:-1]
    assert all(evscript.EN_LO <= h < 0xFF00 and en.is_pair(h) for h in text)
    assert hws[:2] == [0xFFF1, 0x8000] and hws[-1] == 0xFFFF  # tbl args are file byte order


@pytest.fixture(scope="module")
def disc():
    return (TREE / "PSX.EXE").read_bytes(), (TREE / "GDATA.BIN").read_bytes()


@disc_only
def test_rebuild_identity(disc):
    for sec, size, data, where in evscript.script_files(*disc):
        sc = evscript.Script(data)
        repl = {a: sc.seg_bytes((a, b)) for a, b in sc.segments}
        assert insert.script_bytes(sc, size, repl) == data[:size] + bytes(max(0, size - len(data)))


@disc_only
def test_grown_script_moves(disc):
    """a script that outgrows its slot goes to the end of GDATA (sector-rounded) and its table entry is repointed
    once per EXE; the moved file re-parses with the same items"""
    exe, gdata = disc
    relocs = []
    new_gdata = insert.event_edits(gdata, exe, "en", extract.event_table(), relocs=relocs)
    if not relocs:
        pytest.skip("no script outgrows its slot with the current English")
    new_exe = insert.repoint(exe, relocs, "PSX.EXE")
    by_sec = {f[0]: f for f in evscript.script_files(new_exe, new_gdata)}
    end = -(-len(gdata) // 2048)
    for sec, size, nsec, nsize in relocs:
        assert nsec >= end and nsize % 2048 == 0 and size < nsize <= insert.EVENT_BUFFER
        assert by_sec[nsec][1] == nsize and sec not in by_sec  # the table now points at the moved copy only
        old, new = evscript.Script(gdata[sec * 2048:sec * 2048 + size]), evscript.Script(by_sec[nsec][2])
        assert [k for k, *_ in old.items] == [k for k, *_ in new.items]
    with pytest.raises(insert.FitError):
        insert.repoint(new_exe, relocs, "PSX.EXE")  # the old entry is gone: a second repoint must fail loudly


@disc_only
def test_grown_exe_string_moves(disc):
    """a PSX.EXE string longer than its slot moves to insert.REPOINT: every table pointer to it now reads the full
    English, and nothing outside the slots, the pointer entries and REPOINT changes"""
    exe, _ = disc
    table = extract.exe_table()
    report = []
    new = insert.exe_text(exe, "en", table, report)
    if not report:
        pytest.skip("no PSX.EXE string outgrows its slot with the current English")
    rows = {r["id"]: r for r in extract.read_tsv(extract.SCRIPT / "exe.tsv")}
    for line in report:
        rid = line.split()[0]
        off = int(rid.split(".")[1], 16)
        ptrs = extract.table_pointers(exe, off)
        want = en.encode(rows[rid]["en"], table)
        for p in ptrs:
            va = struct.unpack_from("<I", new, p)[0]
            assert insert.REPOINT[0] <= va < insert.REPOINT[1]
            assert new[va - extract.EXE_VA:va - extract.EXE_VA + len(want)] == want


@disc_only
def test_marker_relocation(disc):
    exe, gdata = disc
    new_gdata = insert.event_edits(gdata, exe, "marker", extract.event_table())
    for sec, size, data, where in evscript.script_files(exe, gdata):
        old = evscript.Script(data)
        new = evscript.Script(new_gdata[sec * 2048:sec * 2048 + size])
        assert [k for k, *_ in old.items] == [k for k, *_ in new.items], f"{sec:04X}: item kinds changed"
        # map each old item start to the new one, then check every reference target moved with it
        starts = {a: b for (_, a, _), (_, b, _) in zip(old.items, new.items)}
        seg_starts = {a: b for (a, _), (b, _) in zip(old.segments, new.segments)}
        assert len(old.refs) == len(new.refs)
        for (op, i, t), (nop, ni, nt) in zip(old.refs, new.refs):
            assert i == ni and starts.get(op, op) == nop, f"{sec:04X}: ref at op {op:#x} moved oddly"
            want = starts.get(t, seg_starts.get(t, t if t < old.start else None))
            assert nt == want, f"{sec:04X}: ref {op:#x}/{i} -> {t:#x} now {nt:#x}, want {want}"


@disc_only
def test_exe_marker_in_place(disc):
    exe, _ = disc
    new = insert.exe_text(exe, "marker", extract.exe_table())
    allowed = bytearray(len(exe))
    for row in extract.read_tsv(extract.SCRIPT / "exe.tsv"):
        off = int(row["id"].split(".")[1], 16)
        n = len(extract.exe_table().encode(row["jp"]))
        allowed[off:off + n] = b"\1" * n
    bad = [i for i in range(len(exe)) if exe[i] != new[i] and not allowed[i]]
    assert not bad, f"marker wrote outside string slots at {bad[:5]}"


@disc_only
@pytest.mark.parametrize("mode", ["marker", "ruler"])
def test_exe_codes_kept(disc, mode):
    """a marker or ruler cut to fit its slot keeps every control code of the row ({wait}{end} included)"""
    exe, _ = disc
    table = extract.exe_table()
    new = insert.exe_text(exe, mode, table)
    for row in extract.read_tsv(extract.SCRIPT / "exe.tsv"):
        if "name-entry grid" in row["notes"]:
            continue
        off = int(row["id"].split(".")[1], 16)
        n = len(table.encode(row["jp"]))
        def codes(b):  # control codes with their arguments; glyphs (Japanese < 0x670, pairs <= 0x8484) skipped
            hw, out, i = struct.unpack("<%dH" % (len(b) // 2), b), [], 0
            while i < len(hw):
                if hw[i] >= 0xFF00:
                    k = extract.EXE_ARGS.get(hw[i], 0)
                    out.append(hw[i:i + 1 + k])
                    if hw[i] == 0xFFFF:
                        break
                    i += 1 + k
                else:
                    i += 1
            return out
        assert codes(new[off:off + n]) == codes(exe[off:off + n]), row["id"]


NAME_TABLE = (0x163E40, 0x164E7A)  # event names, 9-byte ASCII records at RAM 0x80173640 ("SEND12" ends it)


@disc_only
@pytest.mark.parametrize("mode", ["marker", "ruler"])
def test_exe_data_untouched(disc, mode):
    """non-text the event engine reads by name must survive every mode: a marker in the name table's tail crashed
    the game at the next event load (strcpy of an unterminated name wiped RAM)"""
    exe, _ = disc
    new = insert.exe_text(exe, mode, extract.exe_table())
    for lo, hi in [NAME_TABLE, (0x164E7A, 0x1660E0)] + extract.EXE_DATA:
        assert new[lo:hi] == exe[lo:hi], f"{mode} wrote into data {lo:#x}-{hi:#x}"


@disc_only
def test_epilog_patch():
    """EPILOG.EXE: one sector appended, pc0 -> the copy stub, the renderer's first word jumps to the blob; nothing
    else in the original image changes"""
    old = (TREE / "TITLE" / "EPILOG.EXE").read_bytes()
    new = insert.assemble(old, "epilog.asm")
    assert len(new) == len(old) + 0x800
    pc0, _, taddr, tsize = struct.unpack_from("<4I", new, 0x10)
    assert (pc0, taddr, tsize) == (0x8009F800, 0x80010000, 0x90000)
    hook = 0x800526E8 - 0x80010000 + 0x800
    assert struct.unpack_from("<I", new, hook)[0] == 0x08000000 | (0x80170000 & 0x0FFFFFFF) >> 2
    changed = {i for i in range(len(old)) if old[i] != new[i]}
    assert changed <= set(range(0x10, 0x14)) | set(range(0x1C, 0x20)) | set(range(hook, hook + 8))


def test_staff_text():
    row = {"id": "STAFF.009", "jp": "　　　　　　小川　雄一郎", "en": "Yuichiro Ogawa"}
    assert insert.staff_text(row, "en") == bytes(b + 1 for b in font_en.fin_pairs("Yuichiro Ogawa"))  # pair codes
    assert insert.staff_text(row, "marker") == "　" * 6 + "［００９］Ｔ"  # same glyph count
    card = {"id": "STAFF.460", "jp": "&　　　　　ＳＯＦＩＸ", "en": "&    SOFIX"}
    assert insert.staff_text(card, "en")[:1] == b"&"  # the single-byte '&' code stays
    assert insert.staff_text(card, "marker").startswith("&　　　　　［４６０］")
