-- Log the PC and the MODE/PHASE flags every PC_EVERY frames (default 200): where a black or stuck screen sits.
local mem = PCSX.getMemPtr()
local function rd16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
local every = PC_EVERY or 200
L.on_frame(function(n)
  if n % every == 0 then
    L.log(string.format("f%d pc=%08X ra=%08X A4A8=%d A654=%d", n, L.pc(), PCSX.getRegisters().GPR.n.ra,
      rd16(0x8001A4A8), rd16(0x8001A654)))
  end
end)
