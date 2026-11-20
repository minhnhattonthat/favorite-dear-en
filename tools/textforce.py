"""textforce.py: text coverage by forcing every message of each event file through the game's printer.

A mash sweep (`cover_sweep.py`) plays one branch per event and shows ~10 rows of each file. This driver runs
`warp.py --event NAME` with tools/lua/textforce.lua, which moves the printer's index to the next row still to show
each time the scene starts a message, so the scene's own print ops play the whole file. Resumable, in passes.

    python -X utf8 tools/textforce.py freeze [--build work/qa/force_build]
        copies build/favorite_dear_en.bin/.cue there and writes, for that text: strings.tsv (as textcover_map.py
        strings), rows.json ({sector: [[start byte, row id or null]..], ends: {sector: file size}}) and names.json
        ({sector: [event names that load it]}). Freeze before a sweep; rebuilds don't disturb it.
    python -X utf8 tools/textforce.py run [--build ..] [--root work/qa/force] [-j 1] [--frames 40000] [--only S,..]
        one pass: every sector with a text row no log under --root shows yet gets a run into <root>/p<N>/ev_<NAME>
        (N = the first pass number with no directory yet, or --pass N to resume one after a crash; pass N uses that
        sector's N-th event name, wrapping). Each run's log is converted (TEXT lines) as soon as it ends. Choice
        menus (｛..｝ rows) are drawn by the choice op, not the printer: the chain leaves them out. Battle files
        (the 0x80174A84 table: T0101 ..) run as `warp.py --battle NAME` into <root>/p<N>/bt_<NAME>.
    python -X utf8 tools/textforce.py left [--build ..] [--root ..]
        rows still unshown per sector.
Then: python -X utf8 $SKILL/scripts/textcover.py <root> <build>/strings.tsv --waive docs/text_unshown_unloaded.tsv
"""
import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import events  # noqa: E402
import extract  # noqa: E402
import textcover_map  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEXT = re.compile(r"^TEXT ([0-9A-Fa-f]+)", re.M)


def load(build):
    rows = json.loads((build / "rows.json").read_text(encoding="utf-8"))
    names = json.loads((build / "names.json").read_text(encoding="utf-8"))
    choice = set(rows["choice"])
    offs = {int(s): [(o, r) for o, r in v] for s, v in rows["rows"].items()}
    ends = {int(s): v for s, v in rows["ends"].items()}
    return offs, ends, {int(s): v for s, v in names.items()}, choice


BATTLE_TABLE = 0x80174A84  # {u16 key, u16 event id} .., key 0xFFFF ends it (docs/re/debug.md, T-events are battles)


def battles(exe):
    """{event name: event id} for the battle events (T0101 ..), as warp.lua resolves them (first id with the name).
    Their files load under that id, not warp's slot 32, and `--event` can't start them: run them with `--battle`."""
    names = events.event_names(exe)
    o, out = BATTLE_TABLE - 0x80010000 + 0x800, {}
    while True:
        key, eid = struct.unpack_from("<HH", exe, o)
        if key == 0xFFFF:
            return out
        if eid < len(names):
            out[names[eid]] = names.index(names[eid])
        o += 4


def run_dir(out, nm, battle):
    return out / (("bt_" + nm) if battle else ("ev_" + nm.replace(":", "_")))


def shown(root):
    out = set()
    for log in root.rglob("log.txt"):
        out.update(int(a, 16) for a in TEXT.findall(log.read_text(encoding="utf-8", errors="replace")))
    return out


def wanted(offs, names, seen, skip=()):
    """{sector: [row ids unshown]} for sectors some event name loads, leaving out the ids in `skip`."""
    out = {}
    for sec, v in offs.items():
        if sec not in names:
            continue
        miss = [rid for o, rid in v if rid and rid not in skip and (sec << 16 | o) not in seen]
        if miss:
            out[sec] = miss
    return out


def cmd_freeze(a):
    build = Path(a.build)
    build.mkdir(parents=True, exist_ok=True)
    for ext in (".bin", ".cue"):
        shutil.copy2(ROOT / "build" / ("favorite_dear_en" + ext), build / ("favorite_dear_en" + ext))
    exe, offs, ends = textcover_map.row_table()
    names = {}
    bare = textcover_map.name_sectors(exe)
    for name in events.event_names(exe):
        sec = bare.get(name.upper())
        if sec is not None and name not in names.setdefault(sec, []):
            names[sec].append(name)
    choice = []  # choice menus (｛..｝ items): drawn by the choice op, not the printer; the chain skips them
    for p in sorted((ROOT / "script/events").glob("*.tsv")):
        choice += [r["id"] for r in extract.read_tsv(p) if r["en"] and "｛" in r["jp"]]
    (build / "rows.json").write_text(json.dumps({"rows": {s: v for s, v in offs.items()}, "ends": ends,
                                                 "choice": choice}), encoding="utf-8")
    (build / "names.json").write_text(json.dumps(names), encoding="utf-8")
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/textcover_map.py"), "strings",
                    "--out", str(build / "strings.tsv")], check=True, cwd=ROOT)
    print(f"frozen into {build}: {len(offs)} files, {len(names)} loaded by an event name")


