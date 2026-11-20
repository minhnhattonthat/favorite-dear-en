-- Probe (negative result, kept for the record): event sub-command 0xE0 sets byte 0x80184170 = 1 (fade out) and 0xE1
-- waits until it reads 2, which only the battle screen's fade task 0x80044C8C writes. This hook writes 2 as soon as
-- it sees 1; a T-script swapped into MYH16's slot still hangs, because the fade task also switches the screen.
-- Use warp.py --battle NAME for T-events instead (docs/re/debug.md). Usage: warp.py --event T0101 --lua <this>.
local mem = PCSX.getMemPtr()
local FLAG = 0x184170
L.on_frame(function(n)
  if mem[FLAG] == 1 then
    mem[FLAG] = 2
    L.log(string.format("townflag 1 -> 2 f%d", n))
  end
end)
