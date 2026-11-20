# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate: in progress, 86 of 144 event batches done (b001-b086; `batches.py todo` lists the 58 left), pilot checked in game.
- **Builds (2026-11-20, phase 6 b001-b005/b024/b025):** `favorite_dear_en.bin` sha1
  0262d61ff1b807ebe1944a3234b560f69696b9ca, smoke ok. Marker/ruler/torture builds as in phase 5. (b006-b016 merged
  into `script/events`, not yet built: phase 7 builds.)
- **Glyph-soup files (found 2026-11-20, phase 7 must fix):** 34F2 34F5 34F8 34FC 3500 3504 3507 350A (all rows,
  ~300) and parts of 393D, 3976-3986 decode as kana/kanji soup under `tbl/jp.tbl` (codes parse; a substitution,
  likely a per-scene glyph set). Batched as `-` (b009-b013); find their table, re-extract, re-batch, translate.
  Glossary "Decisions from earlier batches" has the detail.
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
  2. `python -X utf8 tools/batches.py todo` (next: b047; 36FD soup continues there), translate in order per `docs/translator-brief.md` and
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
  3. Not yet batched: `script/exe.tsv` (867 PSX.EXE rows, need a variant tag per row from `docs/windows.tsv`: hub help
     40, location 11, list 17, week tag/ACTION 10, save 12, confirm 16 (+6 hidden), yes/no 7), `script/staff.tsv`
     (credits, 14 full-width letters minus indent), `script/sjis.tsv` (memory-card titles).
  4. Review pass (self, fresh read-only, or codex after 11-26): pairs per batch, Critical/Important fixed.
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
- **Waiting on the user:** nothing.
- **Open bugs:** none.
