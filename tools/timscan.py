"""timscan.py: every TIM in GDATA.BIN found by a sector scan, including the ones outside the 423-entry directory
at PSX.EXE 0x4C50 (event pictures, the tutorial charts), as PNGs for the graphics-text survey (docs/re/graphics.md).

    python -X utf8 tools/timscan.py [--out work/gfx/scan] [--from 0]   list + one PNG per TIM (named by sector)
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "work" / "disc" / "tree"
TABLE, SECTOR, ENTRIES = 0x4C50, 2048, 423


def scan(gdata, start=0):
    """[(sector, parsed TIM)] for every sector that starts a 4/8/16bpp TIM"""
    out, s = [], start
    while s * SECTOR < len(gdata):
        if gdata[s * SECTOR:s * SECTOR + 4] == b"\x10\0\0\0":
            t = tim.parse(gdata[s * SECTOR:s * SECTOR + 0x80000])
            if t:
                out.append((s, t))
                s += max(1, -(-t["end"] // SECTOR))
                continue
        s += 1
    return out


def directory(exe):
    """{sector: entry} of the 423-entry GDATA directory"""
    return {struct.unpack_from("<I", exe, TABLE + 8 * e)[0]: e for e in range(ENTRIES)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "gfx" / "scan")
    ap.add_argument("--from", dest="start", type=int, default=0)
    a = ap.parse_args()
    gdata = (TREE / "GDATA.BIN").read_bytes()
    known = directory((TREE / "PSX.EXE").read_bytes())
    a.out.mkdir(parents=True, exist_ok=True)
    for s, t in scan(gdata, a.start):
        name = f"s{s:05d}" + (f"_e{known[s]:03d}" if s in known else "")
        tim.to_image(t).save(a.out / f"{name}.png")
        print(f"{name}\t{t['bpp']}bpp\t{t['w']}x{t['h']}\tvram {t['vram']}")
