# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (event, save-load, hub, credits, epilog, minigame warps work; town events, battle and game over left). Last build: none yet.
- **Done:**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md` indexes the notes; `tbl/jp.tbl` complete).
  - Phase 2 so far (`docs/re/debug.md` has the how and the addresses):
    - `tools/debug/warp.py` + `warp.lua`: cold boot -> any row of `tools/debug/scenes.tsv` (columns scene, kind,
      arg, after, frames, card, post, proof, note) or any event by name (`--event NAME`); proof shot
      `work/qa/warp/<scene>/arrived.png` (+ `post.png` when the row has `post` presses); `--state`, `--all`, `-j`.
      `--var TRACE=1` logs MODE/PHASE flag changes and the loaded-event list.
    - Kinds: title/load/option/newgame/week/map; `event` (swap the name in MYH16's event slot; 32 script families
      verified); `save` (load save N from the row's card via Load Game -> hub -> 予定 -> week screen; a rejected
      save never arrives); `exec` (jump the CPU into PSX.EXE exec() to start FIN/EPILOG/FD_MOV/FD_BALL).
    - Scenes verified 2026-11-20, every proof shot checked: week2 (game-written card), save_edit (edited card),
      hub, hub_ability, hub_ability2, hub_map, hub_system, credits (FIN staff roll), epilog (EPILOG.EXE text box,
      no ending params), ending_movie (FD_MOV), minigame (FD_BALL Slime Ball), plus all the earlier rows.
    - `tools/debug/save.py` (ls/check/set --week --ap --name --poke --bad-sum): edits a game-written card and fixes
      c0/c1. Proven: the edited card (week 5, AP 999, name ミカエルアン) loads and shows the values; the same card
      with a wrong c0 is rejected (load returns to the save list). Cards: `work/saves/week1.mcd`, `week2.mcd`,
      `work/saves/edit/ap999.mcd` (rebuild: `save.py set work/saves/week2.mcd work/saves/edit/ap999.mcd --ap 999
      --week 5 --name ミカエルアン`).
    - Program chain mapped (`debug.md` §Programs): all switches go through _LOADE.EXE with an index at 0x1F800020;
      `game_clear` 0x8003ABB8; GOVER.EXE is referenced by no code (looks like an old main-program build).
- **Next (finish phase 2):**
  1. Battle: `battle_start` 0x800D08E4 is only called by two event-script opcode handlers (0x800CC5A0/0x800CC5F8).
     Calling it from the vsync loop hangs the emulator (warp kind `battle`, experimental). Find the opcode number
     (VM compare chain at 0x800CCB50), find events whose scripts use it, and warp to one with kind `event`.
  2. Game over: the real screen uses OVER640/OVER_JI/OVER_BAK.TIM (GDATA name list at PSX.EXE RAM 0x80014440) inside
     PSX.EXE; find its trigger (xref the GDATA index of OVER_BAK, or watch loads with `tools/lua/loadlog.lua`) and
     add a scene. A real ending (EPILOG with params): game_clear's opcode (0x800C4680) is the legit path; find an
     event using it, or set scratchpad 0x1F800000/0x14/0x1C before exec (needs scratchpad write from Lua).
  3. Town events (T0101.., TxxSEN) stick on a blank box in MYH16's slot. Start routines 0x800CFDC8 / 0x800CFF28
     store a context byte (0x80020991) first; set that context or patch the slot those routines use. A hub-map town
     visit loads no event (probe 2026-11-20).
  4. Then run `warp.py --all --state`, check every arrived/post shot, update scenes.tsv notes: phase 2 done.
- **Open questions for later phases (not blocking):**
  - Phase 4: VM opcode argument counts (dispatch 0x800CCB50) are not decoded; the extractor needs them (`events.md`).
    Event names map to GDATA files through the name lookup at 0x8003B680 (462 ids, 444 unique names vs 468 files).
  - Phase 5: the script buffer is full in the largest file (`events.md`); a second 8x8 font (GDATA e204-e206); the
    on-screen 休暇/勇者の発見 menu and はい/いいえ box sources not found (`graphics.md`). The save-screen name box
    fits 6 characters (header slot 0x204, 12 bytes).
  - Movies DEMO.STR / ENDING.STR / the end of OP.STR not checked for burned-in text. FIN.EXE credits read
    DATA/STAFF.TXT; EPILOG.EXE has its own text.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
