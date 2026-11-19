"""ramval.py: print RAM values at given addresses across dumps (2 MB PS1 main RAM from L.dump_ram).

    python -X utf8 tools/ramval.py --addr 0x8001A4A8 0x8001A654 [--width 2] DUMP..."""
import argparse
import struct


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--addr", nargs="+", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--width", type=int, default=2, choices=(1, 2, 4))
    ap.add_argument("dumps", nargs="+")
    a = ap.parse_args()
    fmt = {1: "<B", 2: "<H", 4: "<I"}[a.width]
    print("dump".ljust(40) + " ".join(f"{x:08X}" for x in a.addr))
    for p in a.dumps:
        d = open(p, "rb").read()
        vals = [struct.unpack_from(fmt, d, x & 0x1FFFFF)[0] for x in a.addr]
        print(p[-40:].ljust(40) + " ".join(f"{v:8X}" for v in vals))


if __name__ == "__main__":
    main()
