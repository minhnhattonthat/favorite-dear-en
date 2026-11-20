# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (worker 12: odd runs and page fragments fixed, build 8000adc5;
  next: plate name bug t0201, re-tour + gate on 8000adc5, open sheets, inkbox, stress saves, textcover).
  Worker 12 (2026-11-21): build **8000adc5ae2a4ab269618e632e6a2bf788a80b56** (check ok 75, fitcheck ok, smoke ok).
  (a) Odd runs before {name}/{ins}: all reworded, `oddname.py` 181 -> **0** (fixes in `work/qa/oddname/fix1-5.tsv`;
  rule learnt: wrap.py carries the word before a name onto the name's line, so that word + space must be even, or
  put the vocative first: "{name}, think it through carefully."). (b) "a fool!"/"shows up."/"Dark Carriage." pages:
  `wrap._page_cut` now breaks an overflowing hard line at a sentence/clause end that fits the page (prefers a '.!?'
  end filling the page, then the latest end leaving 4+ words), else moves the whole line to the next page, else
  rebalances 3+1 lines to 2+2; `tools/pagesplit.py` lists continuation pages opening on a 1-3 word lower-case
  fragment: 165 -> **0**. Both lints run in `tests/test_wrap.py`. +12 pages over the script (52759 -> 52771).
  In game: `work/qa/fix2/battle_t0101` f014850 "That's the iron law of the / "Dark Carriage."" on its own page.
  (c) **battle_t0201 plate bug** (open): the enemy plates (top left) draw one garbage glyph instead of the name
  (`work/qa/tour/battle_t0201/f015150.png`, crop 0,0,160,60 zoom 3; t0101 BANDIT/CHIEF fine). Next: find T0201's
  enemy types (u16 0x80182B2C) and whether their plate goes through the new 0x80042448 renderer or another path
  that still reads the old table 0x8013BFCC (now overwritten, `docs/re/graphics.md` §Battle name plates).
  (d) **Text-coverage event sweep restarted** (the first was killed after 18 events): 426 events on the frozen
  `work/qa/cover_build/` (a870a1cf) into `work/qa/cover/`, -j 2, 30000 frames, log `work/qa/cover_run.txt`, started
  04:20; done events have `^exit` in `work/qa/cover/ev_*/emu.txt`. If it died, rebuild the todo list the same way
  (events.txt minus finished dirs) and re-run. Host RAM is tight (1.2 GB free with 3 PCSX): tours at -j 1 while the
  sweep runs. Note: `warp.py` without `--cue` runs the **Japanese** disc; pass `--cue <abs path>/build/...cue`.
  The tour verdicts are STALE (build changed twice since a870a1cf): re-tour on 8000adc5, `qa_sheets.py`,
  `qa_gate.py init`, review the changed sheets.
  Worker 11 (2026-11-21): build **7da42f5ae6eaa065234e2d09abe08d903ab3bd24** (check ok 72, fitcheck ok, smoke ok).
  (a) Tour on a870a1cf finished (all 97 scenes, one run with the new hook; `epilog` alone times out as before),
  `qa_sheets.py` + `qa_gate.py init`; 159 changed sheets reviewed by 6 read-only Explore passes, verdicts
  `work/qa/verdicts/chunk_7d05558d51d5_*.tsv` + `recheck_2.tsv`. `qa_gate.py check`: 0 unreviewed, 17 not ok (list
  below), and STALE (build now 7da42f5a: re-tour, then init). (b) **textcover calibrated:** the printer reads
  `u16 [obj+0] + 2*u16(obj+0x10)` (obj = [0x8001A4B8]; obj+8 set = name/insert sub-stream at [obj+4] + 2*(obj+0xA));
  `tools/lua/textlog.lua` now logs the absolute halfword index, `textcover_map.py convert` maps it (verified: MYH16
  rows 354D.0C34/0DEA = Reiv's scouting on screen). `strings --waive` writes `docs/text_unshown_unloaded.tsv` (186
  rows in files no event id loads). Tour coverage: 66/8824 rows. `warp.py --frames N` added; an **event sweep** of
  all 444 event names (`--event` each, 30000 frames, mash) was started in the background on a frozen copy
  `work/qa/cover_build/` (a870a1cf + its `strings.tsv`) into `work/qa/cover/` (log `work/qa/cover_run.txt`,
  ~70 s/event at -j 2, ~4 h). When done: `textcover_map.py convert work/qa/cover/*`, then
  `textcover.py work/qa/cover work/qa/cover_build/strings.tsv --waive docs/text_unshown_unloaded.tsv`. A mash plays
  one branch only (MYH16: 2 of 28 rows), so choice branches/flag variants stay unshown: next, add scenes that pick
  the other choice, or waive per family with a reason. (c) Fixed: one-word last lines in the epilogues (3B73/3B74);
  "My name is  Raviel" double gap: an odd run ending in a space before `{name}`/`{ins}` is padded to a whole 12-px
  cell (pair glyphs, no half cell possible), so the run must be reworded to an even length; `tools/oddname.py` lists
  them (194 -> **181 families left**, `work/qa/oddname/odd.tsv`; done: "My name's", "I'm the angel"). Next: reword
  the rest (vocatives "Hey, ", "you, " ...: flip parity inside the run after the last `{n}`, e.g. expand a
  contraction, then `fixrows.py`, `batches.py check/merge`, re-run oddname until 0). (d) Not bugs: blank angel name
  in `epilog_*` warps (JP identical), green key colour at x>560 (warp state); added to `docs/visual-qa-brief.md`.
  **Open sheets now:** battle_castle f014550 and battle_t0101 f014700/f014850: a sentence split across the box
  scroll leaves "a fool!"/"shows up."/"Dark Carriage." alone (3B25.0950, 34CC.14C6: page breaks by wrap.py, rebalance
  pages); battle_t0201 plates name missing ("Lv 8" only; all btname rows are filled, look at the frame); battle_t0901
  ポイズン badge; epilog_end1 f013800 "card." over the Fin. logo (compare JP: `warp.py epilog_end1 --root
  work/qa/tour_jp`); ev_bos_clr "Peace level up" placement; stray "P1"/". ." (ev_an, ev_kaiwa1, ev_s0000ok,
  ev_s01ok, ev_evfum02); garbage tiles ev_slove01, ev_ss0101, ev_tm02all (probably warp state: compare JP);
  hub_save_list ラビエル on the save slot (week2.mcd was written by the JP build: likely ok, confirm). Several of the
  old ids (ev_an/qa_sheet_3, epilog_end9/qa_sheet_5 ...) are stale sheet files from the first tour that qa_sheets no
  longer makes: delete `qa_sheet_N.png` files older than the tour's frames and drop their manifest lines.
  Choice boxes for inkbox (from the reviewers): Yes/No `ev_item/f014100.png 166,182,308,44`, save-slot box in every
  ending (`epilog_end15/f017400.png 33,169,588,52`; "Slot 1" sits ~24 px left of its red bar's centre: compare JP),
  `load_list/f005700.png 211,42,74,60`, `option_omake/f004050.png 101,150,118,53`, choices `ev_smen01/f014100.png
  138,170,488,52`.
  Worker 10 (2026-11-21): the re-tour on a870a1cf (`warp.py --all --root work/qa/tour -j 2 --lua
  tools/lua/textlog.lua`, log `work/qa/tour_run2.txt`) was stopped by the host for low memory after 74/98 scenes
  (other projects' emulators share this machine): finish it with only the missing scenes (those whose
  `work/qa/tour/<scene>/log.txt` is older than `tour_run2.txt`), then `qa_sheets.py` + `qa_gate.py init`.
  Textcover groundwork: `tools/textcover_map.py strings` writes `build/strings.tsv` (8824 text rows, key = original
  sector << 16 | byte offset in the built file, from `insert.rebuild_map`; 186 rows sit in files no event id loads =
  the glyph-soup leftovers, to waive); event id -> sector via the GDATA name directory (pointers 0x80013648, 0x39D
  names, index into the table at 0x80014450; MYH16 -> 354D, SQA07 -> 3529 checked). `tools/lua/textlog.lua` logs
  the loaded-script table 0x8016C5B8 (`SCR slot id hwoff`; verified: MYH16 = id 32 at offset 0, then SM02 = id 53)
  and, per frame, u16 obj+0x10 of the task at [0x8001A4B8] (`PIDX`). **Not calibrated:** obj+0x10 is neither a
  buffer index nor a script pc (values 38..435 in SM02, rows at pc 134/704/...); two task objects alternate in that
  slot. Next for textcover: dump the printer object (0x30 bytes) while a box types and find the field that points
  into 0x8016C608.., or use `--debugger` with an exec hook inside the printer at its char fetch; then
  `textcover_map.py convert` (already maps an index to a row) and `textcover.py work/qa/tour build/strings.tsv`.
  LuaJIT gotcha: PCSX `getMemPtr()` bytes are signed and bit ops give signed 32-bit, mask with & 0xFF.
  Worker 9 (2026-11-21): `warp.py --all --root work/qa/tour` on build 64ee6f64: 97/98 scenes ok (`epilog`, no
  ending set, times out: covered by epilog_end1-23). `tools/qa_sheets.py` makes full-size review pages (warp's
  sheet.png is half size); 258 pages in `work/qa/manifest.tsv`, all read by 9 read-only reviewer passes (Explore,
  `docs/visual-qa-brief.md`), verdicts in `work/qa/verdicts/` (202 ok, 56 issue; `recheck_1.tsv` marks 40 fixed).
  Fixed (build a870a1cfc9a5b3c17a1f0d844e1b40f5c4657b1f, check ok 72 tests, fitcheck ok; seen in game in
  `work/qa/fix1/`): (a) "My name isRaviel": wrap.py dropped the space before {name} (`_fix_odd`); (b) wrap.py
  `_balance`: no box ends on a one-word line (2601 -> 96 rows, the rest are "Name:/Huh?!" boxes), 2457 rows rewrapped;
  (c) 3B77.0260 EPILOG clear-data save menu translated (line 6 halves "Slot 1 card "/"Slot 2 card " + line 7 "is
  being checked." work); (d) epilogue "watch them / grow." and "happy / smile."; (e) card dialog line 3 is the first
  8 cells of PSX.1661D6 + PSX.166288, now "Please wait...  Don't remove card."; (f) plate E115 Borunga.
  **Open sheets (re-check on the next tour; compare with the JP tour first):** stray "P1" / ". ." in an empty box
  at the end of ev_an, ev_kaiwa1, ev_s0000ok, ev_s01ok, ev_evfum02 (likely the warp's mash on a leftover box); garbage
  tiles in ev_slove01, ev_ss0101, ev_tm02all (likely warp-state VRAM); battle_t0201 plates show only "Lv 8" (no
  name: check btname rows for that battle's enemies); battle_t0901 status badge ポイズン by the REIV gauge (a battle
  graphic, not e243: find it, D16 says POISON); ev_bos_clr "Peace level up 20 points" drawn over the art (compare
  JP). ev_sy0101 "Right, Angel?" and the "duties to the order" rows were reworded (not yet seen in game).
  **Next:** (1) tour again on a870a1cf with `--root work/qa/tour`, `qa_sheets.py`, `qa_gate.py init ... --glob
  "qa_sheet*.png" --build build/favorite_dear_en.bin` (unchanged pages keep verdicts); (2) JP tour `--root
  work/qa/tour_jp` (default cue) for comparisons; run tours at -j 2: the host killed this worker's -j 3 runs for low
  memory twice; (3) the open sheets; (4) inkbox, stress saves, textcover (no text log exists yet: hook the printer
  0x800CC9EC and log `TEXT <file>.<offset>` from the script buffer 0x8016C608, `docs/re/events.md`).
  Worker 8 (2026-11-21): e204-e206 = bt_font1-3.pss, the 8x8 font of the battle name plates (every enemy
  and hero name under its unit was Japanese: さんぞく, おやぶん ...). `asm/btname.inc` replaces the plate routine
  0x80042448 with an English renderer (upper case, new proportional `fonts/caps4x7.txt`, 64 px, LoadImage);
  names in `trans/btname.tsv` (201 enemies + 17 heroes, `tools/btname.py extract|check|png`, tests
  `tests/test_btname.py`), D17, `docs/re/graphics.md` §Battle name plates. In game: `warp.py battle_t0101`
  f015150 BANDIT/BOSS (build 28b1414e; E051 then renamed CHIEF, data only: the re-run on 64ee6f64 was stopped by
  the host for low memory, so re-check that plate in the tours), `battle_castle` f014700 WIGHT and hero plate REIV. Build sha1
  64ee6f6491832d274ed22638ae7f2df5339d31af, check ok (70 tests), fitcheck ok, smoke ok. Not seen in game yet:
  the longest names (64 px, e.g. Duminas Officer); no warp lists every enemy type. Worker 7 also: the map box's 平和度 is a PSX.EXE string
  at 0x1747B4 (outside EXE_REGIONS, found in a VRAM dump: `warp.py hub_map --lua tools/lua/dumpram_at.lua --var
  DUMP_AT=11150`, render the .vram.bin as 4bpp to read the text engine's drawn labels), now "Peace" in
  asm/font.asm (in game: hub_map post.png). Other text-engine labels in that VRAM dump were all English already.
  Final build sha1 3d1fdaab83968d72f059a02d19037ad7c71f6680. Worker 7 (2026-11-21): TTL_OPT/TTL_OPT2/TTL_INFO PSS done. They are 4bpp 256x256 (the
  old "8bpp 128" note was wrong: bytes 0x01/0x10/0x11 are nibble pairs; on screen the glyphs are 12 px), the GDATA
  LZSS form. gfx.py: `gfx/TTL_*.tsv` = TITLE/<name>.PSS (kind `pss4`), recompressed with the new
  `lzss.compress_optimal` (optimal parse; greedy overshot TTL_OPT's 3 sectors) and zero-padded to the file's own
  size (`insert.edits`, fitcheck allows the whole file within its sectors; tests in test_gfx.py). In game: Slime
  Ball help box (TTL_INFO) English, `warp.py minigame` f12450. TTL_OPT2's blue box and the TTL_OPT memory-card
  notice checked as images only (new scenes `option_omake`, `option_exit` (card in) never show the notice).
  Build sha1 977636daac6dcecc5422345eceddf9b6f5690711, check ok, smoke ok, fitcheck ok. Done 2026-11-20 (worker 3): (a) credits: the FIN `%` line code
  froze the roll after "Backgrounds" (found by `warp.py credits_roll`, 13000 frames); painter rows now one name per
  line (`|` in `trans/staff/en.tsv`), roll verified to the closing cards (`work/qa/p8/cred_fixed.png`,
  `cred_card.png`). Review #5 is fully done. (b) graphics pipeline: `tools/gfx.py` + `gfx/eNNN.tsv` (rect, ink,
  shadow, jp, en; 4bpp LZSS images redrawn in place with en6x12 set proportionally; `insert.edits` and fitcheck
  wired; `tests/test_gfx.py`). Worker 4 (2026-11-21): status screens done. Their labels are the 8bpp TIM
  backgrounds e012 (fairy) e013 (angel) e014 (hero), found by a VRAM dump (`--lua tools/lua/dumpram_at.lua`);
  `gfx.py` now also redraws raw 8bpp TIMs, columns `x y w h font ink shadow bg align jp en` (`bg ink` = erase only
  the ink pixels by row inpainting, for textured panels; font `label` = `fonts/label14.txt`, DejaVu Sans Condensed
  via `tools/labelfont.py`, docs/fonts.md). In game: `work/qa/warp/hub_ability2|3/f010950.png` English; the hero
  screen (e014) is checked only as an image (`gfx.py png 14`): week2.mcd's third character is a fairy
  (`hub_ability4`), a card with a hero is needed for it. Sex value 男/女 = PSX.EXE 0x80183FA4, one cell shows on
  screen, now "M"/"F" (D15). e009 is still not seen anywhere. Build sha1 268ff21f3676ed8acb2808c53395b758483ca4be,
  fitcheck ok, check ok. e008 buttons done too (upper case, `work/qa/warp/hub/post.png`; 月 on the calendar -> "/").
  e142 week-screen fairy panel done (`work/qa/warp/week1/f011250.png`; gfx.py handles 4bpp TIMs, font `narrow`).
  Worker 5 (2026-11-21): name entry done. `asm/name.inc` (`text.md` §Name entry): Latin page first with pair-code
  letters, default "Raviel", 10 letters drawn 8 px apart, packed two per halfword on commit (verified by
  `tools/lua/peek.lua`: week screen shows "Raviel"; `warp.py newgame_name10` stores `Ra vi ww ww ww`); e015 page
  buttons Katakana/Hiragana/ABC (`gfx.py` bg `>=N`); new scenes `newgame_grid`, `newgame_name10`. Also e145
  memory-card panels (in game: `load_list`, `hub_save_list`), e243 status stamps and e143 MIA/KIA icons (images
  only; narrow font now has the capitals they use), D16. e144: logo kana kept (Waiting on the user). Build sha1
  bdde2b23ea6f22f8b905a7ed6fe1ac3934b9a2e1, check ok, smoke ok (name-entry build). `tools/lua/peek.lua` logs RAM
  halfwords per frame. Name entry left: odd-length names still end in a pair with a space (the old "Tia 's" gap).
  Worker 6 (2026-11-21): tutorial charts done. e203 (outlined lettering, small boxes widened by `copy` rows; image
  only: the "2. See the overall flow." choice, PSX.EXE 0x80166390 via pointer 0x80169798, is not reached by any warp)
  and three charts that live OUTSIDE the GDATA directory: `tools/timscan.py` sector-scans GDATA for TIMs (~800 not in
  the 423-entry table: event pictures, portraits, face parts; all looked at, survey note in graphics.md); sectors
  40127/40203/40279 = ゲームの流れ 其の一/二/三, shown by the SETUMEI event, now English in game
  (`warp.py ev_setumei`, `work/qa/warp/ev_setumei/f013800.png`). gfx.py: `gfx/sNNNNN.tsv` sector images, shadow
  `oN` (outline), bg `i:A,B[@dx,dy]`, `lum:LO,HI,D[,teal][@dx,dy]` (diffuse refill over paintings), font `label2`
  (double width for 640 hi-res), `copy` rows, en `-` erase-only rows; tests in test_gfx.py. GAME OVER pictures
  (sectors 15228/41039/41115, ゲーム・オーバー kana under English) left: unreachable. Build sha1
  27c9047bedcb52d885d3aa338b7ff4c94c76b735, check ok, smoke ok.
  **Next:** (3) below (tours, visual QA, inkbox, stress saves, textcover). e204-e206 done (worker 8). Old note on e008 buttons (予定 訪問 能力 地図 スカウト システム 戻る 任務 会話 贈る; 月): ink 15 on fill 5, no shadow, text
  area x 10-47 y 91-99 per button; gfx.py needs a `bg` column (it clears to 0 now). Proposed: Plan Visit Status Map
  Scout System Back Mission Talk Gift. Build sha1 ac73a4b73fb8f746817a2bf7067a44b525be7970, fitcheck ok.
  Older, worker 1: review #5 PSX.EXE part. Grown list
  strings (places, items, ranks, mission titles) now move to 0x80125500-0x80125AF0 with their pointer-table entry
  repointed (`insert.exe_text` REPOINT, `extract.table_pointers`, test `test_grown_exe_string_moves`, fitcheck allows
  it); `exetext.py check` lets a list entry grow up to 2 letters per cell of the list's widest Japanese entry
  (`exetext.LISTS`; places 14, items 16, ranks 12, missions 16). 39 strings moved, no short forms left except
  "Jr. X" (準X翼宮, 13 letters needed) and "Mt.X"; 盗賊・闇馬車 is "Dark Carriage". In game: rank "Chief Seraph" drawn
  from the moved copy on the status screen (`work/qa/p8/rank_chief_seraph.png`). Build sha1
  6ba5501e280b1ff1827293805e82f59328a35850, fitcheck ok, check ok, smoke ok.
  **Next, in order (after worker 3's next above):** (1) done (credits, worker 3); (2) graphics text (D5): finish
  the pilot (status-screen labels, source unknown, see above), then the rest of
  `docs/re/graphics.md`; new, not in the survey: 平和度 in the world-map coordinate box (`warp.py hub_map`, likely
  the 8x8 font e204-e206 or a sprite); (3) tours of every scene in `tools/debug/scenes.tsv` on the English build
  (`warp.py --all --cue build/favorite_dear_en.cue`; NB the default cue is the Japanese disc), `qa_gate.py init`,
  visual QA by a fresh read-only pass, `inkbox.py` on choice/centred boxes, stress saves, textcover. Visual QA
  costs ~1-2k tokens a sheet: about 40 sheets per worker context.
  Phase 7 done-when met 2026-11-20 (build green, batch checks and
  lint clean, fitcheck/romdiff clean on all 7 edited files). Carried into phase 8: the glyph-soup files (see below:
  all 20 SMxxK/SWxxK files plus T01SEN2, S_EV_01 and the SS..T/SY1205/SW021 parts use an older script header
  (argtab 0x1AE/0x1B2, not 0x1D2) and are not in the 462-name event table; a load log (`tools/lua/loadlog.lua`) over
  19 warp scenes (`warp.py --all ... --debugger`, stopped by the host for low memory) loaded 53 names and none of
  them: likely unused leftovers, confirm with a full sweep (-j 1) before release; `jp_left.py` must list them as
  intended); 3B77.0260 save menu; ending narration check; odd-length name gap. Phase 7 log: full English build green (2026-11-20): every batch inserted; 9 scripts that
  outgrew their slot (3529 354D 3551 3555 3634 368F 3964 3A3C 3ACC = SQA07 MYH16 MYH17 MYH14 T1001 S0404OK T9SEN
  TM02001 SMEN11) move to the end of GDATA.BIN with their (sector, size) entry repointed in all five EXEs
  (`insert.event_edits/repoint`, test `test_grown_script_moves`); `tools/fitcheck.py` (romdiff of every edited file
  against derived allowed ranges) runs after each build: all 7 files ok; smoke ok; `warp.py myh16` (a moved script)
  plays in English. Left in phase 7: the content items below (glyph soup, tables, name gap). Phase 6 done 2026-11-20: all 144 batches check OK, glossary updated,
  review pass b001-b144 recorded in `docs/review.tsv` (b057-b144 by 11 read-only Explore/Sonnet reviewer subagents,
  as codex is out of credits and the plugin reviewer type is not offered; reports' Important findings fixed: 12 batches
  `fixed`), `docs/polish.md` all ticked. Phase 7 work list: "Phase 7 items already known" below, plus the glyph-soup
  files, mission-title/rank/clear-data tables, and the never-built b006-b144 text.
- **Phase 6 review (`.harness/reviews/favorite-dear-en-phase6.md`) fixes, 2026-11-20:** done: #1 Critical D1
  honorifics applied (D12, 404 rows, `tools/honorifics.py` + lint in `batches.py check`), #2 "Beasia...-dono",
  #3 Gabriel now "Gabriel-sama" everywhere (no gendered title left), #4 Yaruru お姉ちゃん branch "Big Sis" (D13),
  #7 `docs/synopsis.md`, #8 fiend of flame, #9 via D12, #10 D14. Build sha1
  d5754504214f96b3cf84d6f2b94d4d6f2383aa93, fitcheck ok, smoke ok. **Open:** #5 (PSX.EXE part done in phase 8,
  see Phase; credits part left): give the PSX.EXE short forms full length (glossary "PSX.EXE strings": Mts., R., I., Ct., Jr.Angel, HiX, Studs; Japanese
  left at PSX.159B88 盗賊・闇馬車) by repointing to free space (pointer finder first: 78 rows have no direct
  pointer; `hub_help` test shows the repoint), measure each window's width in game, and give the credits'
  painter lines STAFF.289-292/345-347 and initial-cut names full length (FIN pair-glyph hook, `text.md`
  §Credits, 28 letters); whatever must stay short goes to the user (list under Waiting on the user). #6: codex
  reviewer pass on b014-b056 when codex is back (2026-11-26; probed 2026-11-20: still out). #11: the Explore
  reports' waived Minor ids were never saved to disk, so they can't be listed (note kept in polish.md). In game
  check owed in phase 8: odd-length `{name:0180}-sama` (half-cell gap "Tia -sama").
- **Builds (2026-11-20, phase 8 EXE repoint):** `favorite_dear_en.bin` sha1
  6ba5501e280b1ff1827293805e82f59328a35850, smoke ok, fitcheck ok. Marker/ruler/torture builds as in phase 5.
- **Glyph-soup files (found 2026-11-20, phase 7 must fix):** 34F2 34F5 34F8 34FC 3500 3504 3507 350A (all rows,
  ~300) and parts of 393D, 3976-3986 decode as kana/kanji soup under `tbl/jp.tbl` (codes parse; a substitution,
  likely a per-scene glyph set). Batched as `-` (b009-b013); find their table, re-extract, re-batch, translate.
  Glossary "Decisions from earlier batches" has the detail.
- **Update 2026-11-20 (phase 7):** the mission-title rows and the rank row 3B2F.1100 are lists read by op 0xDE
  (handler 0x800CB770: walks the row counting FFF0 separators up to FFFC, copies line N into a name slot, e.g.
  `DE 8002 <ref> 3` in AN/ITEM; `DE 8007` in BS3OK), so they are now translated line for line (same `{n}` count;
  ranks expanded from the EXE short forms). The gift-name row 3498.1550 is the same kind of list (`DE 8002`), now
  translated with the EXE item names. `warp.py epilog_end2` (20000 frames) ends inside the ending movie, before the
  narration: the epilogue check needs a longer run (phase 8). In-game check still owed (events AN, ITEM, BS3OK, SQA0Q are not loaded
  by id, so `warp.py --event` cannot reach them). 3B77.0260 (END11_2, EPILOG save menu) stays Japanese until an
  ending's save prompt is checked. Older note:
- **Mission-title tables 3AD6.2C44 (b130), 3B01.0CEC (b134) and 3B05.1212 (b135), left `-`:** one `{fc}`-wrapped row holding every mission title
  (盗賊・闇馬車, タンブール教会襲撃, ...) run together with full-width numbers as fillers for unused ids. The game
  must index into it some other way (no row cuts), so lengths cannot change until phase 7 finds that index; translate
  it then. Same for the angel-rank title table 3B2F.1100 (b137: 天使見習い幼翼天使準翼天使..., no fillers) and the
  clear-data save menu 3B77.0260 (b143: 21 fixed lines, はい/いいえ columns, slot names glued as スロット１のスロット２の).
- **Ending epilogue narration 3B6B-3B76 (b142-b143):** one row per hero, a fixed line per `{f7:0080}`, and lines
  holding only `〔` (glyph 0x0E) between pages. English keeps the same line count and the `〔` lines (passed through
  as raw `[0E][00]`, `batches.py` FULL), each line at most 40 letters. Phase 7: check one ending in game (does 0x0E
  still act as the page marker with the English font, and do 40-letter lines fit).
- **Pilot (done 2026-11-20):** `warp.py myh16` on the English build (`work/qa/warp/myh16/`, f015540, f015720): Reiv's
  scouting in English, wrap at 40 letters gives clean 3-line boxes, no overflow, continuation pages fine. The warp's
  angel name is the Japanese default ラビエル (phase 7: English default name). Choice box (b001 3498.1CF0) not yet
  seen: no warp reaches it (event name unknown). Voices: `docs/style-reference.md`.
- **Phase 6 set-up (done):** `tools/wrap.py` (simplify JP for translators, re-wrap English at 20 cells/40 letters,
  continuation pages `{n}{wait}{clear}{spk}{n}`, odd-run space fix), `tools/batches.py split|check|merge|todo`
  (families: identical rows translated once; `-` = not text; choice glyphs `　｛｝` -> raw escapes),
  `tests/test_wrap.py`, `docs/translator-brief.md`, glossary names (D10), decisions D10/D11. Batches:
  `trans/batches/b001-b144.tsv` (6459 entries from 10023 event rows), outputs `trans/en/bNNN.tsv` (the source of
  truth; `merge` rewrites `script/events/*.tsv` `en` from them).
- **No helpers available:** `codex exec` is out of credits until 2026-11-26 and the plugin's translator agents are not
  loaded in Orca workers, so each worker translates batches itself (about 1-2 batches per worker context besides
  set-up; more if it skips set-up reading). When codex is back, dispatch translators/reviewers through it.
- **Next (phase 6):**
  1. Choice box check (b001 row 3498.1CF0 `　｛Go to them　　　｝`, file 3498) once a warp reaches it (find the event
     name via the 0x8003B680 lookup). SS1204 is not file 349C.
  2. Event batches: done 2026-11-20 (b001-b144). Notes kept for re-batching the glyph soup in phase 7: translate per `docs/translator-brief.md` and
     `docs/style-reference.md`, check, merge, commit after every batch or two. Use `tools/compact.py show|soup|expand`
     (brief item 6): it cuts read/write tokens by about a third, and `soup` pre-fills glyph-soup rows as `-`.
     b026-b033 are recruit/re-recruit scenes and hero story battles; many files exist twice (one per angel gender,
     e.g. 358B/35BC, 3591/35B6, 3585/35C2), so pre-fill from the twin: a scratch helper `work/tx/reuse.py bNNN`
     (gitignored; copy it from the b028-b033 session if missing: it splits each row on control codes, maps every
     JP text piece already translated to its EN piece, writes `work/tx/bNNN.pre` in compact form with unknown pieces
     marked ⟦, and reads extra pieces from `work/tx/manual.tsv`). Check its "he'd/she'd" picks in the stock fairy
     line. Worth turning into `tools/` if the next worker finds it useful. Then `docs/synopsis.md`.
     Pace: one worker context did 17 batches (b017-b033) with compact.py + reuse.py; the next did 13 (b034-b046).
     b037-b046 are the per-hero mission offers (`{fb:..}` files, accept/refuse per hero; voices in
     `docs/style-reference.md`). After writing `work/tx/bNNN.en`, `python -X utf8 work/tx/prefer.py bNNN` swaps in
     rows that `reuse.py` filled completely, so repeated lines match earlier batches word for word (gitignored
     scratch: it only replaces rows with no ⟦ left; `batches.py check` still catches code slips).
     Story facts (b034-b036): Sterens usurped Fangam (Apollyon's monster); Beasia's father was possessed by a Fiend;
     Rasuel's double was Belphegor, the real Rasuel died in the demon world; Gaap is the chief fallen angel; Barnes is
     the fairy world's guardian beast (Sylphe saved Tia's life).
     Story facts learned: Miraya is Felimi's elder sister (Duminas army); Rush is the sacred beast Jackhound who
     killed Yaruru's father Ludock; Regal (Knight in Black) is Reiv's friend; Adramelech burned Sievas's town 15 years
     ago; Apollyon killed Fiana's parents; Dian's lost love is Liza.
  3. Done 2026-11-20: `script/exe.tsv` via `tools/exetext.py` (816 families in `trans/exe/batches/x001-x007`, outputs
     `trans/exe/en/`; every string fits its in-place slot, so names and labels are short forms, glossary "PSX.EXE
     strings"; `-` kept Japanese: mission title PSX.159B88 盗賊・闇馬車 (Dark Carriage does not fit 12 letters) and
     the offset-indexed field rows PSX.166398/1663C4). Credits via `tools/stafftext.py` (`trans/staff/en.tsv`, 14
     letters; long names take an initial; the two-name painter lines STAFF.289-292 and 345-347 stay Japanese as no
     family-name pair fits; STAFF.459 ＮＥＣインターチャネル stays). Staff name readings are my Hepburn guesses (see
     Waiting on the user). STAFF.TXT grows 4162 -> 5056 bytes: check the roll in game (`warp.py credits`). Not done:
     `script/sjis.tsv` memory-card titles (no insert path yet; phase 7).
  4. Review pass (done 2026-11-20; b014-b056 self-review, b057-b144 Explore/Sonnet subagents with
     `work/qa/review/reviewer-dispatch.md`; rulings added: 地上 "on earth" without article, "fiend" lower case,
     "Lord Remiel", Yaruru お姉ちゃん stays neutral (style-reference aligned to the glossary)). Original notes: `python -X utf8
     tools/pairs.py` writes `work/qa/review/pairs/bNNN.txt` (JP/EN per entry, codes stripped, boxes already shown in
     an earlier batch dropped: 2.0 MB, about 9 KB of JP+EN per batch). Read each with Read `limit` (60-120 lines; the
     context-mode hook refuses whole files over ~10 KB), judge accuracy/voice, fix Critical/Important in
     `trans/en/bNNN.tsv` (Edit), `batches.py check bNNN` + `merge`, record `bNNN<TAB>ok|fixed<TAB>note` in
     `docs/review.tsv`, Minors as `- [ ]` lines in `docs/polish.md`. Done b001-b013 (one fix: b009 34EA.08AA meaning
     reversed); resume at b014. Pace: about 13 batches per worker context; quality so far is high (no Critical).
     Automated scan (doubled words, tail fragments) found nothing real.
  Phase 7 items already known: odd-length runtime names (`{name:0180}` "Tia") leave a half-cell gap before the next
  text ("Tia 's"); re-pair in the name-insert path or pad names. Row 3498.1550 (gift-name list run together, cut by
  the script at offsets) kept Japanese until its indexing is found. script growth past a file's slot (159 files at 2.5x English length) needs GDATA
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
- **Waiting on the user:** (not blocking) abbreviations: the PSX.EXE ones are gone (phase 8 repoint: "Balgador
  Range", "Primse River", "Barba Isle", "Court Angel", "Chief Seraph", "Gigas Earring", "Dark Carriage"); left are
  "Jr. Power".."Jr. Seraph" (準X翼宮: the rank box holds 12 letters, "Junior Prince" needs 13). Say if "Jr." is
  fine to keep. The credits have no short forms left (FIN pair-glyph hook, phase 8). (not blocking) Honorifics: D1 is now applied in full (D12: "Sievas-sama", "Tia-san",
  "Griffin-dono"); say if you'd rather have English titles. (not blocking) the credits romanize real staff and cast names from kanji by my reading
  (`trans/staff/en.tsv`, given name first, Hepburn); given names that were initials until phase 8 are guesses too:
  新千恵子 "Chieko Atarashi", 戸北宗寛 "Munehiro Tokita", 龍谷修武 "Osamu Ryutani", 萩原由乃 "Yuno Hagiwara",
  富沢泰光 "Yasumitsu Tomizawa", 高橋佳子 "Keiko Takahashi", 本多柚々 "Yuyu Honda", 角田早穂 "Saho Tsunoda",
  藤田顕史 "Kenji Fujita". Corrections welcome; the build works either way. (not blocking) The kana reading
  フェイバリット・ディア under the English FAVORITE DEAR logo (GDATA e144 background watermark, TITLE.PSS,
  TTL_LOGO.PSS) is kept as part of the logo under D5; say if you want it removed. (not blocking) D16: save-list hero
  icons read MIA/KIA (11x10 px), status stamps POISON..PARALYZE, name entry keeps the kana pages.
- **Open bugs:** none from players; tour issues are under Phase (open sheets).
