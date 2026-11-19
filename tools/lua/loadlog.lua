-- Log GDATA loads. Needs --debugger. Usage: emu.py ... --debugger --script tools/lua/loadlog.lua
-- 0x8003B3D0 load_by_name(a0 = name string, a1 = RAM dest); 0x8003B680 name -> table index (v0, <0 = not found);
-- 0x8003F838 disc read (a1 = RAM dest, a2 = sector, a3 = size).
local mem = PCSX.getMemPtr()
local function cstr(a)
  local t = {}
  a = a & 0x1FFFFF
  for i = 0, 31 do
    local c = mem[a + i]
    if c == 0 then break end
    t[#t + 1] = string.char(c)
  end
  return table.concat(t)
end
L.on_exec(0x8003B680, function()
  local r = PCSX.getRegisters().GPR.n
  L.log(string.format("f%d name '%s' ra=%08X", L.frame, cstr(r.a0), r.ra))
end)
L.on_exec(0x8003F838, function()
  local r = PCSX.getRegisters().GPR.n
  L.log(string.format("f%d read dest=%08X sector=%X size=%X ra=%08X", L.frame, r.a1, r.a2, r.a3, r.ra))
end)
