-- Log event-VM sub-commands. Needs --debugger. Usage: emu.py ... --debugger --script tools/lua/cmdlog.lua
-- 0x800CA570 cmd(a0 = work base, a1 = &pos): dispatches on script[pos] - 0x3B through the jump table at
-- 0x80039108 (0xD3 and 0xE3 call battle_start 0x800D08E4). Logs the command word with 4 words of context each side.
-- Standalone (no warp.lua KIND), from a state taken before the event loads (e.g. warp.py + tools/lua/stateat.lua):
--   EVENT='NAME'  overwrite event slot 32 (MYH16) with NAME, as warp.lua does
--   HERO=n        hold the current-hero byte 0x80020991 at n for the first 60 frames
local mem = PCSX.getMemPtr()
local function rd16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
L.on_exec(0x800CA570, function()
  local r = PCSX.getRegisters().GPR.n
  local base, pos = r.a0, rd16(r.a1)
  local t = {}
  for i = -4, 4 do t[#t + 1] = string.format(i == 0 and "[%04X]" or "%04X", rd16(base + 2 * (pos + i))) end
  L.log(string.format("f%d cmd pos=%04X %s", L.frame, pos, table.concat(t, " ")))
end)
L.on_exec(0x800D08E4, function()
  local r = PCSX.getRegisters().GPR.n
  L.log(string.format("f%d battle_start a0=%d a1=%d ra=%08X", L.frame, r.a0, r.a1, r.ra))
end)
if not KIND then
  L.on_frame(function(n)
    if EVENT and n == 1 then
      local a = (0x80173640 + 9 * 32) & 0x1FFFFF
      for i = 0, 8 do mem[a + i] = i < #EVENT and EVENT:byte(i + 1) or 0 end
      L.log("patched slot 32 -> " .. EVENT)
    end
    if HERO and n <= 60 then mem[0x20991] = HERO end
  end)
end
