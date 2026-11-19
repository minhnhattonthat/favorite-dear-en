"""lzhunt.py: brute-force search for LZSS blocks (tools/lzss.py format) whose output looks like dialogue text.

    python -X utf8 tools/lzhunt.py FILE [STEP=4] [LO] [HI]

Tries every STEP-aligned offset whose u32 size is 512..400000, decodes the first 8 KB and prints offsets where the
output has >= 12 FFFF/FFFE/FFFC halfwords and >= 15 % font codes. Used in phase 1 to rule out compressed script in
PSX.EXE and GDATA.BIN (no real hits: the dialogue is uncompressed, docs/re/events.md). Slow: minutes on GDATA.BIN.
"""
import struct
import sys


def head(d, p, want):
    size = int.from_bytes(d[p:p + 4], "little")
    q = p + 4
    ring = bytearray(4096)
    r = 0xFEE
    out = bytearray()
    flags = nb = 0
    while len(out) < min(size, want):
        if q >= len(d) - 2:
            return None
        if nb == 0:
            flags = d[q]
            q += 1
            nb = 8
        if flags & 1:
            c = d[q]
            q += 1
            out.append(c)
            ring[r] = c
            r = (r + 1) & 4095
        else:
            b0, b1 = d[q], d[q + 1]
            q += 2
            pos = b0 | (b1 & 0xF0) << 4
            for k in range((b1 & 15) + 3):
                c = ring[(pos + k) & 4095]
                out.append(c)
                ring[r] = c
                r = (r + 1) & 4095
        flags >>= 1
        nb -= 1
    return out


def main():
    d = open(sys.argv[1], "rb").read()
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    lo = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0
    hi = int(sys.argv[4], 0) if len(sys.argv) > 4 else len(d) - 8
    for p in range(lo, hi, step):
        size = int.from_bytes(d[p:p + 4], "little")
        if not (512 <= size <= 400000):
            continue
        o = head(d, p, 256)
        if not o or len(o) < 256:
            continue
        o = head(d, p, 8192)
        if not o or len(o) < 512:
            continue
        hw = struct.unpack_from("<%dH" % (len(o) // 2), o)
        f = sum(c in (0xFFFF, 0xFFFE, 0xFFFC) for c in hw)
        t = sum(0x23 <= c <= 0x66B for c in hw)
        if f >= 12 and t > len(hw) * 0.15:
            print(hex(p), size, t, f, flush=True)


if __name__ == "__main__":
    main()
