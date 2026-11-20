# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress: marker build boots, in-game check and width gate not done.
  Last builds 2026-11-20: `build/favorite_dear_en_marker.bin` sha1 984211e0cb04130a778946d101bc33efe9ff8cfd (smoke
  ok), `build/favorite_dear_en_ruler.bin` sha1 997e05943bdf8b4dc1c33c37d73285068383f224 (not booted yet).
- **Phase 5 so far (2026-11-20):**
  - Font/encoding decided (D9, `text.md` §English): pair glyphs, hook `asm/font.asm` at 0x800FDCA8, font
    `fonts/en6x12.txt` (`tools/font_en.py`), encoder `tools/en.py`.
  - `tools/insert.py` (called by `build.py`): event scripts rebuilt with reference relocation (each file must fit
    its original sector-rounded slot); PSX.EXE strings in place. Modes `--marker` and `--ruler` (44-letter ruler
    `1234567890ABCDEFGHIJ1234567890abcdefghij+-*/` as each row's first line) in `build.py`.
    `tests/test_insert.py`: identity rebuild, marker relocation (every ref lands on the same item), font widths,
    EXE writes stay in string slots.
  - Marker build: smoke ok. Warps to ev_kaiwa1/ev_setumei/ev_item/myh16 reached the scene (fairy shown, f13500)
    but hit the 900 s wall-clock timeout with -j 4 before the text printed; the -j 2 --timeout 1800 re-run was
    killed by the harness for low system memory. **Not yet seen: any English letter on screen.**
- **Next (phase 5):** with memory free, `warp.py ev_kaiwa1 --cue build/favorite_dear_en_marker.cue --timeout 1800
  --state` (one at a time), check that the pair glyphs render and ids show. Then tour more scenes with the marker
  build (EXE text: newgame opening, menus, items) and the ruler build to measure each box variant (dialogue,
  fairy box, choices, menus, item/skill names, name tag) and record it in a window-data file. Then the glyph torture
  line. Open engine items: name entry grid (PSX.017DA4/017E64, left Japanese) needs Latin letters, and odd-length
  names give a half-cell gap; credits (FIN.EXE, Shift-JIS) not marked; script growth past a file's slot
  (159 files at 2.5x English length) needs GDATA relocation plus a larger buffer or a dictionary (phase 7).
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
