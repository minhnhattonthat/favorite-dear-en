"""font_en.py: the English half-cell font (fonts/en6x12.txt) -> the binaries the glyph hooks read (asm/font.asm,
asm/fin.asm via fin_binary/fin_pairs).

    python -X utf8 tools/font_en.py bin OUT.bin      12 bytes per glyph, codes FIRST..LAST, bit 0 = leftmost pixel
    python -X utf8 tools/font_en.py png OUT.png      preview sheet (16 per row, 3x zoom)

Each glyph is 5 px wide in a 6x12 half cell; the hook ORs the left glyph and the right glyph << 6 into one 12x12
cell of the game's 1bpp format (docs/re/text.md §Font, §English)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts" / "en6x12.txt"
FIRST, LAST = 0x20, 0x84
WIDTH, ROWS, TOP = 5, 12, 3


def glyphs(path=SRC):
    """{code: [12 row bytes]}"""
    out = {}
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        code, *rows = line.split()
        code = int(code, 16)
        if not FIRST <= code <= LAST or code in out:
            raise ValueError(f"{path}:{n}: bad or duplicate code {code:#x}")
        if len(rows) not in (0, 7, 9):
            raise ValueError(f"{path}:{n}: {len(rows)} rows (want 7 or 9)")
        cell = [0] * ROWS
        for y, r in enumerate(rows):
            if len(r) != WIDTH or set(r) - set(".#"):
                raise ValueError(f"{path}:{n}: row {r!r} is not {WIDTH} of . and #")
            cell[TOP + y] = sum(1 << x for x, ch in enumerate(r) if ch == "#")
        out[code] = cell
    return out


def binary(path=SRC):
    g = glyphs(path)
    return b"".join(bytes(g.get(c, [0] * ROWS)) for c in range(FIRST, LAST + 1))


def chars():
    """code -> character for every glyph the font has (ASCII + extras)."""
    extra = {0x80: "…", 0x81: "—", 0x82: "♥", 0x83: "♪", 0x84: "é"}
    return {c: extra.get(c, chr(c)) for c in glyphs()}


# FIN.EXE (credits) pair glyphs: asm/fin.asm decodes a code to two indexes into this string (74 x 74 pairs fit the
# 29 lead bytes 0xE0-0xFC x 189 trail bytes 0x40-0xFC); the glyphs are rows 1-11 of the 12-row cell (FIN's are 11).
FIN_CHARSET = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-'&()!?/:0123456789"
FIN_LEAD, FIN_TRAIL, FIN_TRAILS = 0xE0, 0x40, 189


def fin_binary(path=SRC):
    """11 bytes per FIN_CHARSET letter, bit 5 = leftmost pixel (the hook shifts them into a u16 row)"""
    g = glyphs(path)
    out = bytearray()
    for ch in FIN_CHARSET:
        for row in g[ord(ch)][1:]:
            out.append(sum(1 << (5 - x) for x in range(6) if row >> x & 1))
    return bytes(out)


def fin_pairs(text):
    """an ASCII line -> FIN.EXE pair codes (decoded bytes, before STAFF.TXT's +1); odd length gets a trailing space"""
    if len(text) % 2:
        text += " "
    out = bytearray()
    for a, b in zip(text[::2], text[1::2]):
        n = FIN_CHARSET.index(a) * len(FIN_CHARSET) + FIN_CHARSET.index(b)
        out += bytes([FIN_LEAD + n // FIN_TRAILS, FIN_TRAIL + n % FIN_TRAILS])
    return bytes(out)


def png(out):
    from PIL import Image
    g = glyphs()
    codes = list(range(FIRST, LAST + 1))
    w, h = 16 * 6, ((len(codes) + 15) // 16) * ROWS
    im = Image.new("L", (w, h), 255)
    for i, c in enumerate(codes):
        ox, oy = (i % 16) * 6, (i // 16) * ROWS
        for y, row in enumerate(g.get(c, [0] * ROWS)):
            for x in range(6):
                if row >> x & 1:
                    im.putpixel((ox + x, oy + y), 0)
    im.resize((w * 3, h * 3), Image.NEAREST).save(out)


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    if cmd == "bin":
        Path(out).write_bytes(binary())
    elif cmd == "png":
        png(out)
    else:
        sys.exit(__doc__)
