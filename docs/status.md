# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **2026-11-24, v1.2 (D23): issue #8 fix.** PR #9 merged (8a28a45), #8 closed. `release.py --version 1.2` exit 0
  (tour gate waived for hotfix build edbb98a1): patch sha1 a0bc8c66..., image CRC32 E2FEEA42. Notes ready; the
  GitHub release is run by the user (the guard hook blocks `gh release create` from a worktree session).
- **2026-11-24, issue #8 (released in v1.2): two choice options on one line.** SLOVE01-12 ("Promise to stay" /
  "Can't promise", the hero asks the angel to stay before the last battle) drew both items on one line under one
  cursor bar. Cause: `wrap.simplify()` drops the JP `{n}` between `｝` and `｛` as soft, so translators wrote
  `｛A｝｛B｝` and `wrap()` packed them. `wrap()` now starts every choice item on its own line; `batches.py merge`
  fixed 27 rows (SLOVE01-12, SS0202 3964.*, SS0202T 396D.*: three also had an item split mid-text). Lint
  `test_no_two_choice_items_on_one_line_in_the_script`. Verified: `warp.py ev_slove01` before/after
  (`work/qa/warp/slove01_dense/f014730.png`: two lines, bar on line 1); SS0202's mash path skips its menus
  (lint only). check ok (94), smoke ok, build sha1 edbb98a1.

- **2026-11-23, v1.1 published (D22).** Bug-fix release with issues #1 (gift window Japanese), #2 (Equip box names),
  #4 (topic-menu overflow); #5 (player on v1.0: gift window + two Ashe visit options, 3535.40CA / 3535.564A) was
  the same two bugs, already fixed on main. Reporters credited in README.md (Thanks), README.txt (Credits, plus a
  Changes section in `tools/release.py` README_TXT) and the release notes. The "two status-label strings still
  Japanese" caveat is gone from both READMEs (they were the gift-window rows).

- **2026-11-23, issue #4 (released in v1.1; PRs #6/#7 merged):
  hero-visit topic menu cut options off.** The visit menu (`00D4` + op 0x90 per option) prints each option row's
  first page as one menu line with a one-cell cursor indent: one line, 19 cells (JP options are at most 19 glyphs).
  wrap.py allowed 20 cells and 2 lines, so 302 rows (45 distinct lines) overflowed ("...I'll hel", "...lost your way"
  without its ".", two-line options pushing the next one under the wrong cursor slot). Shortened all 45 in
  `trans/en` (fixrows + merge); new `tools/menuopts.py` (option rows from the scripts, overflow lint) and
  `tests/test_wrap.py::test_hero_visit_choices_fit_the_menu`. Repro: `warp.py --event SQA04 --state`, then emu.py
  `--state-in work/states/sqa04_*.sstate --shot-every 10`: the menu is up ~200 frames after the state; new
  `tools/lua/setmenu.lua` forces the second option's key (`--var MENU_B=0x64`; slot 9 is already fixed by then).
  Verified on build 2e77b172 against the v1.0 build: "...I'll hel" -> "If I can do anything, I'll help.", the
  two-line scenery option now one line (`work/qa/issue4/*_old_vs_fix.png`); check ok (93), smoke ok.

