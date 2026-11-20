"""gfx.py: graphics text (docs/re/graphics.md) -> redrawn GDATA.BIN images.

    python -X utf8 tools/gfx.py png [ENTRY..] [--out work/gfx/en]   original | English side by side, 3x, per entry
    python -X utf8 tools/gfx.py check                                every row fits its rect, every image its slot

Rows live in gfx/<entry>.tsv (entry = GDATA directory index at PSX.EXE 0x4C50, e.g. e009, or sNNNNN = a TIM at that
GDATA sector outside the directory, e.g. the tutorial charts s40127: tools/timscan.py), one label per row:
`x y w h font ink shadow bg align jp en`.
- font `6x12`: the en6x12 font set proportionally (blank columns trimmed, 1 px between letters, 3 px space), the cap
  height centred in the rect; font `label`: fonts/label14.txt (tools/labelfont.py), a capital's top row at rect y
  (make h cover descenders); `label2` = the same with every column doubled (640-wide hi-res images); font `narrow`: fonts/narrow3x7.txt (3 px letters, only the ones a row needs), centred.
- ink: palette index of the letters (and, with bg `ink`, of the Japanese to erase); shadow: index drawn one pixel
  down-right, `oN` = a 1 px outline all round in index N (e203's lettering), `-` = none.
- bg: a palette index to fill the whole rect with, or `ink` = erase only the ink-coloured pixels in the rect, each
  taking the nearest other pixel of its row (for labels printed on a textured background), or `>=N` = the same for
  every pixel of index N or above (lettering in several light indices over a darker texture, e015's buttons), or
  `i:A,B,..` = the same for the listed indices (outlined lettering: fill and outline); `i:A,B@dx,dy` first gives
  each such pixel the one at (dx, dy) from it (a clean patch of the same texture, no row streaks); `lum:LO,HI,D`
  (TIMs) = every pixel whose palette colour is as dark as LO or as light as HI, grown by D px, refilled from the
  outside in with the mean of its neighbours (white lettering with a dark shadow over a painting); `lum:LO,HI,D,teal`
  also takes teal pixels (the charts' title lettering), and a trailing `@dx,dy` first copies the texture from that
  offset where it is clean (grass under a title); `-` = none.
  en `-` = erase only (a big Japanese label erased by one row, the English set by another).
- align: `l` left, `c` centred in the rect.
- font `copy` (other columns `-`, en = "sx,sy"): after every clear, copy the w x h block at sx,sy to x,y, in file
  order; e203 widens its small boxes this way (border first, then the erased inside).
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


def name(entry):
    """file stem of an entry: a directory index (int) -> 'e203', a sector image ('s40127') as is"""
    return f"e{entry:03d}" if isinstance(entry, int) else entry


def slot(exe, entry, gdata=None):
    """(byte offset in GDATA.BIN, slot size) of directory entry `entry` (int), or of a TIM outside the directory
    named by its sector ('s40127': tools/timscan.py; size = the TIM rounded up to whole sectors)"""
    if isinstance(entry, int):
        sec, size = struct.unpack_from("<II", exe, TABLE + 8 * entry)
        return sec * SECTOR, size
    off = int(entry[1:]) * SECTOR
    if gdata is None:
        gdata = (TREE / "GDATA.BIN").read_bytes()
    t = tim.parse(gdata[off:off + 0x80000])
    if t is None:
        raise ValueError(f"{entry}: no TIM at sector {entry[1:]}")
    return off, -(-t["end"] // SECTOR) * SECTOR


class Image:
    """one GDATA image: kind 'lzss4' or 'tim8', width, height, pixel indexes; encode(pix) -> slot bytes"""

    def __init__(self, exe, gdata, entry):
        off, size = slot(exe, entry, gdata)
        self.entry, self.size = entry, size
        blob = gdata[off:off + size]
        t = tim.parse(blob)
        if t is not None:
            if t["bpp"] == 16:
                raise ValueError(f"{name(entry)}: 16bpp TIM, only 4/8bpp are handled")
            self.kind, self.w, self.h, self.pix = f"tim{t['bpp']}", t["w"], t["h"], t["pix"]
            self.blob, self.at = blob, t["end"] - t["w"] * t["h"] * t["bpp"] // 8
            self.pal = [tim.rgb(c) for c in t["cluts"][0]] if t["cluts"] else None  # for bg `lum:` rows
            return
        self.pal = None
        raw, _ = lzss.decompress(gdata[:off + size + 16], off)
        wh, h = struct.unpack_from("<HH", raw, 8)
        if wh != 64:
            raise ValueError(f"{name(entry)}: {wh} halfwords wide, only 4bpp (64) is handled")
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
    path = GFX / f"{name(entry)}.tsv"
    with open(path, encoding="utf-8", newline="") as f:
        out = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    for n, r in enumerate(out, 2):
        if list(r) != FIELDS or None in r.values():
            raise ValueError(f"{path}:{n}: columns must be {FIELDS}")
        if r["font"] not in ("6x12", "label", "label2", "narrow", "copy") or r["align"] not in ("l", "c", "-"):
            raise ValueError(f"{path}:{n}: font must be 6x12|label|label2|narrow|copy, align l|c (- for copy)")
    return out


def entries():
    """directory entries (ints, gfx/eNNN.tsv) then sector images ('sNNNNN', gfx/sNNNNN.tsv)"""
    return (sorted(int(p.stem[1:]) for p in GFX.glob("e[0-9][0-9][0-9].tsv"))
            + sorted(p.stem for p in GFX.glob("s[0-9][0-9][0-9][0-9][0-9].tsv")))


def letter(cell):
    """a glyph's columns (bit masks per row) with blank columns trimmed; space = 3 blank columns"""
    cols = [sum(1 << y for y in range(12) if cell[y] >> x & 1) for x in range(font_en.WIDTH)]
    while cols and not cols[0]:
        cols.pop(0)
    while cols and not cols[-1]:
        cols.pop()
    return cols or [0, 0]


