# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress: English renders in-game, most box widths measured;
  EPILOG hook, credits, torture line and the remaining width gaps left. Builds 2026-11-20 (commit after df6d21a):
  `build/favorite_dear_en_marker.bin` sha1 9cfa9ef2cc7838da196d64ed7eda5ff0414d756b, `build/favorite_dear_en_ruler.bin`
  sha1 5b266f681e9387790673eb2cb3cc3dfd66dafabf (both reach every scene toured below).
- **Phase 5 so far (2026-11-20):**
  - Font/encoding decided (D9, `text.md` §English): pair glyphs, hook `asm/font.asm` at 0x800FDCA8, font
    `fonts/en6x12.txt` (`tools/font_en.py`), encoder `tools/en.py`.
  - `tools/insert.py` (called by `build.py`): event scripts rebuilt with reference relocation (each file must fit
    its original sector-rounded slot); PSX.EXE strings in place. Modes `--marker` and `--ruler` (44-letter ruler
    `1234567890ABCDEFGHIJ1234567890abcdefghij+-*/` as each row's first line) in `build.py`.
  - **English letters render** (pair glyphs, clean, `work/qa/p5/kaiwa1_boxes.png`). Marker ids show in dialogue,
    battle dialogue, hub menus, week panels, save menu, name entry, confirm box (`work/qa/marker/<scene>/`).
  - Fixed: (1) the first marker build crashed loading any event: exe.tsv rows 788-795 were the event-name table's
    tail and u16 tables (0x164E7A-0x1660E0); region 2 now starts at 0x1660E0 (859 EXE rows),
    `test_exe_data_untouched`. (2) Ruler/marker text cut to an EXE slot dropped `{wait}{end}` and hung the opening:
    `insert.fit_slot` trims letters, keeps codes (`test_exe_codes_kept`). (3) **Missed text:** 43 battle scripts in
    the data table 0x4C50 (BM_xx, 1294 segments) and messages starting with a glyph < 0xE6 that the sweep read as
    ops (also in 3B01/3B05/3B0A): `events.TABLES` + `evscript.MSG_REFS` re-sweep; 513 scripts, 10023 rows.
    jp_left on the marker build: GDATA clean (runs >= 16 bytes); PSX.EXE leftovers are kana/kanji conversion tables.
  - **Width gate:** `docs/windows.tsv` (letters x lines per variant, measured from zoomed shots in `work/qa/p5/`):
    dialogue and battle boxes 40 x 3 (portrait or not), hub location 11, hub list 17, week name tag / ACTION 10,
    save menu 12, confirm prompt 16 visible after a hidden 3-cell lead-in (the original hides これで), yes/no 7.
    Guesses left: hub help line (box 46, VRAM area 42, budget 40), name entry, credits, EPILOG.
  - Tools: `warp.py --shot-every N`, `tools/lua/crashtrace.lua`, `tools/lua/trap.lua` (trap-byte free-RAM test),
    `excatch.lua` skips syscalls.
- **Next (phase 5):**
  1. **EPILOG.EXE hook** (endings show garbage glyphs, `work/qa/marker/epilog_end3/f012300.png`). Its renderer is
     0x800526E8 (same interface as PSX 0x800FDCA8, unoptimised build; displaced instructions `addiu sp,-0x40` /
     `sw ra,0x3c(sp)`), reached via 0x800311DC -> 0x80051C98. EPILOG has no free space in its image (trap test:
     0x800671DC-0x80068240 is live, filling it hangs; 0x80010000-0x800109A4 and 0x80099180+ are overwritten).
     Free in ending 3: 0x80140000-0x80180000. Plan: append hook+font after the image (t_size +0x800, file offset
     0x90000 = 0x8009F800), point the header pc0 (0x80013BD0) at a stub that copies the blob to 0x80170000 and jumps
     to 0x80013BD0; share the hook body with `asm/font.asm` (macro). Trap-test 0x80170000-0x80171000 across all
     23 endings (`trap.lua`) first. FD_BALL.EXE: check whether it prints any font text.
  2. Credits: FIN.EXE prints STAFF.TXT (Shift-JIS, own font); find its glyph path, then mark it.
  3. Glyph torture line (all printable ASCII + double spaces) in one dialogue row; name-entry Latin grid and the
     odd-length-name half-cell gap; hub help line real limit (needs EXE repointing, phase 7).
  4. PSX.EXE hook space 0x80124E60 is only checked by RAM dumps: run `trap.lua` on it across several scenes.
  Phase 7 items: script growth past a file's slot (159 files at 2.5x English length) needs GDATA relocation plus a
  larger buffer or a dictionary; battle scripts load at 0x801CE000 (own buffer limit to find).
- **Done:**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md` indexes the notes; `tbl/jp.tbl` complete).
  - Phase 2 (`docs/re/debug.md` has the how and the addresses): `tools/debug/warp.py` + `warp.lua` reach all 86
    rows of `tools/debug/scenes.tsv` from a cold boot (`warp.py --all --state -j 4`, 2026-11-20: 86 ok, states in
    `work/states/<scene>.sstate`, proofs `work/qa/warp/<scene>/arrived.png` checked). Kinds: title/load/option/
    newgame/week/map, `event` (any script in MYH16's slot, `NAME:HERO`), `save` (load a card), `exec` (FIN credits,
    FD_MOV, FD_BALL minigame, EPILOG; `EPILOG:N` = ending N via the scratchpad, rows epilog_end1-23), `battle` (a
    battle by its own T-event). `tools/debug/save.py` edits cards. No game over exists (GOVER.EXE is never exec'd).
  - Phase 3: `tools/build.py` (dumpsxiso unpack if missing, mkpsxiso repack, edited files via `source=` in a
    generated layout; `edits()` returns {disc path: bytes} and is empty). `tests/test_build.py`: identity build is
    byte-identical to `rom/`.
  - Phase 4 (2026-11-20): event-script VM decoded (`docs/re/events.md` §Format: per-file opcode argument table,
    references, inline messages, printer codes in `tbl/ev.tbl`); `tools/evscript.py` parses all 470 scripts (468 +
    2 orphans). `tools/extract.py` writes `script/events/<sector>.tsv` (8781 rows, 562k chars, 7483 distinct),
    `script/exe.tsv` (867 PSX.EXE rows incl. the two name-entry grids), `script/staff.tsv` (176 credit lines),
    `script/sjis.tsv` (5 memory-card titles). `tests/test_extract.py`: every row round-trips byte-exact, coverage
    per source (scripts sweep end to end; PSX.EXE regions hold only rows, padding and the listed data tables;
    STAFF.TXT rebuilds), TSVs equal the extractor's output; a corrupted cell fails it (checked). `tbl/jp.tbl` gained
    FF20 `{var}` / FFE0 `{val}` (PSX.EXE template placeholders).
- **Known gaps in the debug tool:** TxxSEN (ids 1-12) have no warp: they start from a world-map task (0x8011B92C)
  that a RAM write can't install (`debug.md`). Their text gets checked from the files until the world-map flow is
  found. TM*/keys >= 0xC8 played through `battle` show black; they are covered as plain events (`ev_tm02all`).
- **Next (phase 5, `references/pipeline.md` §Marker):** font/VWF decision (12x12 1bpp font, glyph writer takes a
  width in $s0: `text.md` §Font), insertion with reference relocation for event scripts (`events.md` last bullet),
  marker build (`[id]` per row), width gate per box variant. Decide the translation unit: rows are whole messages
  (up to ~4000 chars, many `{wait}{clear}` pages); a per-page view for translators may help.
- **Open questions for later phases (not blocking):**
  - Phase 5: the script buffer is full in the largest file (0x7000 bytes, `events.md`): English that grows a file
    needs a bigger buffer, a second load or a denser encoding. A second 8x8 font (GDATA e204-e206); the on-screen
    休暇/勇者の発見 menu and はい/いいえ box sources not found (`graphics.md`). The save-screen name box fits 6
    characters (header slot 0x204, 12 bytes). PSX.EXE: 78 rows have no direct pointer (reached by base+offset or
    sequence; find before relocating). Memory-card titles are Shift-JIS, 64-byte field.
  - Event names map to GDATA files through the name lookup at 0x8003B680 (462 ids, 444 unique names vs 470 files);
    not needed for extraction, useful for naming the TSVs in QA.
  - 1824 of 9094 messages are referenced directly; how the rest are reached (printer index carried on) matters only
    for keeping message order on insert.
  - Movies DEMO.STR / ENDING.STR / the end of OP.STR not checked for burned-in text.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
