-- setequip.lua: hold every hero's three equipment slots (debug only), for the hero status screen's Equip box.
--   warp.py stress_hero_reiv --cue build/favorite_dear_en.cue --lua tools/lua/setequip.lua [--var "EQUIP='17,175,215'"]
-- Hero records: 0x8001F6E4 + 0x6C * hero (heroes 0..11), u16 item codes at +0x2A/+0x2C/+0x2E (0xFFFF = empty),
-- read by 0x801042CC (stat bonus) and 0x80110CFC (Equip box names). Defaults are the longest English names:
-- 17 Battle Boomerang, 175 Knitted Sweater, 215 Mermaid Earring.
local ffi = require("ffi")
local mem = ffi.cast("uint16_t*", PCSX.getMemPtr())
local codes = {}
for c in string.gmatch(EQUIP or "17,175,215", "%d+") do codes[#codes + 1] = tonumber(c) end
L.on_frame(function(n)
  if n < (EQUIP_FROM or 4000) then return end
  for hero = 0, 11 do
    for slot = 1, 3 do
      mem[(0x1F6E4 + 0x6C * hero + 0x28 + 2 * slot) / 2] = codes[slot] or 0xFFFF
    end
  end
end)
