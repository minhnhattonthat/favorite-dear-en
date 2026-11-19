-- When load_by_name (0x8003B680) is asked for a name containing NAME, log the code addresses found on the stack
-- (a poor man's backtrace). Needs --debugger. --var "NAME='KANRI14'"
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
local function u32(a)
  a = a & 0x1FFFFF
  return mem[a] | (mem[a + 1] << 8) | (mem[a + 2] << 16) | (mem[a + 3] << 24)
end
local count = 0
L.on_exec(0x8003B680, function()
  local r = PCSX.getRegisters().GPR.n
  local s = cstr(r.a0)
  if count < 4 and s:find(NAME, 1, true) then
    count = count + 1
    local t = {}
    for i = 0, 0x400, 4 do
      local w = u32(r.sp + i)
      if w >= 0x80010000 and w < 0x80140000 and (w & 3) == 0 then t[#t + 1] = string.format("%X:%08X", i, w) end
    end
    L.log(string.format("f%d %s ra=%08X sp=%08X %s", L.frame, s, r.ra, r.sp, table.concat(t, " ")))
  end
end)
