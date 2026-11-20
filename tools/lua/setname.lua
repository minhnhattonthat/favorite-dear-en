-- setname.lua: once a loaded save's angel name is in RAM, overwrite every copy of it with another name, so the game
-- itself writes that name to the card on the next save (the 1-code name test: is a 1-halfword name unloadable when
-- the game wrote it, not save.py?). Ride along a `save` warp whose POST saves:
--   warp.py name1_write --lua tools/lua/setname.lua --var "FROM={0x7649,0x2079}" --var "TO={0x2052}"
-- FROM: the halfwords of the name on the card (Ivy = "Iv","y " pair codes); TO: the new name (padded with 0xFFFF to
-- FROM's length + 1). Scans all 2 MB of RAM 300 frames after 0x8001F5F6 first holds FROM[1]; logs every address.
local mem = PCSX.getMemPtr()
local NAME = 0x1F5F6
local seen, done = nil, false

local function u16(a) return (mem[a] % 256) + (mem[a + 1] % 256) * 256 end
local function w16(a, v) mem[a] = v % 256; mem[a + 1] = math.floor(v / 256) % 256 end

L.on_frame(function(n)
  if done then return end
  if not seen then
    if u16(NAME) == FROM[1] then seen = n; L.log(string.format("setname: name seen f%d", n)) end
    return
  end
  if n - seen < 300 then return end
  done = true
  local hits = 0
  for a = 0, 0x1FFFF0, 2 do
    local ok = true
    for i = 1, #FROM do if u16(a + 2 * (i - 1)) ~= FROM[i] then ok = false; break end end
    if ok and u16(a + 2 * #FROM) == 0xFFFF then
      for i = 1, #FROM + 1 do w16(a + 2 * (i - 1), TO[i] or 0xFFFF) end
      hits = hits + 1
      L.log(string.format("setname: 0x%08X rewritten f%d", 0x80000000 + a, n))
    end
  end
  L.log(string.format("setname: %d copies", hits))
end)
