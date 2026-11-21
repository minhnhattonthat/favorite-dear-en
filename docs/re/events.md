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

## Format (verified: all 470 scripts sweep end to end, every reference lands on an op or a message token;
`tools/evscript.py check`, `tests/test_extract.py`)

- Header: u16 argtab (always 6), u16 vars (0x1D2, 0x1AE...: the symbol area, "WORK1", "WORK2" ... ASCII records),
  u16 code (byte offset of the code). argtab..vars is **one u16 per opcode = its argument-word count**, read by the
  step loop 0x800C8BB0 (`s7 = argtab[op]`, then `pc += 1 + s7`). Same 230-entry table in nearly every file.
- Code = halfwords from `code`; pc counts halfwords. Opcodes < len(argtab) are VM ops: 0x00-0x3A inline in the step
  loop (arithmetic, 0x28 goto, 0x29 call (stack at obj+0x20, depth obj+0x16 < 12), 0x2A return, 0x37 end, 0x38/0x39
  yield), 0x3B-0xE5 through the jump table at 0x80039108 (handler 0x800CA570), 0xFFFF a 1-word no-op. An argument
  with bit 15 set is a reference, `arg & 0x7FFF` = a code halfword index; 0x800C855C follows reference chains.
- pc 0 is `0x28 <goto>` over a data area of variable slots (also numeric tables: 25/50/75/100 rows, not text) in all
  but 26 files (those start with 0x3C or 0x00 ops at pc 0).
- **Messages are inline data between ops**, never reached by fall-through (the op before one is an end, goto or
  return). 1824 of 9094 messages are referenced directly (op 0x3C and friends); the rest follow one another (the
  printer keeps its index at obj+0x10). A message is a printer stream for 0x800CC9EC: font codes < 0x66C and 0xFFxx
  codes, ended by 0xFFFF; `FFE0 FFE0` right after an 0xFFFF is padding. 163 references land inside a message (a
  shared tail): the extractor cuts rows there. The last message of a file may end without 0xFFFF; a lone 0xFFFC
  closes some files.
- Printer codes (args = halfwords, from the compare chain at 0x800CCB50; names in `tbl/ev.tbl`): FFF0 newline `{n}`;
  FFF3 wait for a button `{wait}`; FFF2 clear the box `{clear}`; FFFF end; FFF1 a speaker/portrait id `{spk}` (0x3E7 =
  none, 1 arg); FFF8 n inserts the name string at 0x8019C250 + 80*n `{name}` (the angel is `FFF8 8000`, hero 8001);
  FFF9 a b inserts a string from a table `{ins}`; FFFD/FFFE 3 args (call 0x800D028C); FFF6 2; FFC0 FFC1 FFE0 FFE5 FFE7
  FFE8 FFE9 FFEA FFEE FFF4 FFF5 FFF7 FFFA FFFB 1; FFE6 FFEB FFEC FFED FFFC 0. FFFB is not in the chain but every use
  has one arg word (`FFFB 8xxx` opens 7054 messages).
- Entry table: 10 x (u16 id, u16 halfword offset, ...) at RAM 0x8016C5B8, looked up by 0x800C7FF4 (returns
  0x8016C608 + 2*offset): up to 10 loaded scripts share the buffer.
- **Op 0x90 `<value> <table ref>`** (handler 0x800CB880; s4 = code base, s2 = pc; verified by disassembly and by
  patching it in game, `tools/lua/textforce.lua` KEYPATCH): resolves arg 1 to a value (0x800C855C: a reference
  reads that code halfword, the "variable slots" at pc 2..), then scans from the arg-2 reference to 0xFFFC for a
  message opening `FFFB k` with `k & 0x7FFF == value` and starts the printer after the key. KAIWA*, SxxOK, SY*, SQA,
  SCQA and SMEN files print almost only this way (values from globals such as 0x1A/0x1C/0x1D), so one play shows
  one row of them.
- **The printer index obj+0x10 moves a page at a time** (it jumps to the next {wait} or the end), not per letter:
  a frame hook first sees a message when its first page is already drawn. Re-pointing obj+0/obj+0x10 while the
  printer is mid-message stalls it (~60 frames, then it resumes elsewhere): obj+0/0x10 are not its whole state.
- **Ops seen in branches (2026-11-21, SS0204/EVFUM02):** `0028 <ref>` goto; `002B a b <ref>` and `002C a b <ref>`
  conditional jumps (a, b: values or work-word refs); `003C <ref>` print the message at ref; `00D3/00E3 <stage>
  <ref to the hero word>` battle; `0037` end. After a story battle the script reads the result (`005E 000F 8007`)
  and jumps to its end unless won: a warp's battle ends at once, so the text after it never plays.
  textforce `NOBATTLE` turns the battle and those end-jumps into gotos to the next op; `PRINTPATCH` points every
  `003C` at a row still wanted (a branch the cold boot never takes, e.g. EVFUM "returned" vs "quit").
- Two scripts have no size in any table: 0x5988 entry 0 (sector 0x3559, size 0) and sector 0x3672 (in no table);
  each runs to the next file and parses. Their 13 rows carry the note "orphan" (possibly unused).
- **Insertion (phase 5/7) must relocate:** longer text shifts every later halfword, so every reference argument
  (`Script.refs`, including the pc-0 goto) past the change must be rewritten, and message order kept.

## Size (exact, `script/events/`)

8781 rows (message segments with at least one glyph) in 463 files: 562,420 characters, 7483 distinct rows (526,986
characters). Rows are whole messages and can be long (up to ~4000 characters of markup: a scene's conversation with
many `{wait}{clear}` pages). PSX.EXE: 867 rows, 11,583 characters. EPILOG's save prompts are event text too
(sector 0x3B77, one message of `{f7:0080}`-prefixed lines).
