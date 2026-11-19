-- Dump main RAM and VRAM at frame DUMP_AT (set with --var DUMP_AT=N): <out>/ram_<N>.bin, <out>/v<N>.vram.bin.
L.on_frame(function(n)
  if n == DUMP_AT then
    L.dump_ram("ram_" .. n .. ".bin")
    L.dump_ppu("v" .. n)
    L.log("dumped ram+vram at " .. n)
  end
end)
