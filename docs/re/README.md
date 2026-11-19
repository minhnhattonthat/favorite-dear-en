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
| `disc.md` | disc layout, GDATA.BIN directory, LZSS (*.PSS) | directory + LZSS verified; most of GDATA unmapped |
| `text.md` | script location, 16-bit encoding, control codes, font | encoding + font verified; table and pointer tables not done |

Prior work: no earlier English patch or community tools found (web search 2026-11-20).

Helpers: `tools/retools.py` (capstone dis, lui/addiu xref), `tools/lzss.py` (codec, roundtrip-tested on PSS files),
`tools/font.py` (glyph sheet), `tools/lua/dumpram_at.lua` (RAM+VRAM dump at a frame). Watch probe:
`$SKILL/scripts/lua/probes/watch.lua` with `--debugger`; write breakpoints fire on KSEG0 or physical addresses.
