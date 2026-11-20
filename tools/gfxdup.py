"""gfxdup.py: find other copies of every redrawn graphic (gfx/*.tsv) anywhere on the original disc tree.

    python -X utf8 tools/gfxdup.py

A game can load a second copy of an image from a pack (GDATA e207 block 3 = e243, the battle's status stamps), so
redrawing only the directory entry leaves Japanese on screen. Searches every file for the first 64 bytes of each
image's slot (LZSS stream or TIM) and, for LZSS images, for a 64-byte run of the decoded pixels (an uncompressed
copy). Prints each hit outside the image's own slot; a hit needs a gfx.MIRRORS entry (or a reason it is never
drawn). Exit 1 if any hit is not covered by MIRRORS."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfx  # noqa: E402
import lzss  # noqa: E402


def main():
    exe = (gfx.TREE / "PSX.EXE").read_bytes()
    gdata_path = gfx.TREE / "GDATA.BIN"
    files = [p for p in gfx.TREE.rglob("*") if p.is_file() and p.suffix.upper() not in (".STR", ".XA")]
    data = {p: p.read_bytes() for p in files}
    gdata = data[gdata_path]
    mirrored = {}
    for e, places in gfx.MIRRORS.items():
        for pack, index in places:
            off, size = gfx.slot(exe, pack, gdata)
            blocks = gfx.pack_blocks(gdata[off:off + size])
            mirrored.setdefault(e, []).append(off + sum(len(b) for b in blocks[:index]) + 4 * len(blocks))
    bad = 0
    for e in gfx.entries():
        if gfx.is_pss(e):
            continue
        off, size = gfx.slot(exe, e, gdata)
        probes = [("slot", gdata[off:off + 64])]
        img = gfx.Image(exe, gdata, e)
        raw = img.raw(img.pix)
        if img.kind == "lzss4":
            mid = 12 + len(raw) // 2
            probes.append(("pixels", raw[mid:mid + 64]))
        for kind, probe in probes:
            if not probe.strip(probe[:1]):
                continue  # a flat run matches everywhere
            for p, d in data.items():
                i = d.find(probe)
                while i >= 0:
                    own = p == gdata_path and off <= i < off + size
                    if not own and kind == "slot" and img.kind == "lzss4":  # same head, different image?
                        try:
                            own = lzss.decompress(d[:i + size + 16] + bytes(16), i)[0] != raw
                        except (IndexError, ValueError):
                            own = True
                    if not own:
                        ok = p == gdata_path and i in mirrored.get(e, [])
                        bad += not ok
                        print(f"{gfx.name(e)} {kind} copy: {p.relative_to(gfx.TREE)} {i:#x}"
                              f"{' (MIRRORS)' if ok else ''}")
                    i = d.find(probe, i + 1)
    print(f"{bad} uncovered copies")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
