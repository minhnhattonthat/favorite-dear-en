-- Find a jump into the BIOS reset (pc stuck at 0xBFC0xxxx with RAM wiped, no CPU exception). Needs --debugger.
-- Logs the registers when 0xBFC00000 runs, and the first pair-glyph renders (font hook, codes >= 0x2000) with ra.
-- Usage: emu.py CUE --state-in S --frames N --debugger --script tools/lua/crashtrace.lua
local n_glyph = 0
local mem = PCSX.getMemPtr()
local function rd32(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) | (mem[a + 2] << 16) | (mem[a + 3] << 24) end
-- 0x8003B6E0: the name lookup 0x8003B680 found nothing and is about to strcpy the name (s3) into 0x80013180; an
-- unterminated name wipes RAM there. Log the name's bytes and the caller, and save a state (CRASH_STATE) on the spot.
L.on_exec(0x8003B6E0, function()
  local g = PCSX.getRegisters().GPR.n
  local t = {}
  for i = 0, 15 do t[#t + 1] = string.format("%02X", mem[(g.s3 + i) & 0x1FFFFF]) end
  L.log(string.format("f%d NOT FOUND name@%08X [%s] caller=%08X", L.frame, g.s3, table.concat(t, " "),
    rd32(g.sp + 0x20)))
  if CRASH_STATE then L.save_state(CRASH_STATE); CRASH_STATE = nil end
end)
L.on_exec(0xBFC00000, function()
  local g = PCSX.getRegisters().GPR.n
  L.log(string.format("f%d RESET ra=%08X sp=%08X a0=%08X a1=%08X v0=%08X t9=%08X", L.frame, g.ra, g.sp, g.a0,
    g.a1, g.v0, g.t9))
end)
L.on_exec(0x800FDCA8, function()
  local g = PCSX.getRegisters().GPR.n
  if (g.a1 & 0xFFFF) >= 0x2000 and n_glyph < 10 then
    n_glyph = n_glyph + 1
    L.log(string.format("f%d pair glyph %04X ra=%08X a0=%08X a2=%08X", L.frame, g.a1 & 0xFFFF, g.ra, g.a0, g.a2))
  end
end)
