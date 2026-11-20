# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract next (phase 3 identity build done 2026-11-20). Last build: 2026-11-20, no edits,
  sha1 509ffd8fc65852eab028238d06fe23f9f0db7d13 (= original), smoke ok.
- **Done:**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md` indexes the notes; `tbl/jp.tbl` complete).
  - Phase 2 (`docs/re/debug.md` has the how and the addresses): `tools/debug/warp.py` + `warp.lua` reach all 86
    rows of `tools/debug/scenes.tsv` from a cold boot (`warp.py --all --state -j 4`, 2026-11-20: 86 ok, states in
    `work/states/<scene>.sstate`, proofs `work/qa/warp/<scene>/arrived.png` checked). Kinds: title/load/option/
    newgame/week/map, `event` (any script in MYH16's slot, `NAME:HERO`), `save` (load a card), `exec` (FIN credits,
    FD_MOV, FD_BALL minigame, EPILOG; `EPILOG:N` = ending N via the scratchpad, rows epilog_end1-23: 1-12 the hero
    CG endings, 13-23 the sepia-map endings), `battle` (a battle by its own T-event, `--battle NAME`; one row per
    region). `tools/debug/save.py` edits cards (edited card loads; bad checksum is rejected). No game over exists
    (GOVER.EXE is never exec'd).
- **Known gaps in the debug tool:** TxxSEN (ids 1-12) have no warp: they start from a world-map task (0x8011B92C)
  that a RAM write can't install (`debug.md`). Their text gets checked from the files until the world-map flow is
  found. TM*/keys >= 0xC8 played through `battle` show black; they are covered as plain events (`ev_tm02all`).
  - Phase 3: `tools/build.py` (dumpsxiso unpack if missing, mkpsxiso repack, edited files via `source=` in a
    generated layout; `edits()` returns {disc path: bytes} and is empty). `tests/test_build.py`: `--identity` build is
    byte-identical to `rom/`, and a one-byte SYSTEM.CNF edit changes exactly one sector. Build smoke-boots.
- **Next (phase 4):** extract the text to `script/` (TSV) with a roundtrip test (re-encode = original bytes) and a
  coverage test over the text ranges (`references/pipeline.md` §Extract; `docs/re/text.md`, `events.md`): PSX.EXE
  strings, the GDATA event scripts (needs the VM opcode argument counts, below), DATA/STAFF.TXT, EPILOG.EXE.
- **Open questions for later phases (not blocking):**
  - Phase 4: VM opcode argument counts (dispatch 0x800CCB50) are not decoded; the extractor needs them (`events.md`).
    Event names map to GDATA files through the name lookup at 0x8003B680 (462 ids, 444 unique names vs 468 files).
    Sub-commands 0xE0/0xE1 = fade out / wait for fade (`debug.md`).
  - Phase 5: the script buffer is full in the largest file (`events.md`); a second 8x8 font (GDATA e204-e206); the
    on-screen 休暇/勇者の発見 menu and はい/いいえ box sources not found (`graphics.md`). The save-screen name box
    fits 6 characters (header slot 0x204, 12 bytes).
  - Movies DEMO.STR / ENDING.STR / the end of OP.STR not checked for burned-in text. FIN.EXE credits read
    DATA/STAFF.TXT; EPILOG.EXE has its own text.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
