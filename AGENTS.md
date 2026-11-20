# Favorite Dear (PS1, NEC Interchannel, 1998) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`        -> build/favorite_dear_en.bin/.cue (checks the dump against `rom.sha1`, unpacks to `work/disc/` if missing, mkpsxiso; `--identity` = no edits, must match `rom/`)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/favorite_dear_en.cue --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene>|--event <NAME>|--all [--state] [--cue build/favorite_dear_en.cue]` (cold boot, no save; scenes: `tools/debug/scenes.tsv`, how: `docs/re/debug.md`; never ask the user to play to a scene)
- Extract:  `python -X utf8 tools/extract.py` (disc -> `script/*.tsv`; keeps `en`/`notes`, refuses to drop translated rows; `tools/evscript.py` parses the event scripts)
- Release:  `python -X utf8 tools/release.py` (xdelta patch against the .bin + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/Favorite Dear (Japan).bin/.cue` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Unpacked disc: `work/disc/tree/` + `work/disc/layout.xml` (dumpsxiso).
- Emulator: this repo's own PCSX-Redux in `tools/pcsx/` (nightly 32119.20261119.34 x64 from distrib.app via `$SKILL/scripts/fetch_emu.py pcsx`; gitignored); BIOS `tools/bios/scph5500.bin` (`fetch_emu.py psx-bios`). Savestates: `work/states/`.
- Disc tools (gitignored, re-download from GitHub releases): `tools/mkpsxiso/` (Lameguy64/mkpsxiso v2.30 win64), `tools/armips/` (Kingcom/armips v0.11.0), `tools/xdelta/` (jmacd/xdelta-gpl v3.1.0 x86_64).
- Text: `script/` (TSV). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- From Git Bash give Python Windows paths (`C:/...`); emu.py needs an absolute path to the .cue.
- Boot to title takes ~3300 frames even with Start mashed (logos + opening movie OP.STR).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
