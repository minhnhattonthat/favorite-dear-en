# Disc layout

Unpack: `tools/mkpsxiso/mkpsxiso-2.30-win64/dumpsxiso.exe -x work/disc/tree -s work/disc/layout.xml "rom/Favorite Dear (Japan).cue"`
(56 files, one Mode2 data track; `license_data.dat` is the licence sectors). Boot: SYSTEM.CNF -> SLPS_01.759 (loader),
then `_LOADE.EXE` chains PSX.EXE (main game, 1.6 MB, t_addr 0x80010000), FD_BALL.EXE, GOVER.EXE, PS_MOV.EXE,
TITLE/EPILOG.EXE, TITLE/FD_MOV.EXE, DATA/FIN.EXE (credits: DATA/STAFF.TXT is plain Shift-JIS with 0E 0B line breaks
and some 84xx box/Cyrillic codes; 01-13.TIM + FONTCLUT.TIM).

Rebuild (verified 2026-11-20, `tests/test_build.py`): mkpsxiso 2.30 on the dumpsxiso layout gives the original .bin
byte for byte (sha1 509ffd8f...). `tools/build.py` writes `build/<name>.xml` with absolute paths (paths in the XML
are relative to the XML) and a `source=` per edited file; work/disc/tree is never written. Files are laid out in
layout order, so a file that grows past its sector count shifts every later LBA (savestates then go stale).

| File | What | State |
|---|---|---|
| PSX.EXE | main game code, the 12x12 font, and (at least part of) the dialogue script | verified (see text.md) |
| GDATA.BIN (84 MB) | graphics/data pack, sector-aligned files | partly mapped |
| SDATA.BIN | sound (VAB "pBAV" etc.), own (size, sector) table after the name table at PSX.EXE 0x3a3c | guess |
| *.PSS, TITLE/*.PSS | LZSS-compressed images (u32 size, 160x240 16-bit = 320x240 8-bit, etc.) | verified |
| *.STR | FMV (OP.STR opening, ENDING.STR, DEMO.STR, NEIC.STR, SOFIX1.STR) | not looked at |
| XAPACK1.XA, DATA/FINA_BGM.XA | XA audio (voices/music) | not looked at |
| DUMMY.BIN | 27 MB of zeros (padding) | verified (first MB) |

## LZSS (verified: `tools/lzss.py`, decompress -> compress -> decompress identical on TITLE.PSS, NOWLOAD.PSS, TTL_OPT.PSS, NECLOGO1.PSS)

u32 LE decompressed size, then Okumura LZSS: flag byte read LSB first, 1 = literal, 0 = 2-byte ref
`pos = b0 | (b1 & 0xF0) << 4`, `len = (b1 & 0x0F) + 3`; 4096-byte ring, zero-filled, write start 0xFEE.
Decompressed PSS images start with a 12-byte header: u32 size-ish (0x00012C0C), u32 0, u16 width-in-halfwords, u16 height,
then pixels. The stream ends exactly at the file end (no padding inside PSS files).

## GDATA.BIN directory (verified: entries line up with LZSS/TIM starts)

PSX.EXE 0x4C50 (also in FD_BALL/GOVER/PS_MOV/EPILOG EXEs): 423 entries of `u32 sector, u32 size` (size sector-rounded),
contiguous from sector 0, covering only the first 0x16BA800 bytes (23 MB) of GDATA.BIN. The script tables follow
at 0x5988 (below). Most entries are uncompressed TIMs (176 of 195 checked start 10 00 00 00);
entries 0-2, 8-10, 15-16, 64-65, 137-140, 151-153, 204-296 are LZSS images; 308+ look like map/3D records
(header 0x48/0x50 + offsets). Only 158 sector-aligned LZSS blocks exist in the whole file; the rest is raw.
All GDATA tables in PSX.EXE (verified: every entry lines up with a TIM, LZSS block or script header, no overlaps):
0x4C50 (423 entries, sectors 0-0x3559: images, maps, 3D/battle data), 0x5988 (229), 0x60B8 (71) and 0x62F8 (171)
(sectors 0x3559-0xA0EC: event scripts, `events.md`). 0x3BA0 (85 entries) is the same format for SDATA.BIN.
A name table at PSX.EXE ~0x1E480-0x29F18 lists ~660 development file names (TIM/BIN/VAB/SEQ/SEP), and a pointer table
at PSX.EXE 0x3A3C (90 entries: GDATA.BIN, SDATA.BIN, then sound names) - how names map to GDATA entries is not decoded.

## Graphics text

See `graphics.md` (the survey). The first event's name/menu panel (f6600 of `tools/routes/newgame.txt`) is likely
GDATA e015/e016 (name entry).
