"""LZSS codec and font location against the unpacked disc (work/disc/tree; skipped when absent)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import lzss  # noqa: E402

TREE = ROOT / "work" / "disc" / "tree"
need_tree = pytest.mark.skipif(not (TREE / "PSX.EXE").is_file(), reason="disc not unpacked to work/disc/tree")


def test_lzss_roundtrip_synthetic():
    raw = bytes(range(256)) * 20 + b"\0" * 5000 + b"abcabcabc" * 300
    assert lzss.decompress(lzss.compress(raw))[0] == raw


@need_tree
@pytest.mark.parametrize("name", ["TITLE.PSS", "NOWLOAD.PSS", "TITLE/TTL_OPT.PSS", "NECLOGO1.PSS"])
def test_lzss_pss(name):
    data = (TREE / name).read_bytes()
    raw, end = lzss.decompress(data)
    assert end == len(data)
    assert lzss.decompress(lzss.compress(raw))[0] == raw


@need_tree
def test_font_known_glyphs():
    exe = (TREE / "PSX.EXE").read_bytes()
    ha = ["".join("#" if v else "." for v in r) for r in font.glyph(exe, 0x50)]  # は
    assert ha[1] == "#......#...."
    assert ha[2] == "#.########.."
    a = ["".join("#" if v else "." for v in r) for r in font.glyph(exe, 0x24)]  # あ
    assert a[2] == "##########.."
