"""Graphics text (tools/gfx.py): every redrawn image decompresses to what was drawn, fits its slot and changes no
pixel outside its declared rects."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402
import lzss  # noqa: E402

need_disc = pytest.mark.skipif(not (gfx.TREE / "GDATA.BIN").is_file(), reason="no unpacked disc")


def test_rows_parse():
    for e in gfx.entries():
        for r in gfx.rows(e):
            assert r["en"] and r["jp"], (e, r)


@need_disc
def test_images_fit_and_stay_in_rects():
    exe = (gfx.TREE / "PSX.EXE").read_bytes()
    gdata = (gfx.TREE / "GDATA.BIN").read_bytes()
    for e, (off, size, block) in gfx.images(exe, gdata).items():
        pix, new, header, w, h = gfx.redraw(exe, gdata, e)
        assert len(block) <= size and lzss.decompress(block + bytes(16))[0] == gfx.pack(header, new)
        inside = set()
        for r in gfx.rows(e):
            x, y, rw, rh = (int(r[k]) for k in "xywh")
            assert x + rw <= w and y + rh <= h
            inside |= {yy * w + xx for yy in range(y, y + rh) for xx in range(x, x + rw)}
        assert [i for i in range(len(pix)) if pix[i] != new[i] and i not in inside] == []
    assert gfx.gdata_edit(gdata, exe) != gdata