def cmd_run(a):
    build, root = Path(a.build).resolve(), Path(a.root).resolve()
    offs, ends, names, choice = load(build)
    exe = (ROOT / "work/disc/tree/PSX.EXE").read_bytes()
    want = wanted(offs, names, shown(root), choice)
    if a.only:
        keep = {int(x, 16) for x in a.only.split(",")}
        want = {s: v for s, v in want.items() if s in keep}
    n = a.pass_no or 1
    while not a.pass_no and (root / f"p{n}").exists():
        n += 1
    out = root / f"p{n}"
    out.mkdir(parents=True, exist_ok=True)

    bt = battles(exe)

    def finished(nm):
        p = run_dir(out, nm, nm in bt) / "emu.txt"
        return p.exists() and any(x.startswith("exit") for x in p.read_text(errors="replace").splitlines())

    want = {s: v for s, v in want.items() if not finished(names[s][(n - 1) % len(names[s])])}
    cue = str(build / "favorite_dear_en.cue").replace("\\", "/")
    print(f"pass {n}: {len(want)} files, {sum(map(len, want.values()))} rows unshown", flush=True)

    def run(sec):
        nm = names[sec][(n - 1) % len(names[sec])]
        miss = set(want[sec])
        v = offs[sec]
        cells = []
        for k, (o, rid) in enumerate(v):
            e = v[k + 1][0] if k + 1 < len(v) else ends[sec]
            cells.append(f"{o // 2},{e // 2},{1 if rid in miss else 0}")
        battle = nm in bt
        # a battle's file loads under its own id (textforce.lua FORCE_ID), after the host event starts the fight
        how = ["--battle", nm, "--var", f"FORCE_ID={bt[nm]}"] if battle else ["--event", nm]
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "tools/debug/warp.py"), *how, "--cue", cue,
               "--root", str(out), "--frames", str(min(a.frames + 400 * len(miss), 200000)),
               "--shot-every", str(a.shot_every), "--timeout", "3600", "--var", f"MASH_EVERY={a.mash}",
               "--lua", str(ROOT / "tools/lua/textforce.lua"),
               "--var", f"TARGETS='{' '.join(cells)}'"]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        d = run_dir(out, nm, battle)
        textcover_map.convert([d], exe, offs)
        log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
        print(f"{sec:04X}\t{nm}\trc {r.returncode}\tforced {log.count('FORCE ') - log.count('FORCE rows')}"
              f"\tshown {log.count('SHOWN ')}/{len(miss)}\tskip {log.count('SKIP ')}\tdone {'FORCE done' in log}",
              flush=True)

    with ThreadPoolExecutor(a.j) as ex:
        list(ex.map(run, sorted(want)))
    left = wanted(offs, names, shown(root), choice)
    print(f"pass {n} finished: {sum(map(len, left.values()))} rows unshown in {len(left)} files (choice menus not "
          f"counted)", flush=True)


def cmd_left(a):
    offs, _, names, choice = load(Path(a.build))
    seen = shown(Path(a.root))
    left = wanted(offs, names, seen)
    total = sum(len([1 for _, r in v if r]) for s, v in offs.items() if s in names)
    for sec in sorted(left):
        print(f"{sec:04X}\t{len(left[sec])}\t{','.join(names[sec][:4])}")
    nch = sum(1 for v in left.values() for r in v if r in choice)
    print(f"{sum(map(len, left.values()))} of {total} loaded rows unshown in {len(left)} files ({nch} choice menus)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("freeze", "run", "left"):
        s = sub.add_parser(name)
        s.add_argument("--build", default=str(ROOT / "work/qa/force_build"))
        s.add_argument("--root", default=str(ROOT / "work/qa/force"))
        if name == "run":
            s.add_argument("-j", type=int, default=1)
            s.add_argument("--frames", type=int, default=16000, help="base frames; +400 per unshown row (cap 200000)")
            s.add_argument("--mash", type=int, default=20, help="frames between circle presses (warp.lua MASH_EVERY)")
            s.add_argument("--only", help="comma-separated hex sectors")
            s.add_argument("--shot-every", type=int, default=1500, help="frames between shots (30 to catch a page)")
            s.add_argument("--pass", dest="pass_no", type=int, help="resume pass N (default: start the next one)")
    a = ap.parse_args()
    {"freeze": cmd_freeze, "run": cmd_run, "left": cmd_left}[a.cmd](a)


if __name__ == "__main__":
    main()
