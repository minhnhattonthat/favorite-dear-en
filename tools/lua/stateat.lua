-- Save a state at frame STATE_AT to STATE_AT_PATH (warps are deterministic, so a frame from an earlier log works).
-- Usage: warp.py ... --lua tools/lua/stateat.lua --var STATE_AT=13517 --var "STATE_AT_PATH='C:/.../x.sstate'"
L.on_frame(function(n)
  if n == STATE_AT then L.save_state(STATE_AT_PATH); L.log("stateat " .. STATE_AT_PATH .. " f" .. n) end
end)
