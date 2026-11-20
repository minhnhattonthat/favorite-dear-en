"""gfx.py: graphics text (docs/re/graphics.md) -> redrawn GDATA.BIN images.

    python -X utf8 tools/gfx.py png [ENTRY..] [--out work/gfx/en]   original | English side by side, 3x, per entry
    python -X utf8 tools/gfx.py check                                every row fits its rect, every image its slot

Rows live in gfx/<entry>.tsv (entry = GDATA directory index at PSX.EXE 0x4C50, e.g. e009), one label per row:
`x y w h ink shadow jp en`. The rect is cleared to index 0 and `en` drawn in it, left-aligned and vertically centred,
with the en6x12 font set proportionally (blank columns trimmed, 1 px between letters, 3 px space), `ink` index for
the letters and `shadow` index one pixel down-right (`-` = none). Images are the game's LZSS raw images (12-byte
header `u32 ?, u32 0, u16 width in halfwords, u16 height`, 4bpp when width = 64 halfwords); the recompressed block
goes back into the entry's own slot (insert.edits), so it must fit the slot's sector-rounded size."""
import argparse
import csv
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import lzss  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "work" / "disc" / "tree"
GFX = ROOT / "gfx"
TABLE, SECTOR = 0x4C50, 2048
FIELDS = ["x", "y", "w", "h", "ink", "shadow", "jp", "en"]


def slot(exe, entry):
    """(byte offset in GDATA.BIN, slot size) of directory entry `entry`"""
    sec, size = struct.unpack_from("<II", exe, TABLE + 8 * entry)
    return sec * SECTOR, size


def load(exe, gdata, entry):
    """(header bytes, width px, height, [pixel indexes]) of a 4bpp LZSS raw image"""
    off, size = slot(exe, entry)
    raw, _ = lzss.decompress(gdata[:off + size + 16], off)
    wh, h = struct.unpack_from("<HH", raw, 8)
    if wh != 64:
        raise ValueError(f"e{entry:03d}: {wh} halfwords wide, only 4bpp (64) is handled")
    w = wh * 4
    pix = []
    for b in raw[12:12 + w * h // 2]:
        pix += [b & 15, b >> 4]
    return raw[:12], w, h, pix


def pack(header, pix):
    return header + bytes(pix[i] | pix[i + 1] << 4 for i in range(0, len(pix), 2))


def rows(entry):
    path = GFX / f"e{entry:03d}.tsv"
    with open(path, encoding="utf-8", newline="") as f:
        out = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    for n, r in enumerate(out, 2):
        if list(r) != FIELDS or None in r.values():
            raise ValueError(f"{path}:{n}: columns must be {FIELDS}")
    return out


def entries():
    return sorted(int(p.stem[1:]) for p in GFX.glob("e[0-9][0-9][0-9].tsv"))


def letter(cell):
    """a glyph's columns (bit masks per row) with blank columns trimmed; space = 3 blank columns"""
    cols = [sum(1 << y for y in range(12) if cell[y] >> x & 1) for x in range(font_en.WIDTH)]
    while cols and not cols[0]:
        cols.pop(0)
    while cols and not cols[-1]:
        cols.pop()
    return cols or [0, 0]


def text_columns(text):
    g = font_en.glyphs()
    cols = []
    for i, ch in enumerate(text):
        if i:
            cols.append(0)
        cols += letter(g[ord(ch)])
    return cols


def draw(w, pix, r):
    """clear rect r and draw its English; returns the set of touched pixel positions"""
    x, y, rw, rh = (int(r[k]) for k in "xywh")
    ink = int(r["ink"])
    shadow = None if r["shadow"] == "-" else int(r["shadow"])
    cols = text_columns(r["en"])
    if len(cols) + (shadow is not None) > rw:
        raise ValueError(f"{r['en']!r}: {len(cols)} px wide in a {rw} px rect")
    top = font_en.TOP
    used = [yy for yy in range(12) if any(c >> yy & 1 for c in cols)]
    height = used[-1] - top + 1 + (shadow is not None)
    if height > rh:
        raise ValueError(f"{r['en']!r}: {height} px high in a {rh} px rect")
    y0 = y + (rh - (7 + (shadow is not None))) // 2 - top  # centre the cap height (rows 3-9)
    for yy in range(y, y + rh):
        for xx in range(x, x + rw):
            pix[yy * w + xx] = 0
    for layer, ind, d in ((shadow, shadow, 1), (ink, ink, 0)):
        if layer is None:
            continue
        for cx, c in enumerate(cols):
            for cy in range(12):
                if c >> cy & 1:
                    pix[(y0 + cy + d) * w + x + cx + d] = ind


def redraw(exe, gdata, entry):
    """(original pixels, new pixels, header, width, height)"""
    header, w, h, pix = load(exe, gdata, entry)
    new = list(pix)
    for r in rows(entry):
        draw(w, new, r)
    return pix, new, header, w, h


def images(exe=None, gdata=None):
    """{entry: (offset, slot size, new LZSS block)} for every gfx/eNNN.tsv"""
    exe = exe or (TREE / "PSX.EXE").read_bytes()
    gdata = gdata or (TREE / "GDATA.BIN").read_bytes()
    out = {}
    for e in entries():
        _, new, header, w, h = redraw(exe, gdata, e)
        block = lzss.compress(pack(header, new))
        off, size = slot(exe, e)
        if len(block) > size:
            raise ValueError(f"e{e:03d}: {len(block):#x} bytes compressed > its {size:#x}-byte slot")
        out[e] = (off, size, block)
    return out


def gdata_edit(gdata, exe):
    out = bytearray(gdata)
    for off, size, block in images(exe, gdata).values():
        out[off:off + size] = block + bytes(size - len(block))
    return bytes(out)


def png(out_dir, which):
    from PIL import Image
    exe = (TREE / "PSX.EXE").read_bytes()
    gdata = (TREE / "GDATA.BIN").read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    grey = [min(255, i * 17) for i in range(16)]
    for e in which or entries():
        pix, new, _, w, h = redraw(exe, gdata, e)
        im = Image.new("L", (w * 2 + 8, h), 40)
        for k, p in enumerate((pix, new)):
            part = Image.new("L", (w, h))
            part.putdata([grey[i] for i in p])
            im.paste(part, (k * (w + 8), 0))
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        im.save(out_dir / f"e{e:03d}.png")
        print(out_dir / f"e{e:03d}.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["png", "check"])
    ap.add_argument("entry", nargs="*", type=lambda s: int(s.lstrip("e")))
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "gfx" / "en")
    a = ap.parse_args()
    if a.cmd == "png":
        png(a.out, a.entry)
    else:
        for e, (off, size, block) in images().items():
            print(f"e{e:03d}: {len(block):#x}/{size:#x} bytes, {len(rows(e))} labels")