- **2026-11-23, issue #2 (not released yet): hero status Equip box showed no item names.** PR #3 (issue #1)
  merged first. The names were drawn by 0x80110E58, a small-kana cell copier with no Latin (docs/re/text.md §Hero
  equipment); worker 20's "the hero screen draws none" was wrong: its save had nothing equipped. Fixed by
  `asm/equip.inc` (D21, the user's choice): names in caps4x7 capitals from x 77, labels moved to x 25,
  `tests/test_equip.py` checks every equippable name fits. Verified on build 5132f613: `warp.py stress_hero_reiv
  --cue build/... --lua tools/lua/setequip.lua` (new: holds the widest names) shows BATTLE BOOMERANG / KNITTED
  SWEATER / MERMAID EARRING inside the box (`work/qa/issue2/after2_vs_empty.png`); empty slots clean; fairy status
  (`hub_ability4`) and battle plates (`battle_t0101`) unchanged; check ok (92), smoke ok.

- **2026-11-22, issue #1 (not released yet): hero-visit GIFT window was Japanese.** The item stat window
  (装備不可 / 攻撃力 防御力 素早さ, アイテム / 体力 正義感 ストレス) and the 贈りますか？ prompt came from the two
  jp_kept rows PSX.166398 / PSX.1663C4. Their "unknown field layout" is now mapped (docs/re/text.md §Hero visit GIFT
  window): sprite descriptors at 0x8002DA34 cut them from a VRAM strip, so `asm/gift.inc` repoints u/w and the rows
  are English in exe.tsv (removed from docs/jp_kept.tsv). Reproduced and verified on the EN build with the new scene
  `warp.py stress_hero_gift --cue build/... --lua tools/lua/giveitems.lua --var ITEMS_AT=12000` (the heroes save has
  an empty bag; `tools/lua/giveitems.lua` fills it): "Equip: No/OK", Attack/Guard/Speed, Items/Stamina/Justice/Stress,
  "Give this?"; "Equip: Using" (already equipped) checked by forcing state 0x8002801A = 2 (not reached naturally).

- **2026-11-21, after v1.0: name-entry crash fixed (not released yet).** A player on DuckStation froze when the name
  grid opened (state `rom/fav_name_input.sav`). Cause: `asm/name.inc` name_latin had `lw ra` right before `jr ra`;
  with no load interlock the `jr` used the old ra, ran the epilogue twice and resumed the task with sp 8 bytes off
  (unhandled RI exception at 0x8001009C on DuckStation; PCSX-Redux survived it by luck, `tools/lua/namelatin.lua`
  shows the double pass on v1.0 and one pass now). Fixed, plus `tools/asmlint.py` (load-delay lint over asm/, in
  check.py via tests/test_asmlint.py; no other hazard). `tools/dsstate.py` reads a DuckStation .sav (RAM, shot,
  crash registers). New build sha1 0e1a75b3f65286b31f51d09cb6fac00de03c2d4a: smoke ok, check ok (91),
  `warp.py newgame_grid/newgame_name10 --cue build/...` ok with no CPU exception. Released as v1.0 (owner's call,
  replacing the unpublished v1.0 zip): `tools/release.py --version 1.0 --force` exit 0, tour gate waived for this
  hotfix build; xdelta sha1 92f4de4612efbdbfa07a92dc57ca43a220f3dd36 (1425096 bytes), re-apply = 0e1a75b3. Published
  on GitHub (repo made public, release v1.0). Note `warp.py` defaults to the original disc: pass
  `--cue build/favorite_dear_en.cue` to test the patch.

- **Phase:** 9. Release done 2026-11-21 (worker 29): `tools/release.py --version 1.0` exit 0, every gate passed;
  `release/Favorite_Dear_EN_v1.0.zip` (xdelta 1425091 bytes, sha1 a82e8216c819bcb8148ddc53639f9c32b4b705f0, + README.txt),
  re-applied to the original = build sha1 858ac985b50a46d3166a8c18e281045f84af7697. Publishing (`gh release create`)
  is the owner's call. Ad-hoc warps `--event SS1102:11` / `S0705OK` did not reach their scenes (not needed: the tour
  gate is waived for this text-only build with the static checks). Phase 9 work: story pass, all 17 chapter files
  (`tools/pairs.py --chapters`, chapters from `docs/synopsis.md`, split at batch boundaries above 160 KB;
  `work/qa/story/`: brief.md, manifest, verdicts; Explore/Sonnet read-only reviewers since codex is out until
  2026-11-26). Important fixes: 358B.2332 and 3802.12A6 Yaruru "Big Sis" (D13), 36BB.07DA Ryudral "Took you long
  enough", Nasadia 天使サマ -> "my dear angel" on her teasing rows (38A0, 38A6, 39FB), gift-choice callback quotes
  "Since you offer" (3A84/3A9A/3AB1). A ch06a "Critical" (Opponent: label on Nasadia's lines, 3899.14D0) was false:
  the EN already drops it. Minors: fixed or waived in `docs/polish.md` (all ticked). New `tools/jpcheck.py`
  (leftover-Japanese gate: rows + jp_left on STAFF.TXT and the PSX.EXE row spans; kept-on-purpose rows in
  `docs/jp_kept.tsv`: two offset-indexed label rows PSX.166398/1663C4, name-entry kana grid, two memory-card
  titles), new `tools/release.py`, README filled (hashes, status table). Visual-tour gate waived for this text-only
  build (see below). Phase 8 summary: done 2026-11-21 (worker 28, build unchanged 94fa9887): `textcover.py
  work/qa/force work/qa/force_build/strings.tsv --waive docs/text_unshown_unloaded.tsv` exits 0 (8633/8824 shown,
  191 waived, 0 failing); `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` exits 0 (277 sheets); check.py ok
  (79). **Phase 9 to do:** story-pass verdicts per chapter, `docs/polish.md` unticked lines, release script running
  both gates + `jp_left.py`, debug tool off, patch build/re-apply/verify, README hashes, zip = patch + README.
  Run textcover against the frozen strings (`work/qa/force_build` is da7916e8 text; coverage is by row id).
  Worker 28: the 38 left -> 0. MAPSYS 20/20 via new textforce.lua `ENTRYGO` + `EG_ID=150` (goto into each news
  case / game-over branch, patched while the EXE holds the file under id 150, before event 32 runs it; passes
  p21-p43); SS1106 8/8 (NOBATTLE now also skips jumps/gotos to an `00BF 00C0 0037` end block); TM0312A 3/3
  (`--hero 3 --keypatch --var STARTPATCH=1`); T0204 "ran away" (`ENTRYGO='0x53:0x19D'`, the battle-result
  switch); SS1202 1/1 (`--choices --keypatch`, works since the SIG fix). Waived with proof in
  `docs/text_unshown_proven.tsv` (merged into the gate file by `textcover_map.py strings --waive`): SS0507's 4
  rows (its code is `goto entry; end`) and SW11 "Dummy" (drawn, but runs on into the next row on one page, so
  the printer index never lands in it: `docs/screenshots/sw11_dummy_shown.png`). Commands: textforce.py docstring.
  Earlier phase 8 summary (worker 27): only textcover was left, 38 of 8638 rows unshown in 7 files.
  Worker 27 (2026-11-21), build unchanged. Pass 9 finished (574 -> 217), passes 10, 13, 14 (same options, new
  `ROT_SEED`) -> 63; pass 14 gained nothing. **New `textforce.py run --choices`** (lua `FORCECHOICE`): unshown
  choice-menu rows become ordinary targets that KEYPATCH/PRINTPATCH point the scene's lookups at (SMEN06 3/3 in one
  run); pass 16 (`--choices`, no RECHOICE) 62 -> 39, pass 18 -> 38. Passes 11/12/15/17/19 are single-file tests.
  **Left (all "forced 0": the hook never sees the printer in them):** MAPSYS 20, SS1106 8, SS0507 4, TM0312A 3,
  SW11 1 ("Dummy": case 2 of the `006F 0011 8002` switch at JP pc 0x42, `003C 8CEB` at 0x73; not proven
  unreachable), T0204 1 (battle "ran away"), SS1202 1 (choice). Rows: `work/qa/left_rows.txt`.
  **MAPSYS** (world-map news: hero lost/kidnapped, Gabriel bonus AP, 3 game-over lines): entry `007E 8002` reads the
  news id the EXE passes, a `002B 8002 N <stub>` table picks a `003C <row>` print. Found: TARGETS row spans ran to
  the next row's start, so the `003C` sites between inline messages counted as text; PRINTPATCH now measures each
  row to its 0xFFFF (27 sites patched instead of 4). Still 0/20: the scene's own news (rows 22-28) is already
  printing when the file is first seen (f13462 load, f13487 row 22 at +45), so the patched sites never run in that
  visit and the file leaves at f14044. JUMPFORCE (debugger) stalled at f6000 for 25 min (killed). Next idea: a
  warp.lua var that writes the news id the EXE passes to `007E` (find where, or patch `007E 8002` into a
  constant set before the file loads), one run per id; or waive the game-over rows with proof.
  **Phase 9 note:** `work/qa/force_build` (da7916e8 text) is older than the current build 94fa9887 (speaker-space
  edits since); coverage is by row id, so it holds, but phase 9 should run textcover against the frozen strings.
  **Found and fixed this session** (`tools/textforce.py` docstring, `docs/re/events.md`, `docs/re/debug.md`):
  TxxSEN are hero xx's battle lines: a battle with HERO=xx loads them (all 12 shown; T01SEN loads via warp.lua
  `SWAP` in a hero-3 battle). T-battles get HERO from their name (T0703 0 -> 10/10). SSxxyy run as `NAME:xx` with
  NOBATTLE (the battle op and its result end-jumps become gotos: SS0204 30/30). PRINTPATCH points every `003C`
  print at a wanted row and turns conditional jumps (0x2B-0x2F) into a wanted print into gotos (EVFUM, SQA "..."
  random roll, TITA 25/25). RECHOICE re-patches after each choice (SMEN01 10 -> 20 rows a run). MASH_ROTATE (warp.lua)
  presses 0-2 downs before each circle: battle "ran away" rows. TM files run as events (TM12ALL switches on the
  hero, `--hero N`; 31/31 with hero 1). **Bug fixed:** the slot table names a file frames before its data replaces
  the last one, so KEYPATCH patched stale words; now `SIG` (the file's own code words) must match first. Earlier
  passes were hurt by this, so re-running files that "failed" before is worth it.
  Worker 25 (2026-11-21), build unchanged. Pass 4 (same command, `--pass 4`, log `work/qa/force_p4.txt`) was
  killed by Claude Code for low host memory after 95 runs: 1182 -> **1098 left in 125 files (92 choice menus)**.
  Resume with the same command (finished runs are skipped) when free memory allows (-j 2 if under 4 GB free).
  Worker 24 (2026-11-21), build unchanged. (a) **Why forcing failed, fixed:** the printer index obj+0x10 moves a
  page at a time, so the hook first saw a row when its first page was already drawn, then "forced" it again; and
  re-pointing a running printer stalls it (docs/re/events.md). New `ADOPT` (`--var ADOPT=1`): never re-point a row
  the printer entered; credit it and let the {wait}-patched terminator flow into the next row. New `--keypatch`:
  files that print through op 0x90 (a message picked by its FFFB key: KAIWA, SxxOK, SY, SQA, SCQA, SMEN) get their
  0x90 ops patched on load to print the first wanted keyed row. KAIWA1 0/240 -> 240/240. **Pass 3** (`textforce.py
  run -j 4 --pass 3 --frames 40000 --mash 8 --keypatch --var SKIPKEY=1 --var ADOPT=1`, log `work/qa/force_p3b.txt`):
  ~91% of targeted rows shown, 5784 -> 1182 left in ~2 h. Pass 2 (old logic, 12% yield) was stopped.
  **Left, by family:** SMEN 469 (12 menu files: the run loops through the menu, mashing the first option, so rows
  behind the other options never play: next try pressing down before circle on a CHOICE, e.g. a MASH pattern
  that rotates the cursor per loop, or KEYPATCH-like patching of the menu's 0x3C/branch ops); T 328 (TxxSEN ~270:
  they park in op 0x82, a world-map wait; `--var STARTPATCH=1` rewrites the entry and moves the task pc (obj+0x12)
  there but the op does not release the task; find what 0x82 waits on, or waive with that proof); SS 198 (28
  battle-wrapper events: op 0xD3 starts a fight the warp shows black, their text comes after it); TM 52 (TM0312B
  and TM12ALL hang until the 3600 s timeout); SQA 43, MYH 26, MAPSYS 20, small rest. Next: pass 4 with the same
  command and `--pass 4` (each file uses its next event name), then the menu strategy above.
  Worker 23 (2026-11-21), build unchanged. Event pass 1 (`force_run3.txt`) finished all 309 files at 09:55.
  The battle runner (`force_battle.txt`) stopped at 09:26 after 71 files with no final line, probably the host
  running out of memory (Claude Code also reaped a watcher for low memory). `textforce.py left` is now **5814 of
  8638 rows unshown in 358 files (180 choice menus)**, down from 6759. Next: when memory allows, re-run the battle
  command (it skips finished files). Then do pass 2 on events with `--pass 2 --var SKIPKEY=1` at -j 2..4, checking
  free memory first.
  Worker 22 (2026-11-21), build unchanged (94fa9887, check ok 79). (a) **Throughput:** the old -j 1 pass-1 runner was
  killed and restarted as two runners on disjoint files (no collisions): events `textforce.py run -j 4 --pass 1
  --only $(cat work/qa/event_sectors.txt)` (log `work/qa/force_run3.txt`, 288 files left at 09:20) and battles
  `... -j 1 --pass 1 --only $(cat work/qa/battle_sectors.txt)` (log `force_battle.txt`, it had died after 16 files;
  restarted, 67 left). The memory kills were emu.py's output leak (fixed by worker 21): 5 emulators use ~1.3 GB, the
  host had 5.6 GB free at 08:50, but only 2.4 GB at hand-back with other projects' emulators up (9 PCSX on the
  host): check free memory before going above -j 4. Both resume with the same command (finished runs are skipped).
  `textforce.py left` at 08:50: 8005 of 8638 loaded rows unshown. (b) **Choice menus are printer rows** (the tour
  ev_smen01 run's PIDX maps to 3A76.13E0; op 0x90 is a message lookup by FFFB key, handler 0x800CB880, not a menu
  drawer). textforce now passes unshown choice rows as flag 2 in TARGETS and textforce.lua lets the scene's own print
  draw them (logs `CHOICE`), never redirecting into them: test run on SMEN01 logged 3A76.13E0 (key 3A761400). The
  battle runner started before this change (no flag 2: battles have few choices). Still unshown choice rows after
  the passes need scenes that reach them, or a forced-choice mode (untried). (c) Many forced rows SKIP because the
  scene's next print op re-points the printer within ~60 frames (`UNCHAIN 1 at 974 idx 1021`, S0402OK): the forced
  row never gets past its first code. Worth looking at next: hold the script (or redirect at the print op that
  follows a {wait}) so the forced row has time to draw. Partly found: most rows open with their `{fb:XXXX}` key
  (FFFB, looked up by op 0x90, which starts the printer after it); new `textforce.py run --var SKIPKEY=1` starts a
  forced row after a leading FFFB+arg: S0401OK/S0402OK went 0/6 -> 1/6 (row 2 now SHOWN). Use it on pass 2. Row 1
  of S0402OK still stalls (no PIDX for 60 frames after FORCE, then the script's next message): another cause.
  Worker 21 (2026-11-21), build unchanged (94fa9887, check ok 79, smoke ok). (a) **textforce battle mode:** the 83
  battle files (0x80174A84 table, `textforce.battles()`) now run as `warp.py --battle NAME` into
  `<root>/p<N>/bt_<NAME>`, with `FORCE_ID` = the battle's event id (its file loads under that id, not slot 32).
  T0102 test 3/7 shown (was 0). New `--rows ID,..` forces only those rows (a chain that stalls on row 1 never
  wraps to the rest). (b) **Battle pass running** into the main root: `textforce.py run -j 1 --pass 1 --only
  $(cat work/qa/battle_sectors.txt)`, log `work/qa/force_battle.txt` (started 08:45; 15 files in: 17 of 146 rows
  shown, low: many battle rows are win/lose/run or mid-fight lines that the printer never enters after 2 tries, so
  the probe SKIPs them, e.g. T0102 "ran away", "serves you right"). Next: once it ends, `textforce.py left`, then
  for battle rows still unshown try a longer run (`--frames`) or a win/lose hook; waive only with proof they are
  unreachable. Pass 1 (`force_run2.txt`, -j 1) is still going: 43 files done at 09:20. (c) **Sylphe/Gaap closed:**
  "Gaap: How could mere humans stop my plan...?" (`work/qa/speaker_space_gaap_f017640.png`, T00GAP) and "Sylphe:
  It's fine. I'm just really happy / that Tia has become such a fine hero." (`work/qa/speaker_space_sylphe_f016200.png`,
  T1205 row 2104, via `--rows`); both have the space and fit. (d) **Skill fix:** `$SKILL/scripts/emu.py` kept all
  emulator output in memory (`communicate()`); one PCSX run grew it to 5.6 GB, likely the earlier low-memory kills.
  Now a reader thread keeps the last 200 lines (docs/skill-gotchas.md).
  Worker 20 gate: stress_hero_* re-toured on 94fa9887 into `work/qa/tour`, `qa_sheets.py`, `qa_gate.py init --build`,
  9 new sheets reviewed in a fresh read-only pass by the worker itself (codex out of credits until 11-26; verdicts
  `work/qa/verdicts/w20_hero.tsv`), `qa_gate.py check` exit 0. stress_hero_week2 does not reach a hero column:
  heroes have no column on the week screen (right wraps to the angel); its scenes.tsv note overstates it.
  Textforce gap (worker 20, closed by worker 21's battle mode): battle files returned rc 1, shown 0 via `--event`.
  Worker 20 (2026-11-21): build **94fa988734a9eb9f0c0f6d12c913d87fdc89ba1c** (check ok 79, smoke ok). Skill names
  fixed (`asm/skill.inc`, `docs/re/text.md` §Hero skills, D20): rendered into the status text sheet with the Name and
  drawn by the rewritten 0x800C337C in the main font from x 200; labels now "1:".."3:" (gfx/e014.tsv). In game
  `work/qa/skillfix/stress_hero_{reiv,griffin}/final.png` (Reiv Rake / Spinning Raid / Ground Zero; Double Pain /
  Mega Crush / Aerial Shave); widest names via `tools/lua/longskill.lua` -> `work/qa/skillwide` (Double Boomerang
  fits). Equipment values: the hero screen draws none (no render of them in 0x80110FBC's hero branch, JP shows them
  empty too), so nothing to fix there. **The gate manifest's build is now stale** (every sheet was shot on ddee99dd;
  PSX.EXE and GDATA e014 changed only on the hero status screen): re-run `qa_gate.py init --build` after the hero
  sheets are added, waiving the rest with that reason if the gate demands a re-shoot. `work/states/stress_hero_reiv.sstate`
  is a JP-disc state now (worker 20 warped the JP disc with --state).
  Worker 19 (2026-11-21), build unchanged (ddee99dd). (a) **Hero stress save done:** `work/saves/heroes_w3.mcd` save 2
  (game-written, week 3, AP 207, heroes Reiv + Griffin). How: `tools/lua/scoutwin.lua` (new, debug only) rewrites
  the scout test `006D 0016 8002 0001 <yes> <no>` in the script buffer so every scout succeeds; play.py session
  `work/play/hero4` on the **JP disc** (a JP savestate with the EN disc prints soup) from `work/states/week1.sstate`:
  fairies hero search -> the week-1 action menu 訪問/スカウト/能力/地図 -> スカウト -> Reiv -> はい, same for
  Griffin; they join after the week (their own map/"where should I go" scene); end the action phase, System -> Save
  Data.2. New scenes `stress_hero_week/_week2/_ability/_reiv/_griffin/_save` (scenes.tsv, save 2). **Note:
  `warp.py` defaults to the JP cue: pass `--cue C:/.../build/favorite_dear_en.cue`.** Shots: `work/qa/stress_hero/`
  (EN build). Not yet sheeted/reviewed (`qa_sheets.py` + read-only pass + `qa_gate.py init/check`).
  (b) **BUG (open): hero status screen, Skill 1-3 are blank** (`stress_hero_reiv/final.png`; JP shows レイヴレイク..).
  Cause: the skill lines are drawn by 0x800C337C (only 3 callers, 0x8010F740/774/7A8): for each halfword it looks
  the code up in a 256-entry table at 0x80026E18 and draws an 8x8 small-font cell ((i&31)*8, (i>>5)*8+0xC8, 8 px
  apart); codes not in the table are skipped, so pair codes draw nothing. Strings: PSX.16641C.. (exe.tsv rows
  823-858, translated, offsets from the u16 table 0x8002DBFC = 3 per hero, unchanged and correct). Box room at x 0xE8:
  ~9 cells of 8 px. Fix options: hook 0x800C337C to print through the main-font pair path (the Name field next to it
  already shows "Reiv・Vincelras" in 6-px pair letters, so find that drawer and reuse it), or encode the names in
  the small font if it has Latin (then shorten to ~9 letters: needs a glossary pass). Also check equipment names
  (Weapon/Armor/Other: empty on this save, may use the same drawer) and the "・" between given and family name
  (glossary has no ・ rule; JP keeps it). (c) **Textforce pass 1 restarted** 07:40 (it had died): `work/qa/force_run2.txt`,
  404 files / 7376 rows left at start, ~2.3 min per file. (d) Sylphe/Gaap: `textforce.py run --only 365E,3A37
  --shot-every 30` (new option) on a fresh freeze `work/qa/force_build_spk` gave rc 1 for T1205 (battle events don't
  load through `--event`); a textlog hook in a `--battle` run is still the way.
  Worker 18 (2026-11-21): build **ddee99ddfefd466ad8c41083a7efcc7c9d9c1fcb** (check ok 79, smoke ok).
  (a) b099 merged (3943.1746), rebuilt; re-toured epilog_end14 (its old run had died at f900, no sheets) and
  epilog_end16-23 on the new text; `qa_sheets.py`, `qa_gate.py init --build build/favorite_dear_en.bin`, 6 + 1
  read-only Explore review passes (verdicts `work/qa/verdicts/chunk_f29d42123006_*.tsv`, `chunk_82e57efaa9a5_all.tsv`,
  `w18_recheck.tsv`). **`qa_gate.py check`: 268 sheets, 0 unreviewed, 0 not ok, exit 0.** name12_* are `fixed`
  (past the 10-letter cap). credits_roll/qa_sheet_7 closed: the same warp on the JP disc
  (`work/qa/tour_jp/credits_roll`) shows the same noise, then the box opens empty and a line types in, so it is warp
  state. ev_taiken closed (same in JP). Honest caveat: most sheets were shot on earlier builds whose text differs
  from ddee99dd only in rows those scenes don't show (b099 3943.1746; the speaker spaces below, only in
  epilog_end12, which was re-shot). (b) **Speaker space fix:** 6 pages print the speaker inline ("Tia:I wanted",
  JP does the same), now "Tia: I wanted" (b141), "Sylphe: " x4 (b037, 365E = battle T1205), "Gaap: " (b116, 3A37 =
  T00GAP). **Gotcha:** `wrap.wrap_for` drops a space *before* a code (`Tia: {f7:0380}` came out `Tia:{f7:0380}`),
  so put it after (`Tia:{f7:0380} I`). Tia verified in game (epilog_end12 f013050); `warp.py --battle T1205` /
  `T00GAP` (`work/qa/fix6/`, shots every 150) never caught the Sylphe/Gaap inline pages: re-run with
  `--shot-every 30` or a textlog hook if you want a picture. (c) **Hero stress save, still none:** a native MYH16
  run to 36000 frames (`work/qa/herojoin/`) ends on the week-2 screen with only the angel and two fairies; the
  angel's own actions are only Stand By / To Heaven. Joining goes through fairy hero search -> scout ("Go scout a
  hero you've found. Costs 10 AP", the SP01 scout menu VISIT/SCOUT/STATUS/MAP) over several weeks;
  `play.py work/play/hero` (from week2.sstate + week2.mcd; cross clears an action, circle opens the list) is set
  up for that. (d) **textforce pass 1 resumed at -j 1** (`work/qa/force_run2.txt`, started 07:00): ~2.3 min per file,
  ~415 files left, so ~16 h per pass at -j 1; if it died, `python -X utf8 tools/textforce.py run -j 1 --pass 1`
  resumes. 8493 of 8638 loaded rows were unshown before it. See "Waiting on the user".
  (e) Older worker notes (16 and before) moved to `docs/phase8_log.md`.
  Worker 17 (2026-11-21): build **3f8921bc14034ff2bb995434b7b9b3219c7a2f8f** (check ok 79, smoke ok), commit aa2e6c6.
  **Gate bugs:** (1) EPILOG slot labels: worker 16 had fixed them in script/events only and `batches.py merge`
  reverted it; now in `trans/en/b143.tsv` too. **Rule: edit trans/en (events) and trans/exe/en (EXE), then merge;
  never script/ alone** (the exe rows Slot 1/2 and the 1661D6 card text had drifted the same way; synced). (2)
  Week-screen actions: one leading space on all six (the list is one window: `exetext.LISTS` gained 0x1579FC-0x157A50);
  inkbox Stand By 13/12 (was 7/18), To Heaven in the middle box 12/8 (JP 5/9, same 4 px offset). (3) Save/Load box
  24/25 (was 18/31); scout Yes/No rows 297/298 (PSX.157FDC/FE8; the drawer skips the 4-letter "１．" prefix): Yes
  +1 space, No +2: hi-res bar now 28/18 (was 18/32; 1 space = ~10 px there, the closest step). (4) name12: **not a
  bug**: name entry caps at 10 letters (`asm/name.inc` NAME_MAX); the 12-letter card was poked past the cap; 10 W's
  fit. Give name12_week/_save a `fixed` verdict with that reason. (5) ev_taiken trial message above the box: **same
  in JP** (`work/qa/tour_jp/ev_taiken/f013500.png`: text above the box, line 3 under the border, ragged indent).
  (6) Zombie Trader everywhere (D18, glossary). Also: 3943.1746 now "(None: I've been captured!)" (b099, **edited
  after the build: run `batches.py merge` and rebuild first**). Decisions D18/D19 added. **Re-tour on 3f8921bc**
  (log `work/qa/tour_run8.txt`) was killed by the host for low memory at 07:00: done 38 scenes (hub*, load*,
  name*, stress*, ev_sp01/sy0101/syboss1, battle_t0301, epilog_end1-15); missing **epilog_end16-23**. After the
  rebuild those 38 are on the old build only by the b099 row (not shown in any of them), so: re-tour epilog_end16-23
  on the new build, `qa_sheets.py`, `qa_gate.py init ... --build build/favorite_dear_en.bin`, review the changed
  sheets (read-only passes), check. **Textforce pass 1** log has not moved since 06:32 (likely dead; `textforce.py
  run -j 1 --pass 1` resumes). **Hero stress save:** warping SY0101 (scout, Yes) and running 30000 frames back to
  the week screen leaves RAM 0x8001DC48+0xBFC and 0x8001E410+0x1000 unchanged and no hero joins (the patched-slot
  event does not run the join); next idea: find the join in a real week flow (Find Hero action from week2.mcd).
  Older phase 8 worker notes (workers 4-16: tours, textcover sweep, stress saves, fixes): `docs/phase8_log.md`.
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
- **Waiting on the user:** (not blocking, worker 18, eased by worker 24) textcover scale: a textforce pass now takes
  ~2 h at -j 4 and shows ~91% of targeted rows; 1182 rows are left (menus, world-map and battle-wrapper files).
  Default carried on with: keep closing them in game. Alternative for the owner to choose: waive the rest with
  `fitcheck.py` proof (static width check per box).
  (not blocking) abbreviations: the PSX.EXE ones are gone (phase 8 repoint: "Balgador
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
