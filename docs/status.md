# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (event warp works; town events, battle, game over, credits and save.py left). Last build: none yet.
- **Done:**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md` indexes the notes; `tbl/jp.tbl` complete).
  - Phase 2 so far (`docs/re/debug.md` has the how and the addresses):
    - `tools/debug/warp.py` + `warp.lua`: cold boot (no save, no state) -> any row of `tools/debug/scenes.tsv` or any
      event by name (`--event NAME`, names from `tools/events.py names`), proof shot `work/qa/warp/<scene>/arrived.png`,
      `--state` writes `work/states/<scene>.sstate`, `--all` regenerates everything, `-j` runs in parallel (~40 s each).
      Exit 1 when a scene is not reached, its proof is blank, or the screen never changes after arrival.
    - Event warp = overwrite the name slot of event id 32 (MYH16, the first week-1 event) in the event-name table at
      RAM 0x80173640 so the game's own loader fetches the target script. Verified for 32 script families
      (all rows in scenes.tsv reached and progressing, 2026-11-20): every family except the town T-series.
    - Base scenes reached with proof: title menu, Load Game, Option, name entry, week-1 screen, world map, MYH16.
    - RAM flags: 0x8001A4A8 (5 = week screen idle, 1 transitions/map, 4 event dialogue, 2/3 opening) and 0x8001A654.
    - Hub menu (予定/能力/地図/システム) and the in-game save flow found; game-written cards `work/saves/week1.mcd`,
      `week2.mcd`; `tools/debug/mcd.py` (blank/ls/check); save checksum c1 verified, c0 guessed (`debug.md`).
    - Helpers: `tools/lua/loadlog.lua` (GDATA/event loads), `tools/lua/stackat.lua`, `tools/modefind.py` /
      `tools/ramval.py` (mode flags from RAM dumps), `tests/test_debug.py`.
- **Next (finish phase 2):**
  1. Town events (T0101..T1205, T00*, Txx SEN) stick on a blank box in MYH16's context: find where MAPSYS/the map
     triggers them (watch `load_event` 0x800C82E8 callers with `--debugger`, or diff RAM before a T load) and add a
     second warp kind that patches the right slot or sets the town context.
  2. Scenes still missing: hub menus (能力, 地図, システム via `POST` after `week`), week-2+ screen, battle (BT_*/BM_*
     files load in week 1: find a forced battle), game over (GOVER.EXE), endings into EPILOG.EXE/FIN.EXE credits
     (does SEND01 chain into them? mash longer), FD_BALL.EXE minigame, PS_MOV.EXE.
  3. `tools/debug/save.py`: edit AP (0x199C), week (0x275C?), names; fix c1 (sum 0x204-0x22B) and c0; prove an edited
     `week1.mcd` loads via title -> Load Game with no error (warp kind `load` + POST presses).
  4. Each scene: run `warp.py --all --state`, check every arrived.png, then phase 2 is done.
- **Open questions for later phases (not blocking):**
  - Phase 4: VM opcode argument counts (dispatch 0x800CCB50) are not decoded; the extractor needs them (`events.md`).
    Event names map to GDATA files through the name lookup at 0x8003B680 (462 ids, 444 unique names vs 468 files).
  - Phase 5: the script buffer is full in the largest file (`events.md`); a second 8x8 font (GDATA e204-e206); the
    on-screen 休暇/勇者の発見 menu and はい/いいえ box sources not found (`graphics.md`).
  - Movies DEMO.STR / ENDING.STR / the end of OP.STR not checked for burned-in text.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
