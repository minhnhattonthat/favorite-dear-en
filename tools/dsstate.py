"""dsstate.py: read a player's DuckStation savestate (.sav) without DuckStation: main RAM, the embedded screenshot, and
the CPU registers the BIOS saved on a crash. Needs `pip install zstandard` (DuckStation compresses with zstd).

    python -X utf8 tools/dsstate.py STATE.sav --out DIR [--exe build/files_favorite_dear_en/PSX.EXE]

Writes DIR/ram.bin (2 MB, 0x80000000..), DIR/shot.png (what the player saw), DIR/blob.bin (the whole state). Prints
the disc path the player ran, which EXE code differs from --exe (a different build), and the BIOS thread's saved
registers (EPC, Cause, sp, ra..). After an unhandled CPU exception the BIOS halts in A(40h)
SystemErrorUnresolvedException; then Cause/EPC/ra/sp there are the crash. Disassemble RAM with
`disasm.py dis DIR/ram.bin ADDR N --arch mips --base 80000000`.

Format (state version 0x66): 'DUCC', version, title, serial, then at 0xA8 u32s: media path len/offset, ?, screenshot
compression, width, height, compressed size, offset, data compression, compressed size, size, offset. The RAM is found
by locating the EXE's code in the decompressed blob (the section layout shifts between versions)."""
import argparse
import struct
import sys
from pathlib import Path

NAMES = ("zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra "
         "epc hi lo sr cause").split()
EXC = {0: "Int", 4: "AdEL", 5: "AdES", 6: "IBE", 7: "DBE", 8: "Syscall", 9: "Bp", 10: "RI", 11: "CpU", 12: "Ov"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("state")
    ap.add_argument("--out", required=True)
    ap.add_argument("--exe", default=str(Path(__file__).resolve().parents[1] / "build/files_favorite_dear_en/PSX.EXE"))
    a = ap.parse_args()
    import zstandard
    from PIL import Image

    d = Path(a.state).read_bytes()
    if d[:4] != b"DUCC":
        sys.exit("not a DuckStation state")
    f = struct.unpack_from("<12I", d, 0xA8)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    print("version", hex(struct.unpack_from("<I", d, 4)[0]), "media", d[f[1]:f[1] + f[0]].decode("utf-8", "replace"))
    dz = zstandard.ZstdDecompressor()
    w, h = f[4], f[5]
    Image.frombytes("RGBA", (w, h), dz.decompress(d[f[7]:f[7] + f[6]], max_output_size=w * h * 4)).save(
        out / "shot.png")
    blob = dz.decompress(d[f[11]:f[11] + f[9]], max_output_size=f[10])
    (out / "blob.bin").write_bytes(blob)

    e = Path(a.exe).read_bytes()
    t_addr, t_size = struct.unpack_from("<II", e, 0x18)
    probe = e[0x800 + 0x1000:0x800 + 0x1040]
    i = blob.find(probe)
    if i < 0:
        sys.exit("EXE code not found in the state's RAM: another game or a very different build")
    base = i - ((t_addr & 0x1FFFFF) + 0x1000)
    ram = blob[base:base + 0x200000]
    (out / "ram.bin").write_bytes(ram)
    img, seg = e[0x800:0x800 + t_size], ram[t_addr & 0x1FFFFF:(t_addr & 0x1FFFFF) + t_size]
    diff = [k for k in range(0, len(img), 4) if img[k:k + 4] != seg[k:k + 4]]
    print(f"RAM at blob+{base:#x}; {len(diff)} EXE words differ from {Path(a.exe).name} (data changes at runtime; "
          "runs in code mean another build)")

    u32 = lambda addr: struct.unpack_from("<I", ram, addr & 0x1FFFFF)[0]
    tcb = u32(u32(0x80000108))
    regs = [u32(tcb + 8 + 4 * k) for k in range(len(NAMES))]
    r = dict(zip(NAMES, regs))
    code = (r["cause"] >> 2) & 0x1F
    print(f"BIOS thread {tcb:08X}: EPC={r['epc']:08X} Cause={r['cause']:08X} ({EXC.get(code, code)}"
          f"{', in a branch delay slot' if r['cause'] >> 31 else ''})")
    for k in range(0, 32, 8):
        print("  " + "  ".join(f"{n}={v:08X}" for n, v in zip(NAMES[k:k + 8], regs[k:k + 8])))


if __name__ == "__main__":
    main()
