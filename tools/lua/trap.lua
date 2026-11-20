-- Trap-byte test for free RAM: at frame TRAP_AT fill each range with 0xA5, then every TRAP_EVERY frames (and at the
-- last check, TRAP_END) log the sub-ranges whose bytes changed. A range that never logs a change is free for that run.
--   warp.py SCENE --lua tools/lua/trap.lua --var TRAP_AT=11700 --var "TRAP='0x80010000-0x800109A4,0x800671DC-0x80068240'"
--           [--var TRAP_EVERY=600] [--var TRAP_END=19000]
local mem = PCSX.getMemPtr()
local ranges = {}
for lo, hi in string.gmatch(assert(TRAP, "set --var TRAP='lo-hi,..'"), "(0x%x+)%-(0x%x+)") do
  ranges[#ranges + 1] = {tonumber(lo) & 0x1FFFFF, tonumber(hi) & 0x1FFFFF}
end
local at, every, last = assert(TRAP_AT), TRAP_EVERY or 600, TRAP_END or math.huge
local armed = false

local function check(n)
  for _, r in ipairs(ranges) do
    local runs, s, total = {}, nil, 0
    for a = r[1], r[2] do
      local bad = a < r[2] and mem[a] ~= 0xA5
      if bad then total = total + 1; s = s or a
      elseif s then runs[#runs + 1] = string.format("%08X-%08X", 0x80000000 + s, 0x80000000 + a); s = nil end
    end
    L.log(string.format("f%d trap %08X-%08X changed %d bytes %s", n, 0x80000000 + r[1], 0x80000000 + r[2], total,
      table.concat(runs, " ", 1, math.min(#runs, 12))))
  end
end

L.on_frame(function(n)
  if n == at then
    for _, r in ipairs(ranges) do for a = r[1], r[2] - 1 do mem[a] = 0xA5 end end
    armed = true
    L.log("trap armed f" .. n)
  elseif armed and (n % every == 0 or n == last) then
    check(n)
  end
end)
