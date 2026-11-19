# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next (phase 1 recon done 2026-11-20). Last build: none yet.
- **Done:**
  - Step 0: template filled, rom.sha1 pinned (bin + cue), PCSX-Redux + SCPH-5500 in tools/, mkpsxiso/armips/xdelta in tools/, guard hook in .claude/settings.json (canary blocked), pre-commit runs tools/check.py (a failing test was rejected), original disc smokes to title (`tools/routes/boot.txt`), Start opens the title menu, Lua probe logs.
  - Phase 1 recon (docs/re/, index in docs/re/README.md):
    - `tbl/jp.tbl` complete for all 0x66C font cells + printer control codes (`text.md`); kanji matched exactly against MS Gothic 12 px (`tools/fontmatch.py`, `tools/mktbl.py`), kana/Latin by layout; `tests/test_text.py` decodes the opening line and Reiv's line and round-trips every PSX.EXE/EXE string.
    - Text locations: PSX.EXE ~970 FFFF-terminated strings (menus, items, places, fairy/tutorial/opening dialogue; `text.md`); **the bulk (~550K chars) is in 468 event-script files in GDATA.BIN** (sector tables at PSX.EXE 0x5988/0x60B8/0x62F8), inline text in VM bytecode, loaded whole to RAM 0x8016C608 into a ~0x7000-byte buffer that the largest file already fills (`events.md`, `tools/events.py`).
    - Credits DATA/STAFF.TXT = Shift-JIS with each byte +1 (`text.md`). Free-space candidates and RAM limits (`space.md`). Graphics-text survey (`graphics.md`, `tools/tim.py`).
  - Routes: `tools/routes/newgame.txt` (+ `--mash 90 --mash-key circle`) reaches the first dialogue (~f7200) and the first week screen (~f10000 = work/qa/ng2/s012000.sstate after continuing from work/qa/ng/s009000); `tools/routes/week1.txt` from there sets both fairies to hero search and starts the week; mashing circle then reaches Reiv's scouting scene (~f2500-f4000, work/qa/ex3/s003000.sstate). States are in work/ (gitignored); regenerate by replaying the routes.
- **Next (phase 2, debug tool):** a cold-boot way to reach any scene: start from `references/emulator-qa.md` §Debug tool. Leads: event scripts are files in a table, so a Lua warp can force-load event file N into the buffer at 0x8016C608 (find the loader that reads the 0x5988 table and the variable holding the current event id); the week screen and map are reached by `week1.txt`. Scene list goes in `tools/debug/scenes.tsv`.
- **Open questions for later phases (not blocking):**
  - Phase 4: VM opcode argument counts (dispatch 0x800CCB50) are not decoded; the extractor needs them (`events.md`).
  - Phase 5: the script buffer is full in the largest file, so English needs a bigger/moved buffer or a denser encoding (e.g. two half-width letters per 16-bit code); a second 8x8 font exists (GDATA e204-e206) with unknown encoding; on-screen 休暇/勇者の発見 menu and the はい/いいえ confirm box sources not found (`graphics.md`).
  - Movies DEMO.STR / ENDING.STR / the end of OP.STR not checked for burned-in text.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Not checked: the PCSX-Redux GUI taking keyboard input, since nobody is at the keyboard in a dispatched run.)
