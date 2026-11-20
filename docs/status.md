# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build next (phase 4 extract done 2026-11-20). Last build: 2026-11-20, no edits,
  sha1 509ffd8fc65852eab028238d06fe23f9f0db7d13 (= original), smoke ok.
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
