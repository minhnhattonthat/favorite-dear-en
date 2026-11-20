"""Text coverage for the event scripts (phase 8 gate, `$SKILL/scripts/textcover.py`).

    python -X utf8 tools/textcover_map.py strings [--out build/strings.tsv]
        one `row id<TAB>hex key` per text row of the event scripts in the English build; key = original sector << 16 |
        byte offset of the row in the built file. Rows of files that no event id loads come last.
    python -X utf8 tools/textcover_map.py convert LOGDIR [LOGDIR..]
        reads each run's log.txt (written by tools/lua/textlog.lua), maps every printer index to the row that holds it
        and appends `TEXT <hex key>` lines (the row's start key) to the same log.txt, once per key.

How the map works: the loaded-script table at 0x8016C5B8 lists (event id, halfword offset into the buffer 0x8016C608)
per slot (docs/re/debug.md §Loading); a printer index (halfword index into that buffer) belongs to the slot with the
greatest offset <= index; the event id names the file through the name table (events.event_names) and the GDATA
name directory (pointer table 0x80013648, 0x39D entries, index = the combined GDATA table at 0x80014450 / file 0x4C50).
"""
import argparse
import bisect
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import en  # noqa: E402
import events  # noqa: E402
import evscript  # noqa: E402
import extract  # noqa: E402
import insert  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NAMEPTRS_VA, NNAMES = 0x80013648, 0x39D
TABLE_VA = 0x80014450


def va2off(va):
    return va - 0x80010000 + 0x800


def cstr(exe, va):
    o = va2off(va)
    return exe[o:exe.index(b"\0", o)].decode("ascii", "replace")


def id_sectors(exe):
    """{event id: original GDATA sector} for every event id whose name resolves to a directory entry."""
    names = [cstr(exe, struct.unpack_from("<I", exe, va2off(NAMEPTRS_VA) + 4 * i)[0]) for i in range(NNAMES)]
    bare = {}
    for i, n in enumerate(names):
        bare.setdefault(n.split(".")[0].split(";")[0].upper(), i)
    out = {}
    for eid, name in enumerate(events.event_names(exe)):
        i = bare.get(name.upper())
        if i is not None:
            out[eid] = struct.unpack_from("<I", exe, va2off(TABLE_VA) + 8 * i)[0]
    return out


def row_offsets():
    """{original sector: [(new byte offset, row id)]} for the English build, sorted by offset."""
    tree = ROOT / "work/disc/tree"
    exe, gdata = (tree / "PSX.EXE").read_bytes(), (tree / "GDATA.BIN").read_bytes()
    table = extract.event_table()
    out = {}
    for sec, size, data, where in evscript.script_files(exe, gdata):
        path = extract.SCRIPT / "events" / f"{sec:04X}.tsv"
        if not path.exists():
            continue
        sc = evscript.Script(data)
        rows = extract.read_tsv(path)
        repl = {}
        for row in rows:
            text = insert.row_text(row, "en")
            if text is not None:
                repl[(int(row["id"].split(".")[1], 16) - sc.code_off) // 2] = en.encode(text, table)
        _, newpos = insert.rebuild_map(sc, repl)
        lst = []
        for row in rows:
            pc = (int(row["id"].split(".")[1], 16) - sc.code_off) // 2
            lst.append((sc.code_off + 2 * newpos(pc), row["id"] if row["en"] else None))  # None: not text
        out[sec] = sorted(lst)
    return exe, out


def cmd_strings(a):
    exe, offs = row_offsets()
    loaded = set(id_sectors(exe).values())
    lines, orphan = [], []
    for sec, v in sorted(offs.items()):
        for off, rid in v:
            if rid:
                (lines if sec in loaded else orphan).append(f"{rid}\t{sec << 16 | off:X}")
    Path(a.out).write_text("".join(x + "\n" for x in lines + orphan), encoding="utf-8")
    print(f"{len(lines) + len(orphan)} rows -> {a.out}; {len(orphan)} in files no event id loads")


def cmd_convert(a):
    exe, offs = row_offsets()
    ids = id_sectors(exe)
    starts = {sec: [o for o, _ in v] for sec, v in offs.items()}
    for d in a.logdirs:
        log = Path(d) / "log.txt"
        if not log.exists():
            continue
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
        lines = [x for x in lines if not x.startswith("TEXT ")]
        slots, keys = {}, []
        for x in lines:
            m = re.search(r"SCR (\d+) (\d+) (\d+)", x)
            if m:
                slots[int(m[1])] = (int(m[2]), int(m[3]))
                continue
            m = re.search(r"PIDX (\d+)", x)
            if not m:
                continue
            idx = int(m[1])
            best = None
            for eid, hoff in slots.values():
                if hoff <= idx and eid in ids and (best is None or hoff > best[1]):
                    best = (eid, hoff)
            if best is None:
                continue
            eid, hoff = best
            sec = ids[eid]
            st = starts.get(sec)
            if not st:
                continue
            boff = 2 * (idx - hoff)
            k = bisect.bisect_right(st, boff) - 1
            if k < 0:
                continue
            key = sec << 16 | st[k]
            if key not in keys:
                keys.append(key)
        log.write_text("\n".join(lines + [f"TEXT {k:X}" for k in keys]) + "\n", encoding="utf-8")
        print(f"{d}: {len(keys)} rows")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("strings")
    s.add_argument("--out", default=str(ROOT / "build/strings.tsv"))
    c = sub.add_parser("convert")
    c.add_argument("logdirs", nargs="+")
    a = ap.parse_args()
    {"strings": cmd_strings, "convert": cmd_convert}[a.cmd](a)


if __name__ == "__main__":
    main()
