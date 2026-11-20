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
        img, new = gfx.redraw(exe, gdata, e)
        pix, w, h = img.pix, img.w, img.h
        assert len(block) <= size and img.decode(block) == img.raw(new)
        inside = set()
        for r in gfx.rows(e):
            x, y, rw, rh = (int(r[k]) for k in "xywh")
            assert x + rw <= w and y + rh <= h
            inside |= {yy * w + xx for yy in range(y, y + rh) for xx in range(x, x + rw)}
        assert [i for i in range(len(pix)) if pix[i] != new[i] and i not in inside] == []
    assert gfx.gdata_edit(gdata, exe) != gdata


@need_disc
def test_ink_erase_leaves_no_japanese():
    """bg `ink` rows: after redraw, every ink-coloured pixel in a rect belongs to the English letters"""
    exe = (gfx.TREE / "PSX.EXE").read_bytes()
    gdata = (gfx.TREE / "GDATA.BIN").read_bytes()
    for e in gfx.entries():
        img = gfx.Image(exe, gdata, e)
        rs = [r for r in gfx.rows(e) if r["bg"] == "ink"]
        if not rs:
            continue
        cleared = list(img.pix)
        for r in rs:
            gfx.clear(img.w, cleared, r)
        for r in rs:
            x, y, rw, rh = (int(r[k]) for k in "xywh")
            left = [(xx, yy) for yy in range(y, y + rh) for xx in range(x, x + rw)
                    if cleared[yy * img.w + xx] == int(r["ink"])]
            assert left == [], (e, r["jp"], left[:5])


def test_label_font_has_every_letter():
    import labelfont
    for e in gfx.entries():
        for r in gfx.rows(e):
            if r["font"] == "label":
                assert labelfont.columns(r["en"])
