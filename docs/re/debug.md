# Debug tool (phase 2): how the warp works

Entry point: `python -X utf8 tools/debug/warp.py SCENE` (scenes in `tools/debug/scenes.tsv`, `--list`), or
`--event NAME` for any event script, `--all` to regenerate everything, `--state` to also write
`work/states/<scene>.sstate`, `--cue build/favorite_dear_en.cue` for a built disc. Every run boots cold (no memory
card, no savestate) and drives the game with `tools/debug/warp.lua`. Output: `work/qa/warp/<scene>/arrived.png`
(the proof, 30 frames after arrival), shots every 150 frames, `sheet.png`, `log.txt` (`WARP OK <scene> f<frame>`),
and a line in `work/qa/warp/results.tsv`. Exit 1 if a scene was not reached, its proof shot is blank, or (AFTER=mash)
nothing on screen changed after arrival (a stuck script).

## Loading (verified: `tools/lua/loadlog.lua` with `--debugger`, week-1 run)

- `0x8003B680` name -> GDATA table index (names like `KANRI14.BIN;1`, or bare event names like `MYH16`);
  `0x8003B3D0 load_by_name(a0 name, a1 dest)`; `0x8003B63C size_by_name`; `0x8003F838` the disc read
  (a1 dest, a2 sector, a3 size). The GDATA tables at PSX.EXE 0x4C50/0x5988/0x60B8/0x62F8 are one table at RAM
  0x80014450 (pointer at 0x80016060).
- **Events are loaded by id**: `0x800C82E8 load_event(id)` copies the 9-byte name at **0x80173640 + 9*id** (the event-name
  table, 462 ids, `tools/events.py names`) and loads that file into the script buffer at 0x8016C608. Loaded events are
  listed at **0x8016C5B8**: 10 x 8 bytes (u16 id, u16 halfword offset into the buffer, ...); the buffer fill
  position is at gp+0x28EE, max 0x3800 halfwords.
