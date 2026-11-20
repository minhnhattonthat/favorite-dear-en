"""Battle name plates (tools/btname.py, asm/btname.inc): every name fits its 64-px plate, the Japanese column is what
the EXE tables hold, and the assembled EXE carries the English records where the routine reads them."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import btname  # noqa: E402

need_disc = pytest.mark.skipif(not (btname.TREE / "PSX.EXE").is_file(), reason="no unpacked disc")


def test_names_fit():
    assert btname.errors(btname.read_rows()) == []


def test_width_counts_gaps():
    f = btname.font()
    assert btname.width("I", f) == f["I"][0]
    assert btname.width("AB", f) == f["A"][0] + f["B"][0] + 1


@need_disc
def test_jp_column_matches_exe():
    exe = (btname.TREE / "PSX.EXE").read_bytes()
    rows = btname.read_rows()
    assert [(r["id"], r["jp"]) for r in rows] == btname.jp_names(exe)
    assert dict(btname.jp_names(exe))["E042"] == "さんぞく"


@need_disc
def test_assembled_records():
    import insert
    exe = (btname.TREE / "PSX.EXE").read_bytes()
    out = insert.assemble(exe)
    rows = {r["id"]: r["en"].upper().encode() for r in btname.read_rows()}
    names = 0x80153BE0 - btname.EXE_VA
    assert out[names + 42 * 16:names + 43 * 16].rstrip(b"\0") == rows["E042"]
    assert out[names + 200 * 16:names + 201 * 16].rstrip(b"\0") == rows["E200"]
    table = slice(0x80154CF4 - btname.EXE_VA, 0x80154CF4 - btname.EXE_VA + 4 * 192)
    assert out[table] == exe[table]  # the HUD still reads the code table (codes 0x00-0x24)
