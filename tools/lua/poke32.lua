-- poke32.lua: hold u32 words in RAM every frame from POKE_FROM on (a width test without a test build).
--   --var "POKES='0x80169D8C=0x80125708,0x80166060=0x80125500'" [--var POKE_FROM=3000]
-- Used for phase 8's repoint check: point the Apprentice rank entry at a moved string and look at the status screen.
local ffi = require("ffi")
local mem = ffi.cast("uint32_t*", PCSX.getMemPtr())
local list = {}
for a, v in string.gmatch(POKES or "", "(0x%x+)=(0x%x+)") do
  list[#list + 1] = { (tonumber(a) - 0x80000000) / 4, tonumber(v) }
end
L.on_frame(function(n)
  if n < (POKE_FROM or 3000) then return end
  for _, p in ipairs(list) do mem[p[1]] = p[2] end
end)
