-- Text coverage log for tools/textcover_map.py. Per frame, read the message printer's object (pointer at 0x8001A4B8,
-- read by the printer task 0x800CC9EC; its stream index is the u16 at obj+0x10, a halfword index from the script
-- buffer 0x8016C608) and the loaded-script table at 0x8016C5B8 (10 x 8 bytes: u16 event id, u16 halfword offset).
-- Logs "SCR <slot> <id> <off>" when the table changes and "PIDX <index>" when the printer index changes.
-- No --debugger needed. Usage: warp.py SCENE --lua tools/lua/textlog.lua
local mem = PCSX.getMemPtr()
local function u16(a) a = a & 0x1FFFFF; return (mem[a] & 0xFF) | ((mem[a + 1] & 0xFF) << 8) end
local function u32(a) return u16(a) | (u16(a + 2) << 16) end
local tab = {}
local last = {}
L.on_frame(function()
  for s = 0, 9 do
    local e = 0x8016C5B8 + 8 * s
    local v = string.format("%d %d", u16(e), u16(e + 2))
    if tab[s] ~= v then
      tab[s] = v
      L.log(string.format("SCR %d %s", s, v))
    end
  end
  local obj = u32(0x8001A4B8)
  if DEBUG_OBJ and obj ~= lastobj then lastobj = obj; L.log(string.format("OBJ %08X", obj)) end
  local hi = u16(0x8001A4BA)  -- LuaJIT bit ops are signed 32-bit: range-check the high half
  if hi >= 0x8000 and hi < 0x8020 then
    local i = u16(obj + 0x10)
    if i ~= last[obj] then
      last[obj] = i
      L.log(string.format("PIDX %d %X f%d", i, obj, L.frame))
    end
  end
end)