- The opening (angel's briefing after New Game) is **not** an event script (no event load until week 1); its text is
  in PSX.EXE (`text.md`).

## RAM flags (verified by RAM dumps across screens, `tools/modefind.py`, `tools/ramval.py`)

| Address | Values |
|---|---|
| 0x8001A4A8 (u16) | 2/3 opening dialogue and name entry, 5 week screen idle, 9/0xB week-screen submenus and confirm, 1 transitions and world map, 4 event dialogue |
| 0x8001A654 (u16) | 0 before week 1, 1 week screen idle, 2/3 after orders are given |

Week screen ready = A4A8 == 5 and A654 == 1. No clean flag for the world map: the warp waits 450 frames after
A4A8 turns 1 once the orders are confirmed (no text in between, so the timing holds for translated builds).

## The event warp (verified: MYH16, SEND01, SM01 play their own text from a cold boot)

Cold boot -> title (fixed presses, no text yet) -> New Game -> circle every 20 frames through the opening until the
week-screen flag -> `tools/routes/week1.txt` presses (both fairies to hero search) -> circle every 60 frames. With
both fairies searching, the game's first event is MYH16 (id 32). Before that, warp.lua overwrites the name slot of
id 32 in the event-name table with the target name, so the game's own loader fetches the target script; arrival is
id 32 showing up in the loaded-event table. From cold boot to the event takes ~13,500 frames (~40 s wall clock).

## Hub and saving (verified from `work/states/week1.sstate`, shots in work/qa/ws)

- Week screen: cross twice (120 frames apart) leaves to the **hub** (the palace room, 640x240) with a right-hand menu
  予定 (schedule -> back to the week screen) / 能力 (abilities) / 地図 (map) / システム (system).
- システム -> the angel with セーブ / ロード -> slot list スロット1/2 -> "checking the memory card" (~600 frames after a
  state load) -> the three save files (swords, データなし when empty) -> circle -> "セーブしますか？" with the cursor on
  **いいえ**: press left, then circle -> saving -> "セーブが終了しました". Route from the week screen:
  `60 -;6 cross;120 -;6 cross;600 -;6 down;50 -;6 down;50 -;6 down;50 -;6 circle;900 -;6 circle;200 -;6 circle;1000 -;6 circle;200 -;6 left;100 -;6 circle;1500 -`
  (`warp.py`'s POST var runs it after a warp). Needs `--sav work/saves/blank.mcd` (PCSX-Redux's own formatted
  blank; `tools/debug/mcd.py blank` writes an equivalent).
- Game-written cards: `work/saves/week1.mcd` (week 1, from a cold-boot warp + the route) and `work/saves/week2.mcd`
  (week 2). `tools/debug/mcd.py ls` lists them: product BISLPS-0175900, title "フェイバリットディア　ゲームデータ１",
  2 blocks (16 KB) per save, three saves per card.

### Save file layout (16 KB from block 1; offsets relative to the file; partly mapped)

- 0x000-0x1FF: "SC" title frame + icon frames.
- 0x200 u16 **c0** = (sum of bytes 0x204-0x3FFF) & 0x0FFF (matches both cards; guess until an edited save loads).
- 0x202 u16 **c1** = sum of bytes 0x204-0x22B (verified on both cards).
- 0x204-0x22B: a 40-byte header (changes week to week); 0x22C+: game data, copied from RAM chunks (save 0xB04-0x1804
  matches RAM 0x801C3DE4 + offset; 0x1A04-0x25FF matches 0x8001DC48 + offset; 0x2604+ matches 0x8001E410 + offset,
  week-2 RAM).
- Week 1 -> week 2 differences: 0x199C 0x64 -> 0x96 (angel AP 100 -> 150), 0x275C 01 -> 02 (week?), plus
  0x22C-0x321 (a table rewritten), 0x29DC-0x29E8 (a 13-entry list rotated).
- Names: the angel's name is 6 u16 font codes (tbl/jp.tbl, 0xFFFF padded) at 0x204 and again at 0x19AE. Week:
  0x215 (header) and 0x275C. AP: u16 0x199C.
- **`tools/debug/save.py`** (`ls`, `check`, `set --week --ap --name --poke --bad-sum`) edits a game-written card and
  fixes c0/c1. Verified 2026-11-20: `save_edit` scene (week2.mcd edited to week 5, AP 999, name ミカエルアン) loads
  through title -> Load Game to the week screen showing AP 999 and the new name; the same edit with `--bad-sum`
  (c0 off by one) never reaches the week screen, so c0 is checked and the formula is right.

## Programs (EXE chain; verified by disassembly and the `exec` warps)

- Every program switch goes through `\_LOADE.EXE` (loaded at 0x801C0000): the caller looks the path up in an
  8-entry table (PSX.EXE 0x80175E98, 12 bytes each: PS_MOV 0, PSX 1, FD_MOV 2, FIN 3, EPILOG 4, GOVER 5, FD_BALL 6,
  _LOADE 7), writes the index to scratchpad 0x1F800020 and execs _LOADE, which loads that program.
- PSX.EXE `exec(path)` = 0x8003C7D4 (4 callers). `game_clear(a0)` = 0x8003ABB8: writes a0+1 to scratchpad
  0x1F800000, then a0=0 -> FD_MOV.EXE (ending movie), 1 -> FIN.EXE (staff roll), 2 -> EPILOG.EXE if scratchpad
  0x14 == 0x1C else PS_MOV.EXE. Called by an event-script opcode (0x800C4680), by 0x801042A8 (when 0x8001F5F1 ==
  0xFF) and at PSX.EXE start (0x8003AF64, when 0x80010008 is 1 or 2: the program restarted after FD_MOV/FIN).
  Calling it by hand from the week screen with a0=0 hangs (the opcode does sound fades first); exec'ing the program
  directly works.
- PS_MOV.EXE is the boot/title program (logos, OP.STR, title menu): it execs PSX.EXE (New Game/Load) and FD_BALL.EXE.
- **GOVER.EXE is not referenced by any code** (no exec of its path in any program): it looks like an older build of
  the main program (same sound list, OVER_BAK/OVER_JI.TIM). Exec'd directly it shows black for ~1300 frames and
  returns to the title. The real game-over screen uses OVER640/OVER_JI/OVER_BAK.TIM from GDATA inside PSX.EXE
  (name list at PSX.EXE RAM 0x80014440); its trigger is not found yet.
- Battles run inside PSX.EXE: `battle(a0)` = 0x800C3FD4 (debug prints "BT_result after battle"), called from
  0x80113450 (in 0x801132C4, called from the VM at 0x800D090C) and via 0x80113844(a0 byte) from 0x80113720. Not
  warped yet.

## Warp kinds `exec` and `save` (tools/debug/warp.lua)

- `exec`: at the week-1 screen, warp.lua sets the CPU's a0 to the program's path string (found in PSX.EXE data) and
  pc to `exec` 0x8003C7D4 (`PCSX.getRegisters()` is writable; the CPU is then in the vsync wait loop, a safe place).
  Arrival = the pc has been inside _LOADE.EXE and left it. Scenes: credits (FIN), ending_movie (FD_MOV), epilog,
  minigame (FD_BALL).
- `save`: title -> Load Game -> slot 1 -> card check -> save N -> "ロードしますか？" (left, circle) -> hub -> circle
  (予定) until the week-screen flag. Card from the scene's `card` column (copied into the run's folder). Hub scenes
  add `post` presses from the week screen (cross twice = hub).

Limits: the target runs in MYH16's context (week 1, the guild room background, Shelly/Florinda as the fairies,
default flags). Scripts that read state they expect (town, hero, story flags) may show wrong portraits or
backgrounds or stop (see the survey results in `tools/debug/scenes.tsv` notes). Battles, game over, the endings'
EXE chain (EPILOG/FIN.EXE credits) and FD_BALL.EXE are separate programs: see the scene list for which are covered.
