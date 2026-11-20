-- longskill.lua (debug only): width test for the hero status screen's Special box (asm/skill.inc).
-- From frame 8000 every hero's three skills point at the three longest names (Double Boomerang, Sol Prominence,
-- Tempest Hearts: u16 halfword offsets from 0x80175C1C in the table 0x8002DBFC, 3 per hero).
--   python -X utf8 tools/debug/warp.py stress_hero_reiv --cue C:/.../build/favorite_dear_en.cue \
--       --lua C:/.../tools/lua/longskill.lua      (2026-11-21: all three fit, work/qa/skillwide)
local ffi = require("ffi")
local mem = ffi.cast("uint16_t *", PCSX.getMemPtr())
local vals = { 0x7D, 0xC3, 0x128 }
L.on_frame(function()
  if L.frame < 8000 then return end
  for h = 0, 11 do
    for k = 0, 2 do mem[(0x2DBFC + h * 6 + k * 2) / 2] = vals[k + 1] end
  end
end)
