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
