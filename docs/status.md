# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate: ready to start (phase 5 done 2026-11-20).
- **Builds (2026-11-20, commit "Phase 5 done"):** `build/favorite_dear_en_marker.bin` sha1
  cd6324cd63fe7d72e926bdc72cfcd09270691f95, `_ruler.bin` 50c223e684ded4244886e112ad9ed958a631892d, `_torture.bin`
  d2f103ef850f431eb345018504bdc833df8562c1, `favorite_dear_en.bin` (no English yet, hooks only)
  d1fa3e6f852a005d514b45468b769ef37c8b2ae9, smoke ok.
- **Next (phase 6, `references/translation.md`):**
  1. Decide the translation unit: rows are whole messages (up to ~4000 chars, many `{wait}{clear}` pages); give
     translators a per-page view with the 40 x 3 budget per page (`docs/windows.tsv`), or batch by script file.
  2. Budgets per row come from `docs/windows.tsv` (all variants measured): dialogue/battle/EPILOG 40 x 3, hub help 40,
     hub location 11, hub list 17, week tag/ACTION 10, save menu 12, confirm 16 (+6 hidden lead-in), yes/no 7, angel
     name 10, credits 14 full-width (minus the line's indent). Tag each `script/*.tsv` row with its variant first.
  3. Glossary (`glossary.md`) and `docs/decisions.md` rulings (credits English, names...) before dispatching.
  Phase 7 items already known: script growth past a file's slot (159 files at 2.5x English length) needs GDATA
  relocation plus a larger buffer or a dictionary; battle scripts load at 0x801CE000 (own buffer limit to find);
  PSX.EXE strings that grow need repointing (proved: `hub_help` test repointed PSX.15C998 via file 0x15CAB0); the
  name-entry grid must produce pair codes, and odd-length runtime names leave a half-cell gap; optional FIN pair-glyph
  hook for 28-letter credits (`text.md` §Credits).
- **Phase 5 (done 2026-11-20):**
  - Font/encoding (D9, `text.md` §English): pair glyphs; hook body `asm/pair.inc` + `pair_data.inc`, used by
    `asm/font.asm` (PSX.EXE 0x800FDCA8) and `asm/epilog.asm` (EPILOG.EXE 0x800526E8: one appended sector, a stub
    copies the blob to 0x80170000, free in all 23 endings by trap test, `space.md` §EPILOG). Font `fonts/en6x12.txt`,
    encoder `tools/en.py`.
  - `tools/insert.py` (called by `build.py`): event scripts rebuilt with reference relocation (each file must fit its
    original sector-rounded slot); PSX.EXE strings in place; EPILOG.EXE patched; DATA/STAFF.TXT credits in
    full-width forms (FIN.EXE draws only double-byte codes, ASCII hangs it). Modes `--marker`, `--ruler`, `--torture`.
  - Marker ids show in dialogue, battle dialogue, hub menus, week panels, save menu, name entry, confirm box,
    endings (EPILOG) and credits (`work/qa/marker/<scene>/`, `work/qa/warp/epilog_end3`, `work/qa/p5/credits_*.png`).
    Non-text excluded (EXE data tables, name-entry grids). jp_left on the marker build: GDATA clean; PSX.EXE leftovers
    are kana/kanji conversion tables. The Slime Ball help box is graphics (TTL_INFO.PSS, `graphics.md`).
  - Width gate: every variant in `docs/windows.tsv` measured from zoomed shots; torture line clean
    (`work/qa/p5/torture/sheet.png`). New scenes `name12_week`, `name12_save` (12-letter angel name card
    `work/saves/edit/name12.mcd`); `credits` proof moved to 1800 frames (text shows), `minigame` to 1200.
- **Done:**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md` indexes the notes; `tbl/jp.tbl` complete).
  - Phase 2 (`docs/re/debug.md` has the how and the addresses): `tools/debug/warp.py` + `warp.lua` reach all rows of
    `tools/debug/scenes.tsv` from a cold boot (`warp.py --all --state -j 4`, 2026-11-20: 86 ok, states in
    `work/states/<scene>.sstate`, proofs `work/qa/warp/<scene>/arrived.png` checked). Kinds: title/load/option/
    newgame/week/map, `event` (any script in MYH16's slot, `NAME:HERO`), `save` (load a card), `exec` (FIN credits,
    FD_MOV, FD_BALL minigame, EPILOG; `EPILOG:N` = ending N via the scratchpad, rows epilog_end1-23), `battle` (a
    battle by its own T-event). `tools/debug/save.py` edits cards. No game over exists (GOVER.EXE is never exec'd).
  - Phase 3: `tools/build.py` (dumpsxiso unpack if missing, mkpsxiso repack, edited files via `source=` in a
    generated layout). `tests/test_build.py`: identity build is byte-identical to `rom/`.
  - Phase 4: event-script VM decoded (`docs/re/events.md`); `tools/evscript.py` parses all scripts; `tools/extract.py`
    writes `script/events/<sector>.tsv` (513 scripts, 10023 rows incl. 43 battle scripts), `script/exe.tsv`,
    `script/staff.tsv` (176 credit lines), `script/sjis.tsv` (5 memory-card titles). `tests/test_extract.py`: every
    row round-trips byte-exact, coverage per source.
- **Known gaps in the debug tool:** TxxSEN (ids 1-12) have no warp: they start from a world-map task (0x8011B92C)
  that a RAM write can't install (`debug.md`). Their text gets checked from the files until the world-map flow is
  found. TM*/keys >= 0xC8 played through `battle` show black; they are covered as plain events (`ev_tm02all`).
- **Open questions for later phases (not blocking):**
  - The script buffer is full in the largest file (0x7000 bytes, `events.md`). A second 8x8 font (GDATA e204-e206);
    the on-screen 休暇/勇者の発見 menu and はい/いいえ box sources not found (`graphics.md`). PSX.EXE: 78 rows have no
    direct pointer (reached by base+offset or sequence; find before relocating). Memory-card titles are Shift-JIS,
    64-byte field.
  - Event names map to GDATA files through the name lookup at 0x8003B680 (462 ids); useful for naming TSVs in QA.
  - 1824 of 9094 messages are referenced directly; how the rest are reached matters only for message order on insert.
  - Movies DEMO.STR / ENDING.STR / the end of OP.STR not checked for burned-in text.
- **Waiting on the user:** nothing.
- **Open bugs:** none.
