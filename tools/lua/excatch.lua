-- Log CPU exceptions other than interrupts (EPC, Cause, BadVAddr, ra, sp). Needs --debugger.
-- Hooks the general exception vector 0x80000080; Cause ExcCode 0 (interrupt) and 8 (syscall) are skipped. This PCSX-Redux build
-- exposes CP0 only as an array: r[8] BadVAddr, r[12] SR, r[13] Cause, r[14] EPC.
local n_logged = 0
L.on_exec(0x80000080, function()
  local r = PCSX.getRegisters()
  local cause, epc, bad = r.CP0.r[13], r.CP0.r[14], r.CP0.r[8]
  local code = (cause >> 2) & 0x1F
  if code ~= 0 and (code ~= 8 or EXC_SYSCALLS) and n_logged < 20 then  -- 8 = syscall (BIOS calls): set EXC_SYSCALLS=true to see them
    n_logged = n_logged + 1
    local g = r.GPR.n
    L.log(string.format("f%d EXC code=%d EPC=%08X BadVAddr=%08X ra=%08X sp=%08X a0=%08X v0=%08X", L.frame, code,
      epc, bad, g.ra, g.sp, g.a0, g.v0))
  end
end)
