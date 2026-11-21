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
        menus (｛..｝ rows) are printer rows too (tour ev_smen01 logs 3A76.13E0), but forcing into one is untried (a
        menu may need its op's state): the chain never redirects to them, it only lets the scene's own print draw them (flag 2). Battle files
        (the 0x80174A84 table: T0101 ..) run as `warp.py --battle NAME` into <root>/p<N>/bt_<NAME>.
        Best settings (pass 3, 2026-11-21): `--keypatch --var SKIPKEY=1 --var ADOPT=1`. ADOPT: the printer index
        moves a page at a time, so never re-point a row the printer entered by itself (that stalled it); credit it
        and let the {wait}-patched terminator flow on into the next row. KEYPATCH: files printed through op 0x90
        (a message picked by its FFFB key: KAIWA, SxxOK, SQA, SCQA, SMEN..) get their 0x90 ops patched on load to
        print the first wanted keyed row (KAIWA1: 0/240 -> 240/240).
        `--var STARTPATCH=1` (with --keypatch; untested beyond TxxSEN, where it fails): a file with no 0x90 site gets
        its entry replaced by `00BA 003C <row> 00B9 0037` and the VM task (obj+0x12 = pc) moved there. TxxSEN still
        print nothing: they park in op 0x82 (a world-map wait) and moving the pc does not wake them.
        Pass 6 settings (2026-11-21), each a textforce.lua/warp.lua --var: PRINTPATCH=1 (every `003C` print site
        points at the first wanted row: rows behind untaken branches), RECHOICE=1 (re-patch after each choice menu:
        SMEN01 10 -> 20 of 26 rows per run), NOBATTLE=1 (SSxxxx: battle op and the end-jumps on its result become
        gotos, SS0204 0 -> 30/30), MASH_ROTATE=3 (warp.lua: 0..2 downs before each circle: battle "ran away" rows,
        other menu answers). TxxSEN run as a battle with hero xx (how_to_run); SSxxyy run with hero xx.
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


SEN = re.compile(r"T(\d\d)SEN")  # hero NN's battle lines (event id NN): loaded in any battle with hero NN in front
SEN_HOST = "T0101"
BHERO = re.compile(r"T(\d\d)\d\d")
SS = re.compile(r"SS(\d\d)\d+")  # SSxxyy..: hero xx's story events


def run_dir(out, nm, how):
    """the folder warp.py writes for this run: its --name, else bt_<nm> / ev_<nm> (warp.py's own naming)"""
    args, battle = how
    if "--name" in args:
        return out / args[args.index("--name") + 1]
    return out / (("bt_" + nm) if battle else ("ev_" + nm.replace(":", "_")))


def how_to_run(nm, bt, hero=None):
    """(warp.py args, battle?) for event name nm. TxxSEN run as battle SEN_HOST with hero xx in front (HERO=xx),
    forcing their own file (FORCE_ID=xx): `--event` parks them in op 0x82, a world-map wait. `hero`: run nm as an
    event for that current hero (TM12ALL switches on it: op 0x5D), into ev_<nm>_h<hero>."""
    if hero:
        return ["--event", f"{nm}:{hero}", "--name", f"ev_{nm}_h{hero}"], False
    m = SEN.fullmatch(nm)
    if m:
        h = int(m[1])
        swap = []
        if h == 1:  # a hero-1 battle loads no SEN file (2026-11-21 probe): load T01SEN as T03SEN in a hero-3 one
            h, swap = 3, ["--var", f"SWAP='3={nm}'"]
        return ["--battle", SEN_HOST, "--name", "bt_" + nm, "--var", f"HERO={h}", "--var", f"FORCE_ID={h}",
                *swap], True
    if nm.startswith("TM"):  # in the battle table, but heroes talking, no fight: as --battle TM0312B/TM12ALL hang
        return ["--event", nm], False
    if nm in bt:  # a battle's file loads under its own id (textforce.lua FORCE_ID), after the host starts the fight
        m = BHERO.match(nm)  # Txxyy: hero xx's battle, whose dialogue needs hero xx on the field (T0703: Ryudral)
        hero = ["--var", f"HERO={int(m[1])}"] if m and 1 <= int(m[1]) <= 12 else []
        return ["--battle", nm, "--var", f"FORCE_ID={bt[nm]}", *hero], True
    m = SS.fullmatch(nm)
    if m and 1 <= int(m[1]) <= 12:  # hero xx's story event: its battle (op 0xD3) needs hero xx, not MYH16's Reiv
        return ["--event", f"{nm}:{int(m[1])}", "--name", "ev_" + nm], False
    return ["--event", nm], False


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


def signatures(exe):
    """{sector: 'pos:value ..'} the code words (file halfword index: value) at pc 0, 1 and the first ops after the
    variable area. textforce.lua patches a file only once these are in the buffer: the slot table names a file a
    few frames before its data replaces the last file's (a patch on that frame hit stale words, TITA 2026-11-21).
    Code sits before the text, so insertion doesn't move these words."""
    import evscript
    gdata = (ROOT / "work/disc/tree/GDATA.BIN").read_bytes()
    out = {}
    for sec, _, data, _ in evscript.script_files(exe, gdata):
        try:
            sc = evscript.Script(data)
        except evscript.ParseError:
            continue
        base = sc.code_off // 2
        pcs = [0, 1] + list(range(sc.start, min(sc.start + 6, len(sc.code))))
        out[sec] = " ".join(f"{base + p}:{sc.code[p]}" for p in pcs)
    return out


def cmd_run(a):
    build, root = Path(a.build).resolve(), Path(a.root).resolve()
    offs, ends, names, choice = load(build)
    exe = (ROOT / "work/disc/tree/PSX.EXE").read_bytes()
    sigs = signatures(exe)
    seen = shown(root)
    want = wanted(offs, names, seen, choice)
    # unshown choice menus: flag 2 in TARGETS (textforce.lua lets the scene's own print draw them)
    chmiss = set(choice) - {rid for s, v in offs.items() for o, rid in v if rid in choice and (s << 16 | o) in seen}
    if a.only:
        keep = {int(x, 16) for x in a.only.split(",")}
        want = {s: v for s, v in want.items() if s in keep}
    if a.rows:  # only these row ids (a chain that stalls on an earlier row never reaches them otherwise)
        ids = set(a.rows.split(","))
        want = {s: [r for r in v if r in ids] for s, v in want.items()}
        want = {s: v for s, v in want.items() if v}
    n = a.pass_no or 1
    while not a.pass_no and (root / f"p{n}").exists():
        n += 1
    out = root / f"p{n}"
    out.mkdir(parents=True, exist_ok=True)

    bt = battles(exe)

    def finished(nm):
        p = run_dir(out, nm, how_to_run(nm, bt, a.hero)) / "emu.txt"
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
            cells.append(f"{o // 2},{e // 2},{1 if rid in miss else 2 if rid in chmiss else 0}")
        how, battle = how_to_run(nm, bt, a.hero)
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "tools/debug/warp.py"), *how, "--cue", cue,
               "--root", str(out), "--frames", str(min(a.frames + 400 * len(miss), 200000)),
               "--shot-every", str(a.shot_every), "--timeout", "3600", "--var", f"MASH_EVERY={a.mash}",
               "--lua", str(ROOT / "tools/lua/textforce.lua"),
               "--var", f"TARGETS='{' '.join(cells)}'"]
        if sec in sigs:
            cmd += ["--var", f"SIG='{sigs[sec]}'"]
        for v in a.var or ():
            cmd += ["--var", v]
        if a.keyforce:
            cmd += ["--debugger", "--var", "KEYFORCE=1"]
        if a.keypatch:
            cmd += ["--var", "KEYPATCH=1"]
        if a.jumpforce:
            cmd += ["--debugger", "--var", "JUMPFORCE=1"]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        d = run_dir(out, nm, (how, battle))
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
            s.add_argument("--hero", type=int, help="run each file as an event for this current hero (TM12ALL)")
            s.add_argument("--rows", help="comma-separated row ids (365E.1B8A,..): force only these")
            s.add_argument("--shot-every", type=int, default=1500, help="frames between shots (30 to catch a page)")
            s.add_argument("--var", action="append", help="extra textforce.lua variable, NAME=LUA (e.g. SKIPKEY=1)")
            s.add_argument("--pass", dest="pass_no", type=int, help="resume pass N (default: start the next one)")
            s.add_argument("--keyforce", action="store_true",
                           help="interpreter mode + KEYFORCE: point op 0x90 key lookups at wanted rows (KAIWA, SxxOK)")
            s.add_argument("--keypatch", action="store_true",
                           help="KEYPATCH: the same by patching the file's 0x90 ops when it loads (no debugger, fast)")
            s.add_argument("--jumpforce", action="store_true",
                           help="interpreter mode + JUMPFORCE: move a waiting script to a print of its rows (TxxSEN)")
    a = ap.parse_args()
    {"freeze": cmd_freeze, "run": cmd_run, "left": cmd_left}[a.cmd](a)


if __name__ == "__main__":
    main()
