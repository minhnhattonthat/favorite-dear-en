# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: starting (phase 7 done-when met 2026-11-20: build green, batch checks and
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
- **Builds (2026-11-20, all batches b001-b144):** `favorite_dear_en.bin` sha1
  0c367aaf686f05923ae905d143afb6c79ddfa1c9, smoke ok, fitcheck ok. Marker/ruler/torture builds as in phase 5.
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
- **Waiting on the user:** (not blocking) the credits romanize real staff and cast names from kanji by my reading
  (`trans/staff/en.tsv`, given name first, Hepburn); readings such as 新千恵子 "C. Atarashi", 角田早穂 "Saho
  Tsunoda", 溝上真紀子 "M. Mizokami", 龍谷修武 "O. Ryutani", 萩原由乃 "Y. Hagiwara", 藤田顕史 "Kenji Fujita" are
  unverified. Corrections welcome; the build works either way.
- **Open bugs:** none.
