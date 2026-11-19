-- Probe: once RAM flag MODE (u16 at 0x8001A4A8) == WHEN_MODE for 30 frames, jump the CPU to FN with a0 = ARG.
-- Use for routines that never return (an exec of another program). Vars: FN, ARG, WHEN_MODE (default 5).
local mem = PCSX.getMemPtr()
local function rd16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
WHEN_MODE = WHEN_MODE or 5
local seen, done = nil, false
L.on_frame(function(n)
  if done then
    if n % 300 == 0 then L.log(string.format("PC %08x f%d", tonumber(PCSX.getRegisters().pc), n)) end
    return
  end
  if rd16(0x8001A4A8) == WHEN_MODE and rd16(0x8001A654) == 1 then
    seen = seen or n
    if n - seen >= 30 then
      local r = PCSX.getRegisters()
      L.log(string.format("CALL pc was %08x -> %08x a0=%d f%d", tonumber(r.pc), FN, ARG, n))
      r.GPR.n.a0 = ARG
      r.pc = FN
      done = true
    end
  elseif n % 20 == 0 then
    L.press("circle", 6)
  end
end)
