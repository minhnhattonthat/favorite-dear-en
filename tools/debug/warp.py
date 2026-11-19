"""warp.py: boot the disc cold and land on a scene from tools/debug/scenes.tsv (no save, no savestate).

    python -X utf8 tools/debug/warp.py SCENE [SCENE..] [--cue build/favorite_dear_en.cue] [-j 3] [--state]
    python -X utf8 tools/debug/warp.py --all [-j 3] [--state]      regenerate every scene (shots + optional states)
    python -X utf8 tools/debug/warp.py --event NAME                any event script by name (see `events.py names`)
    python -X utf8 tools/debug/warp.py --list

Each run writes work/qa/warp/<scene>/ (shots every 150 frames, sheet.png, log.txt) and, with --state,
work/states/<scene>.sstate (60 frames after arrival). Exit 1 if any scene was not reached ("WARP OK" missing in the
log) or, for scenes with AFTER=mash, the screen never changed after arrival (a stuck script). Results go to
work/qa/warp/results.tsv. The Lua side is tools/debug/warp.lua; how it works: docs/re/debug.md."""
import argparse
import csv
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
from skill import SKILL  # noqa: E402

sys.path.insert(0, os.path.join(SKILL, "scripts"))
import sheet  # noqa: E402

ORIG_CUE = os.path.join(REPO, "rom", "Favorite Dear (Japan).cue")
SCENES = os.path.join(HERE, "scenes.tsv")
COLS = ["scene", "kind", "event", "after", "frames", "note"]


def load_scenes():
    with open(SCENES, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.reader(f, delimiter="\t") if r and not r[0].startswith("#")]
    head, rows = rows[0], rows[1:]
    assert head == COLS, f"scenes.tsv header {head} != {COLS}"
    out = {}
    for r in rows:
        assert len(r) == len(COLS), f"scenes.tsv row has {len(r)} columns, want {len(COLS)}: {r}"
        d = dict(zip(COLS, r))
        assert d["scene"] not in out, f"duplicate scene {d['scene']}"
        out[d["scene"]] = d
    return out


def frame_of(log, tag):
    for line in log.splitlines():
        if line.startswith(tag):
            return int(line.rsplit(" f", 1)[1])
    return None


def run(sc, cue, state, timeout):
    out = os.path.join(REPO, "work", "qa", "warp", sc["scene"])
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".png"):
            os.remove(os.path.join(out, f))
    lua = [f"KIND='{sc['kind']}'", f"AFTER='{sc['after'] or 'mash'}'"]
    if sc["event"]:
        lua.append(f"EVENT='{sc['event']}'")
    if state:
        p = os.path.join(REPO, "work", "states", sc["scene"] + ".sstate").replace("\\", "/")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        lua.append(f"STATE='{p}'")
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "emu.py"), os.path.abspath(cue),
           "--out", out, "--script", os.path.join(HERE, "warp.lua"), "--frames", sc["frames"] or "16000",
           "--shot-every", "150", "--timeout", str(timeout)]
    for v in lua:
        cmd += ["--var", v]
    with open(os.path.join(out, "emu.txt"), "w", encoding="utf-8") as fo:
        rc = subprocess.call(cmd, stdout=fo, stderr=subprocess.STDOUT)
    logp = os.path.join(out, "log.txt")
    log = open(logp, encoding="utf-8", errors="replace").read() if os.path.exists(logp) else ""
    ok_at = frame_of(log, "WARP OK")
    verdict, distinct = "ok", 0
    if rc != 0:
        verdict = f"emu exit {rc}"
    elif ok_at is None:
        verdict = "not reached"
    else:
        shots = sorted(f for f in os.listdir(out) if f[0] == "f" and f[1:7].isdigit() and f.endswith(".png")
                       and int(f[1:7]) >= ok_at + 150)
        imgs = [sheet.read_png(os.path.join(out, f)) for f in shots]
        seen = []
        for im in imgs:
            if not any(sheet.diff(im, s) < 0.002 for s in seen):
                seen.append(im)
        distinct = len(seen)
        if (sc["after"] or "mash") == "mash" and distinct < 2:
            verdict = "stuck"
        proof = os.path.join(out, "arrived.png")
        if not os.path.exists(proof):
            verdict = "no arrived.png"
        elif sheet.is_blank(sheet.read_png(proof)):
            verdict = "blank"
        sheet.make(out, lo=max(0, ok_at - 300), limit=16, changed=0.002)
    return sc["scene"], verdict, ok_at, distinct


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--event", action="append", default=[], help="ad-hoc event name (no scenes.tsv row needed)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--cue", default=ORIG_CUE)
    ap.add_argument("--state", action="store_true", help="also save work/states/<scene>.sstate")
    ap.add_argument("-j", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    table = load_scenes()
    if a.list:
        for s in table.values():
            print(f"{s['scene']:<16} {s['kind']:<8} {s['event']:<9} {s['note']}")
        return 0
    todo = list(table.values()) if a.all else []
    for name in a.scenes:
        if name not in table:
            sys.exit(f"unknown scene {name}; --list shows them")
        todo.append(table[name])
    for ev in a.event:
        todo.append({"scene": "ev_" + ev, "kind": "event", "event": ev, "after": "mash", "frames": "16500",
                     "note": ""})
    if not todo:
        ap.error("name a scene, --event NAME or --all")
    with ThreadPoolExecutor(max_workers=a.j) as ex:
        res = list(ex.map(lambda s: run(s, a.cue, a.state, a.timeout), todo))
    os.makedirs(os.path.join(REPO, "work", "qa", "warp"), exist_ok=True)
    with open(os.path.join(REPO, "work", "qa", "warp", "results.tsv"), "a", encoding="utf-8") as f:
        for r in res:
            f.write("\t".join(str(x) for x in r) + "\n")
    bad = 0
    for name, verdict, at, distinct in res:
        print(f"{name:<16} {verdict:<12} arrived f{at}  distinct shots after arrival: {distinct}")
        bad += verdict != "ok"
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
