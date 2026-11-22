-- setmenu.lua: force the two topics of a hero-visit choice menu (debug only), to see given option rows in game.
--   emu.py build/favorite_dear_en.cue --state-in work/states/sqa04_fix.sstate --script tools/lua/setmenu.lua
--       [--var MENU_A=0x64 --var MENU_B=0x82 --var MENU_ID=32 --var MENU_UNTIL=40]
-- The visit scripts keep the two topic keys in variable slots 9 and 10 (code halfwords; op 0x90 `8009`/`800A`,
-- docs/re/events.md, tools/menuopts.py). Loaded events: 0x8016C5B8, 10 x 8 bytes (u16 id, u16 halfword offset into
-- the buffer at 0x8016C608); the warp loads its target as id 32. Defaults: 0x64 "beautiful scenery" and 0x82
-- "anything I can do" (the issue #4 pair). Patch only before the menu prints (the state is taken ~60 frames ahead).
local ffi = require("ffi")
local mem = ffi.cast("uint16_t*", PCSX.getMemPtr())
local id = MENU_ID or 32
local done = false
L.on_frame(function(n)
  if n > (MENU_UNTIL or 40) then return end
  for e = 0, 9 do
    local base = (0x16C5B8 + 8 * e) / 2
    if mem[base] == id then
      local script = 0x16C608 + 2 * mem[base + 1]
      local code = script + mem[(script + 4) / 2]
      mem[(code + 2 * 9) / 2] = MENU_A or 0x64
      mem[(code + 2 * 10) / 2] = MENU_B or 0x82
      if not done then
        L.log(string.format("SETMENU id %d script %06X code %06X", id, script, code))
        done = true
      end
    end
  end
end)
