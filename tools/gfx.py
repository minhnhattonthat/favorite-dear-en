"""gfx.py: graphics text (docs/re/graphics.md) -> redrawn GDATA.BIN images.

    python -X utf8 tools/gfx.py png [ENTRY..] [--out work/gfx/en]   original | English side by side, 3x, per entry
    python -X utf8 tools/gfx.py check                                every row fits its rect, every image its slot

Rows live in gfx/<entry>.tsv (entry = GDATA directory index at PSX.EXE 0x4C50, e.g. e009), one label per row:
`x y w h font ink shadow bg align jp en`.
- font `6x12`: the en6x12 font set proportionally (blank columns trimmed, 1 px between letters, 3 px space), the cap
  height centred in the rect; font `label`: fonts/label14.txt (tools/labelfont.py), a capital's top row at rect y
  (make h cover descenders); font `narrow`: fonts/narrow3x7.txt (3 px letters, only the ones a row needs), centred.
- ink: palette index of the letters (and, with bg `ink`, of the Japanese to erase); shadow: index drawn one pixel
  down-right, `-` = none.
- bg: a palette index to fill the whole rect with, or `ink` = erase only the ink-coloured pixels in the rect, each
  taking the nearest other pixel of its row (for labels printed on a textured background).
- align: `l` left, `c` centred in the rect.
Images: the game's LZSS raw images (12-byte header `u32 ?, u32 0, u16 width in halfwords, u16 height`, 4bpp when
width = 64 halfwords; recompressed back into the entry's own slot, so it must fit the slot's sector-rounded size) and
raw 8bpp TIMs (pixels replaced in place, same size)."""
import argparse
import csv
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import labelfont  # noqa: E402
import lzss  # noqa: E402
import tim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "work" / "disc" / "tree"
GFX = ROOT / "gfx"
TABLE, SECTOR = 0x4C50, 2048
FIELDS = ["x", "y", "w", "h", "font", "ink", "shadow", "bg", "align", "jp", "en"]


def slot(exe, entry):
    """(byte offset in GDATA.BIN, slot size) of directory entry `entry`"""
    sec, size = struct.unpack_from("<II", exe, TABLE + 8 * entry)
    return sec * SECTOR, size


