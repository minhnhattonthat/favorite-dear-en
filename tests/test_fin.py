"""FIN.EXE (credits) pair glyphs: the encoder matches asm/fin.asm's decode, the hook writes only its own ranges, and
no Japanese line left in the credits uses the glyphs the hook overwrites (SJIS 0x8440-0x84BE)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import font_en  # noqa: E402
import insert  # noqa: E402

FIN = insert.TREE / "DATA" / "FIN.EXE"
need_fin = pytest.mark.skipif(not FIN.is_file() or not insert.ARMIPS.is_file(), reason="no unpacked disc or armips")
FREE, FREE_END, HOOK = 0x80025AF8, 0x80026364, 0x80013BD0


def decode(lead, trail):
    """asm/fin.asm's arithmetic"""
    n = (lead - 0xE0) * 189 + (trail - 0x40)
    return font_en.FIN_CHARSET[n // 74] + font_en.FIN_CHARSET[n % 74]


def test_pairs_roundtrip():
    assert len(font_en.FIN_CHARSET) == 74 == len(set(font_en.FIN_CHARSET))
    every = "".join(a + b for a in font_en.FIN_CHARSET for b in font_en.FIN_CHARSET)
    data = font_en.fin_pairs(every)
    assert all(0xE0 <= data[i] <= 0xFC and 0x40 <= data[i + 1] <= 0xFC for i in range(0, len(data), 2))
    assert "".join(decode(data[i], data[i + 1]) for i in range(0, len(data), 2)) == every
    assert font_en.fin_pairs("abc") == font_en.fin_pairs("abc ")


def test_staff_en_bytes():
    raw = insert.staff_en("&  Hi")
    assert raw[:1] == b"&" and extract.STAFF_NL not in raw and 0xFF not in raw
    assert bytes(b - 1 for b in raw[1:]) == font_en.fin_pairs("  Hi")


def test_staff_split_lines():
    """'|' makes one line per part (the painter rows); no English row may start with '%', which stops the roll"""
    a, b = insert.staff_en("Ab Cd|Ef").split(extract.STAFF_NL)
    assert bytes(x - 1 for x in a) == font_en.fin_pairs("Ab Cd") and bytes(x - 1 for x in b) == font_en.fin_pairs("Ef")
    rows = extract.read_tsv(extract.SCRIPT / "staff.tsv")
    assert not [r["id"] for r in rows if r["en"].startswith("%")]


def test_font_size():
    assert len(font_en.fin_binary()) == 11 * len(font_en.FIN_CHARSET)


def off(addr):
    return addr - 0x80010000 + 0x800


@need_fin
def test_hook_ranges():
    orig = FIN.read_bytes()
    assert struct.unpack_from("<I", orig, 0x18)[0] == 0x80010000
    new = insert.assemble(orig, "fin.asm")
    assert len(new) == len(orig)
    diff = [i for i in range(len(orig)) if orig[i] != new[i]]
    assert diff and all(off(HOOK) <= i < off(HOOK) + 8 or off(FREE) <= i < off(FREE_END) for i in diff)


def test_japanese_lines_avoid_overwritten_glyphs():
    for row in extract.read_tsv(extract.SCRIPT / "staff.tsv"):
        if row["en"]:
            continue
        for ch in row["jp"]:
            if ord(ch) >= 0x80:
                code = int.from_bytes(ch.encode("cp932"), "big")
                assert not 0x8440 <= code <= 0x84BE, (row["id"], ch)
