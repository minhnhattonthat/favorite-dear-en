-- Dump main RAM and VRAM at frame DUMP_AT (set with --var DUMP_AT=N, or a list --var "DUMP_AT='600,900'"):
-- <out>/ram_<N>.bin, <out>/v<N>.vram.bin.
local at = {}
for v in tostring(DUMP_AT):gmatch("%d+") do at[tonumber(v)] = true end
L.on_frame(function(n)
  if at[n] then
    L.dump_ram("ram_" .. n .. ".bin")
    L.dump_ppu("v" .. n)
    L.log("dumped ram+vram at " .. n)
  end
end)
