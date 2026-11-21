-- Trace asm/name.inc name_latin's return (load-delay check): log every exec of the instruction after its
-- `jal 0x8010567C` and of the task code it returns to (0x800C0F60), with sp. A hazard-free return hits each once.
-- Usage: emu.py CUE --state-in work/states/newgame.sstate --route-str "6 circle;300 -" --debugger --script tools/lua/namelatin.lua
local AFTER_JAL = NAME_AFTER_JAL or 0x80125A50
local n = 0
local function log(tag)
  if n < 40 then
    n = n + 1
    local g = PCSX.getRegisters().GPR.n
    L.log(string.format("f%d %s pc-hook sp=%08X ra=%08X", L.frame, tag, g.sp, g.ra))
  end
end
L.on_exec(AFTER_JAL, function() log("name_latin+after_jal") end)
L.on_exec(0x800C0F60, function() log("task_resume") end)
