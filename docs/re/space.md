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

## EPILOG.EXE (verified 2026-11-20, trap test)

- The image 0x80010000-0x8009F800 has no free run: its zero runs 0x80010000-0x800109A4 and 0x80099180+ are
  overwritten after main starts, and filling 0x800671DC-0x80068240 hangs it. crt0 (pc0 0x80013BD0) clears BSS
  0x80073320-0x800911B8.
- **0x80160000-0x80180000 is free in all 23 endings**: `trap.lua` armed at f11450 (just after EPILOG's arrival) on
  `epilog_end1`-`epilog_end23`, 7 checks each to f20000, 0 bytes changed. `asm/epilog.asm` copies its blob
  (0x678 bytes) to 0x80170000 from a stub in an appended sector (file 0x90000-0x907FF, the new pc0 0x8009F800).
- Growing EPILOG.EXE by one sector shifts the LBAs of the TITLE/ files after it (EPI_OBJ, FD_MOV, TTL_*.PSS) and
  DUMMY.BIN. Every program finds them by name (CdSearchFile paths in the EXEs), so title, option, minigame and the
  endings still load (marker build, 2026-11-20).
- PSX.EXE: the free run at 0x80124E60 also took a 48-letter test string at 0x80125900 (`hub_help` width test).
  In use: font hook 0x80124E60-0x80125500 (`asm/font.asm` stops there), grown list strings 0x80125500-0x80125980
  (`tools/insert.py` REPOINT; 39 strings to 0x80125782 on 2026-11-20), name-entry code and buffers
  0x80125980-0x80125AF0 (`asm/name.inc`, 2026-11-21). Proof: the Apprentice rank pointer poked to
  the moved "Chief Seraph" draws it on the status screen (`tools/lua/poke32.lua`, `work/qa/p8/rank_chief_seraph.png`).
