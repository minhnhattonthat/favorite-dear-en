"""cover_sweep.py: text-coverage sweep, one `warp.py --event NAME` run per event, resumable.

    python -X utf8 tools/cover_sweep.py [--build work/qa/cover_build] [--root work/qa/cover] [-j 2] [--frames 30000]

Runs every name in <build>/events.txt that has no finished run yet (a finished run has a line starting with
"exit" in <root>/ev_<NAME>/emu.txt), with tools/lua/textlog.lua, shots every 1500 frames, on <build>'s .cue.
Re-run it after a crash: it picks up where it stopped. Then:
    python -X utf8 tools/textcover_map.py convert <root>/*
    python -X utf8 $SKILL/scripts/textcover.py <root> <build>/strings.tsv --waive docs/text_unshown_unloaded.tsv
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def done(root, ev):
    p = os.path.join(root, "ev_" + ev.replace(":", "_"), "emu.txt")
    if not os.path.exists(p):
        return False
    with open(p, encoding="utf-8", errors="replace") as f:
        return any(line.startswith("exit") for line in f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default="work/qa/cover_build")
    ap.add_argument("--root", default="work/qa/cover")
    ap.add_argument("-j", type=int, default=2)
    ap.add_argument("--frames", type=int, default=30000)
    a = ap.parse_args()
    build = os.path.abspath(os.path.join(ROOT, a.build))
    root = os.path.join(ROOT, a.root)
    cue = [os.path.join(build, f) for f in os.listdir(build) if f.endswith(".cue")][0].replace("\\", "/")
    with open(os.path.join(build, "events.txt"), encoding="utf-8") as f:
        events = [line.strip() for line in f if line.strip()]
    todo = [e for e in events if not done(root, e)]
    print(f"{len(events) - len(todo)} done, {len(todo)} to run", flush=True)

    def run(ev):
        cmd = [sys.executable, "-X", "utf8", os.path.join(ROOT, "tools", "debug", "warp.py"), "--event", ev,
               "--cue", cue, "--root", root, "--frames", str(a.frames), "--shot-every", "1500",
               "--lua", os.path.join(ROOT, "tools", "lua", "textlog.lua")]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"{ev}\t{r.returncode}", flush=True)

    with ThreadPoolExecutor(a.j) as ex:
        list(ex.map(run, todo))
    left = [e for e in events if not done(root, e)]
    print(f"finished; {len(left)} without an exit line: {' '.join(left[:40])}", flush=True)


if __name__ == "__main__":
    main()