def text_columns(text, font="6x12"):
    if font == "label2":  # the label font with every column doubled: for 640-wide hi-res images
        return [c for c in text_columns(text, "label") for _ in (0, 1)]
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
    """every ink pixel in the rect takes the nearest non-ink pixel of its row (left first at equal distance);
    ink: one index, or a set of them"""
    inks = ink if isinstance(ink, (set, frozenset)) else {ink}
    for yy in range(y, y + rh):
        row = pix[yy * w:(yy + 1) * w]
        for xx in range(x, x + rw):
            if row[xx] not in inks:
                continue
            for d in range(1, w):
                for c in (xx - d, xx + d):
                    if 0 <= c < w and row[c] not in inks:
                        pix[yy * w + xx] = row[c]
                        break
                else:
                    continue
                break


def diffuse(w, pix, mask, pal):
    """fill the masked pixels from the outside in: each takes the palette colour nearest the mean of its clean
    8-neighbours (a smooth patch over photo backgrounds, no row streaks)"""
    mask = set(mask)
    near = {}

    def nearest(rgb):
        if rgb not in near:
            near[rgb] = min(range(len(pal)), key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i], rgb)))
        return near[rgb]

    h = len(pix) // w
    while mask:
        done = {}
        for xx, yy in mask:
            around = [pal[pix[(yy + dy) * w + xx + dx]] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                      if (dx or dy) and 0 <= xx + dx < w and 0 <= yy + dy < h and (xx + dx, yy + dy) not in mask]
            if len(around) >= 3 or (around and len(mask) < 50):
                done[(xx, yy)] = nearest(tuple(sum(c[k] for c in around) // len(around) for k in range(3)))
        if not done:  # no pixel has 3 clean neighbours: take any with one
            for xx, yy in mask:
                around = [pix[(yy + dy) * w + xx + dx] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                          if 0 <= xx + dx < w and 0 <= yy + dy < h and (xx + dx, yy + dy) not in mask]
                if around:
                    done[(xx, yy)] = around[0]
        if not done:
            raise ValueError("diffuse: masked pixels with no clean pixel anywhere")
        for (xx, yy), v in done.items():
            pix[yy * w + xx] = v
        mask -= set(done)


def clear(w, pix, r, pal=None):
    """fill rect r, or erase its ink (bg `ink`); pal: the image's palette as RGB, for bg `lum:`"""
    x, y, rw, rh = (int(r[k]) for k in "xywh")
    if r["bg"] == "-":  # draw only (an erase-only row cleared the Japanese)
        return
    if r["bg"].startswith("lum:"):  # lum:LO,HI,D[,teal]: pixels as dark as LO or as light as HI, grown by D px
        spec, _, off = r["bg"][4:].partition("@")
        lo, hi, grow, *teal = spec.split(",")
        lo, hi, grow = int(lo), int(hi), int(grow)
        hit = [not lo < sum(c) // 3 < hi or (teal and c[1] >= 120 and c[2] >= 120 and c[0] <= c[1] - 40) for c in pal]
        seed = {(xx, yy) for yy in range(y, y + rh) for xx in range(x, x + rw) if hit[pix[yy * w + xx]]}
        mask = {(xx + dx, yy + dy) for xx, yy in seed for dx in range(-grow, grow + 1) for dy in range(-grow, grow + 1)}
        mask = {(xx, yy) for xx, yy in mask if x <= xx < x + rw and y <= yy < y + rh}
        if off:  # texture fill from (dx, dy) away where that pixel is clean; the rest diffuses
            dx, dy = (int(v) for v in off.split(","))
            for xx, yy in sorted(mask):
                sx, sy = xx + dx, yy + dy
                if 0 <= sx < w and 0 <= sy < len(pix) // w and (sx, sy) not in mask and not hit[pix[sy * w + sx]]:
                    pix[yy * w + xx] = pix[sy * w + sx]
                    mask.discard((xx, yy))
        diffuse(w, pix, mask, pal)
        return
    if r["bg"] == "ink":
        erase(w, pix, x, y, rw, rh, int(r["ink"]))
    elif r["bg"].startswith(">="):
        erase(w, pix, x, y, rw, rh, set(range(int(r["bg"][2:]), 256)))
    elif r["bg"].startswith("i:"):
        spec, _, off = r["bg"][2:].partition("@")
        inks = {int(i) for i in spec.split(",")}
        if off:  # texture fill: each ink pixel takes the pixel at (dx, dy) from it when that one is clean
            dx, dy = (int(v) for v in off.split(","))
            for yy in range(max(y, -dy), min(y + rh, len(pix) // w - dy)):
                for xx in range(max(x, -dx), min(x + rw, w - dx)):
                    src = pix[(yy + dy) * w + xx + dx]
                    if pix[yy * w + xx] in inks and src not in inks:
                        pix[yy * w + xx] = src
        erase(w, pix, x, y, rw, rh, inks)
    else:
        for yy in range(y, y + rh):
            for xx in range(x, x + rw):
                pix[yy * w + xx] = int(r["bg"])


def draw(w, pix, r):
    """draw rect r's English (after every rect is cleared, so overlapping rects don't erase each other's letters)"""
    x, y, rw, rh = (int(r[k]) for k in "xywh")
    if r["en"] == "-":  # erase-only row (a big Japanese label, the English set by a smaller rect)
        return
    ink = int(r["ink"])
    outline = r["shadow"].startswith("o")
    shadow = None if r["shadow"] == "-" else int(r["shadow"].lstrip("o"))
    cols = text_columns(r["en"], r["font"])
    pad = 2 if outline else (shadow is not None)  # extra px the shadow or outline adds to each axis
    width = len(cols) + pad
    if width > rw:
        raise ValueError(f"{r['en']!r}: {width} px wide in a {rw} px rect")
    used = [yy for yy in range(16) if any(c >> yy & 1 for c in cols)]
    lead = 1 if outline else 0  # the outline's first row/column comes before the letters
    if r["font"] in ("label", "label2"):
        y0 = y - labelfont.CAP[0] + lead
    elif r["font"] == "narrow":
        y0 = y + (rh - (7 + pad)) // 2 + lead
    else:
        y0 = y + (rh - (7 + pad)) // 2 - font_en.TOP + lead  # centre the cap height (rows 3-9)
    if y0 + used[0] - lead < y or y0 + used[-1] + pad - lead >= y + rh:
        raise ValueError(f"{r['en']!r}: rows {y0 + used[0]}-{y0 + used[-1]} leave rect y {y}-{y + rh - 1}")
    x0 = x + ((rw - width) // 2 if r["align"] == "c" else 0) + lead
    dots = [(cx, cy) for cx, c in enumerate(cols) for cy in range(16) if c >> cy & 1]
    if outline:
        ring = {(cx + dx, cy + dy) for cx, cy in dots for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        layers = ((shadow, ring), (ink, dots))
    else:
        layers = ((shadow, [(cx + 1, cy + 1) for cx, cy in dots]), (ink, dots))
    for layer, pts in layers:
        if layer is None:
            continue
        for cx, cy in pts:
            pix[(y0 + cy) * w + x0 + cx] = layer


def redraw(exe, gdata, entry):
    """(Image, new pixels)"""
    img = Image(exe, gdata, entry)
    new = list(img.pix)
    labels = [r for r in rows(entry) if r["font"] != "copy"]
    for r in labels:
        clear(img.w, new, r, img.pal)
    for r in rows(entry):
        if r["font"] == "copy":
            copy(img.w, new, r)
    for r in labels:
        draw(img.w, new, r)
    return img, new


def copy(w, pix, r):
    """copy the w x h block at `en` = "sx,sy" to x,y (after the clears, in file order): widens a box by repeating
    its border and erased inside"""
    x, y, rw, rh = (int(r[k]) for k in "xywh")
    sx, sy = (int(v) for v in r["en"].split(","))
    block = [pix[(sy + yy) * w + sx:(sy + yy) * w + sx + rw] for yy in range(rh)]
    for yy, line in enumerate(block):
        pix[(y + yy) * w + x:(y + yy) * w + x + rw] = line


def images(exe=None, gdata=None):
    """{entry: (offset, slot size, new slot bytes)} for every gfx/eNNN.tsv and gfx/sNNNNN.tsv"""
    exe = exe or (TREE / "PSX.EXE").read_bytes()
    gdata = gdata or (TREE / "GDATA.BIN").read_bytes()
    out = {}
    for e in entries():
        img, new = redraw(exe, gdata, e)
        block = img.encode(new)
        off, size = slot(exe, e, gdata)
        if len(block) > size:
            raise ValueError(f"{name(e)}: {len(block):#x} bytes > its {size:#x}-byte slot")
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
        scale = 3 if img.w <= 256 else 2 if img.w <= 320 else 1
        im = im.resize((im.width * scale, im.height * scale), PImage.NEAREST)
        im.save(out_dir / f"{name(e)}.png")
        print(out_dir / f"{name(e)}.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["png", "check"])
    ap.add_argument("entry", nargs="*", type=lambda s: s if s.startswith("s") else int(s.lstrip("e")))
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "gfx" / "en")
    a = ap.parse_args()
    if a.cmd == "png":
        png(a.out, a.entry)
    else:
        for e, (off, size, block) in images().items():
            print(f"{name(e)}: {len(block):#x}/{size:#x} bytes, {len(rows(e))} labels")
