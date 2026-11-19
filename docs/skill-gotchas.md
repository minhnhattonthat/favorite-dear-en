# Skill gotchas (one line each: reference file, then the fact)

- SKILL.md Step 0: in an Orca profile (CLAUDE_CONFIG_DIR elsewhere) the plugin's guard hook never loads; the canary went through until the hooks block was added to .claude/settings.json with the stable marketplace path (it then took effect without a restart).
- SKILL.md / platform-ps1.md: a repo helper named `tools/re.py` shadows the stdlib `re` (capstone imports fail); name it `retools.py`.
- emulator-qa.md (PCSX-Redux): `L.dump_ppu` writes 2 MB, not 1 MB: the first 1 MB is VRAM 1024x512 16-bit, the rest is padding/second copy.
- emulator-qa.md (PCSX-Redux): read breakpoints on script text in RAM never fired for this game while write breakpoints (watch.lua, --debugger) did; trace the draw path from the output buffer backwards.
- platform-ps1.md: emu.py `L.shot(name)` on PCSX writes a file without .png extension (`dump_7650`), and it is a raw-size file the Read tool rejects; use --shots instead.
- pipeline.md §Recon: a scan for FFFF-terminated strings found only 28 KB of text and the dialogue looked missing; the real script was inline in VM bytecode (no terminator, opcode-delimited). Search RAM for an on-screen line encoded with the table before concluding text is compressed.
- pipeline.md §Recon (code = font cell): kana read by eye from a sheet misread 々 as ゞ; decode a long script sample and read it as Japanese (数々の) before trusting the table.
- platform-ps1.md: the font image had 0x66C cells, not the 0x5E0 an earlier session assumed; find the font end by matching every cell (scores collapse on non-font data) rather than by eye.
- context-mode (Claude Code plugin): Bash output above ~4 KB comes back as a stub; keep disassembly/sample prints under that or use ctx_execute.
- emulator-qa.md §Hooks (scripts/sheet.py): `--crop` past the image edge crashes with struct.error in write_png; PS1 shots switch between 320 and 640 wide per screen, so check the size first.
- translation.md / ground rules (Claude Code Edit tool): an Edit whose old/new string ends in a tab dropped that tab and merged two TSV columns; rewrite small TSVs whole.
- emulator-qa.md §Debug tool (PS1): a game that loads event scripts by name from a name table in RAM can be warped by overwriting the name slot of the first event the game loads; no debugger and no code patch needed (Favorite Dear, docs/re/debug.md).
- emulator-qa.md §Debug tool (PS1, PCSX-Redux): `PCSX.getRegisters()` is writable from `L.on_frame` (`r.GPR.n.a0 = x; r.pc = fn`); jumping into a never-returning routine (an exec of another program) from the game's vsync wait loop works as a warp. Calling a routine that returns (a battle start) the same way hung the emulator: no frame after the call.
- context-mode (Claude Code): Read/Bash outputs over ~4 KB come back as a one-line stub even for 70-line files; read with offset/limit in ~35-line parts or print only the answer from ctx_execute.
