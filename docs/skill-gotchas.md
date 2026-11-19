# Skill gotchas (one line each: reference file, then the fact)

- SKILL.md Step 0: in an Orca profile (CLAUDE_CONFIG_DIR elsewhere) the plugin's guard hook never loads; the canary went through until the hooks block was added to .claude/settings.json with the stable marketplace path (it then took effect without a restart).
- SKILL.md / platform-ps1.md: a repo helper named `tools/re.py` shadows the stdlib `re` (capstone imports fail); name it `retools.py`.
- emulator-qa.md (PCSX-Redux): `L.dump_ppu` writes 2 MB, not 1 MB: the first 1 MB is VRAM 1024x512 16-bit, the rest is padding/second copy.
- emulator-qa.md (PCSX-Redux): read breakpoints on script text in RAM never fired for this game while write breakpoints (watch.lua, --debugger) did; trace the draw path from the output buffer backwards.
- platform-ps1.md: emu.py `L.shot(name)` on PCSX writes a file without .png extension (`dump_7650`), and it is a raw-size file the Read tool rejects; use --shots instead.
