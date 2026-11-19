# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (Step 0 setup done 2026-11-20). Last build: none yet.
- **Done:** Step 0: template filled, rom.sha1 pinned (bin + cue), PCSX-Redux + SCPH-5500 BIOS in tools/, mkpsxiso/armips/xdelta in tools/, guard hook in .claude/settings.json (canary blocked), pre-commit runs tools/check.py (failing test rejected), original disc smokes to title and Start opens the title menu (`tools/routes/boot.txt`), Lua probe logs (`tools/lua/hello.lua`). Disc unpacked to work/disc/ with dumpsxiso.
- **Next:** Phase 1 recon: find the script container (SDATA.BIN / GDATA.BIN / PSX.EXE), encoding, pointers, compression, graphics-text survey -> docs/re/.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Not checked: the PCSX-Redux GUI taking keyboard input, since no one is at the keyboard in a dispatched run.)
