# Free space (candidates only: none is proven free yet)

PSX.EXE loads at 0x80010000, t_size 0x192000, so it ends at RAM 0x801A2000; the stack starts at 0x801FFFF0. RAM above
the EXE is heap: 82-90 of its 94 4 KB pages were non-zero in every RAM dump taken (title intro, fairy dialogue, week
screen, hero scene), so it is not free.

Zero runs >= 2 KB in PSX.EXE checked against four RAM dumps (work/qa/ram1, ram3, ram4, ram5):

| File offset | RAM | Length | In the dumps |
|---|---|---|---|
| 0x12FC3 | 0x800227C3 | 0x12D9 | always zero: best candidate |
| 0x11565D | 0x80124E5D | 0xC93 | always zero: candidate |
| 0x16154 | 0x80025954 | 0x12E8 | 0x12C4 always zero |
| 0x1CD33 | 0x8002C533 | 0xA3D | 0x9A7 always zero |
| 0xB2E4 | 0x8001AAE4 | 0x60FA | used (a text/name work buffer of 0x0000 cells) |
| 0x15CDA2 | 0x8016C5A2 | 0x7068 | event-script load buffer (`events.md`) |
| 0x16CB20 | 0x8017C320 | 0x4384 | text line buffer + more (`text.md`) |
| 0x1714F0 | 0x80180CF0 | 0xD60 | message buffer the printer reads |
| 0x17483A | 0x8018403A | 0x1DFC6 | mostly used at runtime (0x515B common zero) |

Each candidate needs the trap-byte tour (skill `references/pipeline.md` §Recon 2) before use.

Other room:
- PSX.EXE strings are FFFF-terminated and padded to 4 bytes; English that grows a string needs repointing (405 strings
  are pointed at by a u32 vaddr directly, others sit 10/14/18 bytes into records: `text.md`).
- GDATA.BIN can be rebuilt with moved and grown files, since every file is reached through the (sector, size)
  tables in PSX.EXE (`disc.md`, `events.md`); the disc also has DUMMY.BIN (27 MB of zeros) to give back.
- The hard limit is the event-script RAM buffer (~0x7000 bytes, already filled by the largest file).
