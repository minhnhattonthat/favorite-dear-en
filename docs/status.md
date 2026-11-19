# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (event, save-load, hub, credits, epilog, minigame and battle warps work; town events left, then the --all regen). Last build: none yet.
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
    - 2026-11-20: **battles** (`battle_castle` SS0204:2, `battle_forest` SS0501:5, proofs checked). Scripts start
      battles with sub-command 0xD3 for the current hero (byte 0x80020991); MYH16's slot leaves hero 16 (Reiv),
      whose sprite crashes the loader, so `NAME:HERO` in a scene arg / warp.lua `HERO` sets it. The old `battle`
      kind is removed. **No game over exists**: GOVER.EXE is never exec'd and draws nothing; the OVER_* TIMs are
      only in the name list (`debug.md` §Programs). `warp.py --lua/--var/--debugger` runs hooks with a warp;
      new helpers `tools/lua/cmdlog.lua`, `stateat.lua`, `pcsample.lua`, `excatch.lua`.
- **Next (finish phase 2):**
  1. Town events (T0101.., TxxSEN): with HERO=1 T0101 now runs its commands (cmdlog from
     `work/states/event_pre13000.sstate`, standalone EVENT/HERO vars) up to sub-command **0xE0** (sets byte
     0x80184170 = 1) and **0xE1** (calls 0x800CD5E8(a, b)) at f623, then the screen stays on a blank box: it likely
     waits for the town screen. Read 0x800CD5E8 and who reads 0x80184170; either set what it waits for or warp in
     through the town (hub map -> town; in week 1 a town visit loads no event, so find the unlock flag). TxxSEN are
     the stage table's 0-12 (BD8 table), so T01SEN may need battle_start's path too (try `T01SEN:1` after T0101).
     If a town event can't be reached cleanly, record why in `debug.md` and list it as a known gap.
  2. A real ending (EPILOG with params): game_clear's opcode (0x800C4680) is the legit path; find an event using it,
     or set scratchpad 0x1F800000/0x14/0x1C before exec (needs scratchpad write from Lua).
  3. Then run `warp.py --all --state`, check every arrived/post shot, update scenes.tsv notes: phase 2 done.
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
