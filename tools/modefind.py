"""modefind.py: find RAM words that tell one screen from others (a mode flag for the debug tool).

    python -X utf8 tools/modefind.py --in A.bin B.bin --out C.bin D.bin.. [--width 1|2|4] [--max 40]

Lists addresses whose value is the same in every --in dump and differs from it in every --out dump,
smallest values first (mode ids tend to be small). Dumps are 2 MB PS1 main RAM (L.dump_ram)."""
import argparse

import numpy as np


def load(path, width):
    dt = {1: np.uint8, 2: np.uint16, 4: np.uint32}[width]
    return np.frombuffer(open(path, "rb").read(), dtype=dt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inn", nargs="+", required=True)
    ap.add_argument("--out", nargs="+", required=True)
    ap.add_argument("--width", type=int, default=2, choices=(1, 2, 4))
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--lo", type=lambda s: int(s, 0), default=0x10000)
    a = ap.parse_args()
    ins = [load(p, a.width) for p in a.inn]
    outs = [load(p, a.width) for p in a.out]
    v = ins[0]
    ok = np.ones(len(v), bool)
    for x in ins[1:]:
        ok &= x == v
    for x in outs:
        ok &= x != v
    ok[: a.lo // a.width] = False
    idx = np.nonzero(ok)[0]
    idx = idx[np.argsort(v[idx], kind="stable")]
    print(f"{len(idx)} candidates")
    for i in idx[: a.max]:
        addr = 0x80000000 + i * a.width
        print(f"{addr:08X} in={int(v[i]):#x} out=" + ",".join(f"{int(x[i]):#x}" for x in outs[:8]))


if __name__ == "__main__":
    main()
