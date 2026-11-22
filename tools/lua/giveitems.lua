-- giveitems.lua: fill the angel's item bag (debug only) so the hero-visit GIFT screen has something to list.
--   emu.py CUE --state-in S --lua tools/lua/giveitems.lua [--var "ITEMS='0x01,0x20,0x40'"]
-- Bag: u8 count at 0x80026FAC, item codes (u8) from 0x80026FAD (read by 0x8010D4E8, the gift list renderer).
local ffi = require("ffi")
local mem = ffi.cast("uint8_t*", PCSX.getMemPtr())
local codes = {}
for c in string.gmatch(ITEMS or "0x01,0x02,0x20,0x40,0x60,0x80", "0x%x+") do codes[#codes + 1] = tonumber(c) end
L.on_frame(function(n)
  if n ~= (ITEMS_AT or 2) then return end
  mem[0x26FAC] = #codes
  for i, c in ipairs(codes) do mem[0x26FAC + i] = c end
  L.log("giveitems: " .. #codes .. " items")
end)