class Image:
    """one GDATA image: kind 'lzss4' or 'tim8', width, height, pixel indexes; encode(pix) -> slot bytes"""

    def __init__(self, exe, gdata, entry):
        off, size = slot(exe, entry)
        self.entry, self.size = entry, size
        blob = gdata[off:off + size]
        t = tim.parse(blob)
        if t is not None:
            if t["bpp"] == 16:
                raise ValueError(f"e{entry:03d}: 16bpp TIM, only 4/8bpp are handled")
            self.kind, self.w, self.h, self.pix = f"tim{t['bpp']}", t["w"], t["h"], t["pix"]
            self.blob, self.at = blob, t["end"] - t["w"] * t["h"] * t["bpp"] // 8
            return
        raw, _ = lzss.decompress(gdata[:off + size + 16], off)
        wh, h = struct.unpack_from("<HH", raw, 8)
        if wh != 64:
            raise ValueError(f"e{entry:03d}: {wh} halfwords wide, only 4bpp (64) is handled")
        self.kind, self.w, self.h, self.header = "lzss4", wh * 4, h, raw[:12]
        self.pix = [b >> s & 15 for b in raw[12:12 + wh * 4 * h // 2] for s in (0, 4)]

    def raw(self, pix):
        """the decoded image bytes for pix (LZSS: header + 4bpp; TIM: the whole file)"""
        packed = bytes(pix) if self.kind == "tim8" else bytes(pix[i] | pix[i + 1] << 4 for i in range(0, len(pix), 2))
        if self.kind.startswith("tim"):
            return self.blob[:self.at] + packed + self.blob[self.at + len(packed):]
        return self.header + packed

    def encode(self, pix):
        """slot bytes (not padded) for pix"""
        return self.raw(pix) if self.kind.startswith("tim") else lzss.compress(self.raw(pix))

    def decode(self, block):
        """raw image bytes from slot bytes, the inverse of encode for checks"""
        return block if self.kind.startswith("tim") else lzss.decompress(block + bytes(16))[0]


def rows(entry):
    path = GFX / f"e{entry:03d}.tsv"
    with open(path, encoding="utf-8", newline="") as f:
        out = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    for n, r in enumerate(out, 2):
        if list(r) != FIELDS or None in r.values():
            raise ValueError(f"{path}:{n}: columns must be {FIELDS}")
        if r["font"] not in ("6x12", "label", "narrow") or r["align"] not in ("l", "c"):
            raise ValueError(f"{path}:{n}: font must be 6x12|label|narrow, align l|c")
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


def text_columns(text, font="6x12"):
    if font in labelfont.FONTS:
        path, height, _ = labelfont.FONTS[font]
        return labelfont.columns(text, path, height)
    g = font_en.glyphs()
    cols = []
    for i, ch in enumerate(text):
        if i:
            cols.append(0)
        cols += letter(g[ord(ch)])
    return cols


def erase(w, pix, x, y, rw, rh, ink):
    """every ink pixel in the rect takes the nearest non-ink pixel of its row (left first at equal distance)"""
    for yy in range(y, y + rh):
        row = pix[yy * w:(yy + 1) * w]
        for xx in range(x, x + rw):
            if row[xx] != ink:
                continue
            for d in range(1, w):
                for c in (xx - d, xx + d):
                    if 0 <= c < w and row[c] != ink:
                        pix[yy * w + xx] = row[c]
                        break
                else:
                    continue
                break


def clear(w, pix, r):
    """fill rect r, or erase its ink (bg `ink`)"""
    x, y, rw, rh = (int(r[k]) for k in "xywh")
    if r["bg"] == "ink":
        erase(w, pix, x, y, rw, rh, int(r["ink"]))
    else:
        for yy in range(y, y + rh):
            for xx in range(x, x + rw):
                pix[yy * w + xx] = int(r["bg"])


def draw(w, pix, r):
    """draw rect r's English (after every rect is cleared, so overlapping rects don't erase each other's letters)"""
    x, y, rw, rh = (int(r[k]) for k in "xywh")
    ink = int(r["ink"])
    shadow = None if r["shadow"] == "-" else int(r["shadow"])
    cols = text_columns(r["en"], r["font"])
    width = len(cols) + (shadow is not None)
    if width > rw:
        raise ValueError(f"{r['en']!r}: {width} px wide in a {rw} px rect")
    used = [yy for yy in range(16) if any(c >> yy & 1 for c in cols)]
    if r["font"] == "label":
        y0 = y - labelfont.CAP[0]
    elif r["font"] == "narrow":
        y0 = y + (rh - (7 + (shadow is not None))) // 2
    else:
        y0 = y + (rh - (7 + (shadow is not None))) // 2 - font_en.TOP  # centre the cap height (rows 3-9)
    if y0 + used[0] < y or y0 + used[-1] + (shadow is not None) >= y + rh:
        raise ValueError(f"{r['en']!r}: rows {y0 + used[0]}-{y0 + used[-1]} leave rect y {y}-{y + rh - 1}")
    x0 = x + ((rw - width) // 2 if r["align"] == "c" else 0)
    for layer, d in ((shadow, 1), (ink, 0)):
        if layer is None:
            continue
        for cx, c in enumerate(cols):
            for cy in range(16):
                if c >> cy & 1:
                    pix[(y0 + cy + d) * w + x0 + cx + d] = layer


def redraw(exe, gdata, entry):
    """(Image, new pixels)"""
    img = Image(exe, gdata, entry)
    new = list(img.pix)
    for r in rows(entry):
        clear(img.w, new, r)
    for r in rows(entry):
        draw(img.w, new, r)
    return img, new


def images(exe=None, gdata=None):
    """{entry: (offset, slot size, new slot bytes)} for every gfx/eNNN.tsv"""
    exe = exe or (TREE / "PSX.EXE").read_bytes()
    gdata = gdata or (TREE / "GDATA.BIN").read_bytes()
    out = {}
    for e in entries():
        img, new = redraw(exe, gdata, e)
        block = img.encode(new)
        off, size = slot(exe, e)
        if len(block) > size:
            raise ValueError(f"e{e:03d}: {len(block):#x} bytes > its {size:#x}-byte slot")
        out[e] = (off, size, block)
    return out


def gdata_edit(gdata, exe):
    out = bytearray(gdata)
    for off, size, block in images(exe, gdata).values():
        out[off:off + size] = block + bytes(size - len(block))
    return bytes(out)


def png(out_dir, which):
    from PIL import Image as PImage
    exe = (TREE / "PSX.EXE").read_bytes()
    gdata = (TREE / "GDATA.BIN").read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    for e in which or entries():
        img, new = redraw(exe, gdata, e)
        if img.kind.startswith("tim"):
            t = tim.parse(img.blob)
            parts = [tim.to_image(dict(t, pix=p)) for p in (img.pix, new)]
        else:
            grey = [min(255, i * 17) for i in range(16)]
            parts = []
            for p in (img.pix, new):
                part = PImage.new("L", (img.w, img.h))
                part.putdata([grey[i] for i in p])
                parts.append(part.convert("RGB"))
        im = PImage.new("RGB", (img.w * 2 + 8, img.h), (40, 40, 40))
        for k, part in enumerate(parts):
            im.paste(part, (k * (img.w + 8), 0))
        scale = 3 if img.w <= 256 else 2
        im = im.resize((im.width * scale, im.height * scale), PImage.NEAREST)
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
