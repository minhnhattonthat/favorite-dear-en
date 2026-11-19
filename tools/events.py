"""events.py: the event script files in GDATA.BIN (hero visits, scouting, story events) and a text estimate.

    python -X utf8 tools/events.py list   [--disc work/disc/tree]       one line per file: table, index, sector, size, text
    python -X utf8 tools/events.py text N [--disc work/disc/tree]       decoded text runs of file N (global index)
    python -X utf8 tools/events.py names                                event id -> script name (what warp.py takes)

Recon-grade (phase 1): files are found through three (u32 sector, u32 byte size) tables in PSX.EXE whose entries
start with the u16 magic 6; text = runs of >= 3 non-zero font codes (< 0x66C) holding >= 2 kana, between 0xFFxx
opcodes. Opcode argument counts are not decoded yet (an argument that happens to look like a code pair would be
counted as text), so the totals are an estimate; the extractor (phase 4) must walk the VM grammar instead.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TABLES = [(0x5988, 229), (0x60B8, 71), (0x62F8, 171)]  # PSX.EXE offset, entries (docs/re/events.md)
NCODES = 0x66C
LOAD_VA = 0x8016C608  # where the game loads a script file (verified: hero line at file 0xD94 = RAM 0x8016D39C)


def files(exe, gdata):
    out = []
    for tab, n in TABLES:
        for i in range(n):
            sec, size = struct.unpack_from("<II", exe, tab + 8 * i)
            data = gdata[sec * 2048:sec * 2048 + size]
            if size and len(data) >= 6 and struct.unpack_from("<H", data)[0] == 6:
                out.append((tab, i, sec, size, data))
    return out


def text_runs(data):
    """[(byte offset, [codes])] of plausible text runs."""
    n = len(data) // 2
    hw = struct.unpack_from("<%dH" % n, data)
    runs, cur, start = [], [], 0
    for i, v in enumerate(hw + (0xFFFF,)):
        if 0 < v < NCODES and i < n:  # 0x0000 (full-width space) is rare in text and fills variable areas
            if not cur:
                start = i
            cur.append(v)
            continue
        if len(cur) >= 3 and sum(0x23 <= c <= 0xBD for c in cur) >= 2:
            runs.append((start * 2, cur))
        cur = []
    return runs


NAMES_VA = 0x80173640  # event-name table: 9-byte ASCII names, index = event id (docs/re/debug.md)


def event_names(exe):
    """[name] indexed by event id, from the PSX.EXE event-name table (462 ids; some names repeat)."""
    o = NAMES_VA - 0x80010000 + 0x800
    out = []
    while True:
        name = exe[o + 9 * len(out):o + 9 * len(out) + 9].split(b"\0")[0]
        if not name or any(c < 0x20 or c > 0x7E for c in name):
            return out
        out.append(name.decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "text", "names"])
    ap.add_argument("n", nargs="?", type=int)
    ap.add_argument("--disc", default=str(ROOT / "work/disc/tree"))
    a = ap.parse_args()
    exe = (Path(a.disc) / "PSX.EXE").read_bytes()
    if a.cmd == "names":
        for i, name in enumerate(event_names(exe)):
            print(f"{i}\t{name}")
        return
    gdata = (Path(a.disc) / "GDATA.BIN").read_bytes()
    fs = files(exe, gdata)
    if a.cmd == "list":
        tot = 0
        for k, (tab, i, sec, size, data) in enumerate(fs):
            chars = sum(len(c) for _, c in text_runs(data))
            tot += chars
            print(f"{k}\t{tab:#x}\t{i}\t{sec:#x}\t{size:#x}\t{chars}")
        print(f"# {len(fs)} files, ~{tot} text characters")
    else:
        t = Table.load(ROOT / "tbl/jp.tbl")
        data = fs[a.n][4]
        for off, codes in text_runs(data):
            b = struct.pack("<%dH" % len(codes), *codes)
            print(f"{off:05X}\t{t.decode(b, 0, len(b))[0]}")


if __name__ == "__main__":
    main()
