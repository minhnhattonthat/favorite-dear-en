# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (Step 0 done 2026-11-20). Last build: none yet.
- **Done:**
  - Step 0: template filled, rom.sha1 pinned (bin + cue), PCSX-Redux + SCPH-5500 in tools/, mkpsxiso/armips/xdelta in tools/, guard hook in .claude/settings.json (canary blocked), pre-commit runs tools/check.py (a failing test was rejected), original disc smokes to title (`tools/routes/boot.txt`), Start opens the title menu, Lua probe logs.
  - Recon so far (docs/re/): disc unpacked to work/disc/ (dumpsxiso; rerun the command in docs/re/disc.md on a fresh clone); LZSS codec (`tools/lzss.py`, tested); GDATA.BIN directory at PSX.EXE 0x4C50 (423 entries, first 23 MB only); script encoding = 16-bit font-cell codes with FFFE/FFFC/FFFF controls, opening dialogue found in PSX.EXE 0x15A8C8; 12x12 1bpp font at PSX.EXE 0x1213C0 (`tools/font.py`), kanji in Shift-JIS order (used-only subset).
  - `tools/routes/newgame.txt` + `--mash 90 --mash-key circle` reaches the first dialogue (~f7200); savestates of that run are in work/qa/ng/ (gitignored; regenerate with the command in docs/re/text.md history if missing: emu.py ... --route tools/routes/newgame.txt --frames 9000 --mash 90 --mash-key circle --state-every 1500).
- **Next (phase 1, in order):**
  1. Build `tbl/jp.tbl` for codes 0x000-0x5DD: render glyphs, match to MS Gothic 12 px with Shift-JIS order as a constraint for kanji 0x0C0-0x5CC, eyeball the punctuation/kana rows (`python -X utf8 tools/font.py sheet work/disc/tree/PSX.EXE work/font/sheet.png 0x5E0`). Verify by decoding the opening event.
  2. Map the script: all text regions in PSX.EXE (scan for runs of codes < 0x5E0 ending in FFFF), their pointer tables, and whether other script banks load from GDATA.BIN (check the 4 GDATA LZSS blocks with many FFFE: sectors 0x1FAC, 0x1FBC, 0x351A, 0x824B; and watch RAM 0x8016xxxx across a scene change). Also the other EXEs (FD_BALL, GOVER, EPILOG, FIN/STAFF.TXT credits in Shift-JIS).
  3. Free space candidates in PSX.EXE; how the remaining 60 MB of GDATA.BIN is indexed (table at PSX.EXE 0x5988).
  4. Graphics-text survey into docs/re/graphics.md (menus, name entry, status screens, STR subtitles?).
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Not checked: the PCSX-Redux GUI taking keyboard input, since nobody is at the keyboard in a dispatched run.)
