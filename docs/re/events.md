# Event scripts (the bulk of the dialogue)

## Where (verified: the line "あの、あなたはヴォーラス騎士団の" on screen in Reiv's scouting scene, f100 from
`work/qa/ex3/s003000.sstate`, sits in RAM at 0x8016D39C and in GDATA.BIN at 0x1ACE594)

- 468 script files in GDATA.BIN, sectors 0x3559-0xA0EC, found through three `(u32 sector, u32 byte size)` tables in
  PSX.EXE: 0x5988 (229 entries), 0x60B8 (71), 0x62F8 (171; 2 of them are not scripts). Every script starts with u16 6.
  No two files overlap. `python -X utf8 tools/events.py list` prints them (global index, table, entry, sector, size,
  text estimate); `tools/events.py text N` prints one file's text runs. Test: `tests/test_text.py::test_event_scripts`.
- Uncompressed, sector-padded. Sizes 0x800-0x7000 bytes.
- The game loads one file whole at RAM **0x8016C608** (file offset 0xD94 = RAM 0x8016D39C). The buffer is the zero
  run PSX.EXE 0x15CDA2-0x163E0A (RAM 0x8016C5A2-0x8017360A), so it holds at most ~0x7000 bytes, and the largest
  original file is exactly 0x7000. **English text that grows a file needs a bigger buffer, a second load, or a denser
  encoding (phase 5 decision).**
- The other 0x4C50 table (423 entries) covers sectors 0-0x3559: images, maps, 3D/battle data (`disc.md`). The table
  at 0x3BA0 (85 entries) indexes SDATA.BIN (sound).

## Format (partly decoded)

- Header (guess from one file): u16 6, u16 0x1D2 / 0x1AE (header length?), u16 count (0xB62 = ~ the number of used
  halfwords in RAM), then a table of small numbers, then named blocks ("WORK1", "WORK2" ... as ASCII, 0x1D4 on).
- Code: 16-bit words; 0xFFxx are VM opcodes, everything < 0x66C in a text run is a font code (`text.md`). Text runs
  are inline, not FFFF-terminated, and a line break between runs is an opcode, e.g.
  `FFE0 FFE0 FFF1 83E7 FFF0 <line 1> FFF0 <line 2> FFF0 FFF3 FFF2 FFE0 ...`: FFF0 ends a line, FFF3/FFF2 end a page
  (guess), FFF1 takes one argument (0x83E7, 0x8000: speaker/face, guess), args with bit 15 set look like variable or
  label references. The angel's name is inserted by an opcode: "私は天使の[F8]汚[80]と言うものです" is
  `FFF8 8000` between two runs.
- VM: dispatch is a compare chain at 0x800CCB50 (opcodes 0xFFC0-0xFFFF seen there: FFC0 FFC1 FFE0 FFE5 FFE8 FFE9 FFEA
  FFEE FFF0 FFF1 FFF2 FFF3 FFF5 FFF7 FFF9 FFFA ...). Entry table: 10 x (u16 id, u16 halfword offset) at RAM
  0x8016C5B8, looked up by 0x800C7FF4 (returns 0x8016C608 + 2*offset). Opcode argument counts are **not decoded**:
  the extractor (phase 4) must read every handler's argument fetches, or the runs will include argument words.

## Size (estimate, heuristic in `tools/events.py`)

~553,000 text characters across the 468 files (runs of >= 3 non-zero codes with >= 2 kana; includes some argument
noise and duplicated branches). For comparison PSX.EXE has ~970 strings / ~14,000 characters. Text reads naturally
in samples from files 18, 100, 250 and 400 (Reiv's scouting, refusals, fairy advice).
