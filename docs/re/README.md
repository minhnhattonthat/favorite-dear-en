# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise. PSX.EXE: file offset = vaddr - 0x80010000 + 0x800.

| File | Covers | State |
|---|---|---|
| `disc.md` | disc layout, GDATA.BIN directory tables, LZSS (*.PSS) | tables + LZSS verified |
| `text.md` | 16-bit encoding (`tbl/jp.tbl`), printer control codes, PSX.EXE strings, credits, font | verified (tests/test_text.py) |
| `events.md` | the 468 event-script files in GDATA (the bulk of the dialogue), load buffer, VM | location verified; opcode args not decoded |
| `graphics.md` | graphics-text survey | done for GDATA images and disc-root images; movies not checked |
| `space.md` | free-space candidates, RAM limits | candidates only |
| `debug.md` | debug warp: event loader, event-name table, RAM mode flags, hub/save menus, memory-card save layout | warp verified; save checksum partly |

Prior work: no earlier English patch or community tools found (web search 2026-11-20).

Helpers: `tools/retools.py` (capstone dis, lui/addiu xref), `tools/lzss.py` (codec, roundtrip-tested on PSS files),
`tools/font.py` (glyph sheet), `tools/fontmatch.py` + `tools/mktbl.py` (build tbl/jp.tbl), `tools/scantext.py`
(FFFF-terminated strings in any file), `tools/events.py` (event scripts), `tools/tim.py` (TIM -> PNG, GDATA image dump), `tools/lua/dumpram_at.lua` (RAM+VRAM dump at a frame). Watch probe:
`$SKILL/scripts/lua/probes/watch.lua` with `--debugger`; write breakpoints fire on KSEG0 or physical addresses.
