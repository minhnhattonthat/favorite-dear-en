# Favorite Dear English translation

Unofficial English fan translation of **Favorite Dear** (PlayStation, NEC Interchannel, 1998): the source text and tools
that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue and story, battle text, the 23 endings | Translated |
| Menus, items, places, system messages | Translated (two short status-label strings in PSX.EXE are still Japanese: their layout is not known yet) |
| Title screen, menus and labels drawn as graphics | Translated (the small kana reading under the title logo is kept) |
| Name entry | English letter page by default; the kana pages are kept |
| Staff credits | Translated (names romanized) |
| Voice acting, songs | Left in Japanese (audio) |
| Memory-card titles (console memory-card manager) | Left in Japanese |

Base disc: `Favorite Dear (Japan).bin` (Redump, SLPS-01759), 594696144 bytes, CRC32 8269851F,
MD5 8151d2c66c6d8978324a0c872dedc21d, SHA-1 509ffd8fc65852eab028238d06fe23f9f0db7d13. Tested in PCSX-Redux; start
from a cold boot, not a savestate made with the Japanese game.

Known issues: see [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/favorite-dear-en
cd favorite-dear-en
# copy your dump to: rom/Favorite Dear (Japan).bin and .cue
#   (594696144 bytes, SHA-1 509ffd8fc65852eab028238d06fe23f9f0db7d13; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/favorite_dear_en.bin/.cue
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is NEC Interchannel's and is included only
so the translation can be checked against it. Favorite Dear is (c) NEC Interchannel; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
