-- peek.lua: log u16 values at RAM addresses every PEEK_EVERY frames from PEEK_FROM (default 3000, every 60).
--   warp.py SCENE --lua tools/lua/peek.lua --var "PEEK='0x8002752C,0x8002752E'" [--var PEEK_FROM=6000]
-- Used for the name-entry patch (asm/name.inc): count and page while the grid is up.
local ffi = require("ffi")
local mem = ffi.cast("uint8_t*", PCSX.getMemPtr())
local addrs = {}
for a in string.gmatch(assert(PEEK, "set --var PEEK='0x8...,..'"), "0x%x+") do addrs[#addrs + 1] = tonumber(a) & 0x1FFFFF end
local from, every = PEEK_FROM or 3000, PEEK_EVERY or 60
L.on_frame(function(n)
  if n < from or (n - from) % every ~= 0 then return end
  local out = {}
  for _, a in ipairs(addrs) do out[#out + 1] = string.format("%08X=%04X", 0x80000000 + a, mem[a] | mem[a + 1] << 8) end
  L.log("f" .. n .. " " .. table.concat(out, " "))
end)
