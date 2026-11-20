-- Forced text viewer for text coverage (tools/textforce.py drives it; docs/re/events.md §Format).
-- Rides on `warp.py --event NAME` (warp.lua renames event id 32 to NAME, so id 32 loads NAME's file). Each time the
-- message printer (object [0x8001A4B8], stream = [obj+0] + 2 * u16 obj+0x10) moves into a row of that file that is not
-- the row it is printing, the hook moves its index to the next row still to show (TARGETS), so the scene's own print
-- ops play every message of the file in turn while warp.lua mashes through the pages.
--   TARGETS  "<start hw>,<end hw>,<want 0|1> ..." per row of the file, space-separated (halfword offsets from the
--            file start, in order; end = next row's start or the file end).
-- Logs like tools/lua/textlog.lua ("SCR", "PIDX"), so `textcover_map.py convert` maps the run; PIDX is logged only
-- for indexes the printer reached itself, never for the one the hook wrote. Also "FORCE <row> f<frame>" per redirect,
-- "SHOWN <row>" once the printer moved past a wanted row's first code, "FORCE done" (then the run ends) when no
-- wanted row is left.
local mem = PCSX.getMemPtr()
local function u16(a) a = a & 0x1FFFFF; return (mem[a] & 0xFF) | ((mem[a + 1] & 0xFF) << 8) end
local function u32(a) return u16(a) + u16(a + 2) * 65536 end
local function w16(a, v) a = a & 0x1FFFFF; mem[a] = v % 256; mem[a + 1] = math.floor(v / 256) % 256 end

local BUF = 0x8016C608
local ID = FORCE_ID or 32  -- the event id warp.lua renames (its local SLOT)
local rows = {}
for s, e, w in TARGETS:gmatch("(%d+),(%d+),(%d)") do
  -- w = 2: an unshown choice menu (｛..｝): never a redirect target, but when the scene's own print op moves the
  -- printer into it, the hook leaves it alone so the menu draws and PIDX logs it
  rows[#rows + 1] = {s = tonumber(s), e = tonumber(e), want = w == "1", choice = w == "2"}
end
local left = 0
for _, r in ipairs(rows) do if r.want then left = left + 1 end end
L.log(string.format("FORCE rows %d wanted %d", #rows, left))

local function row_of(rel)
  for i, r in ipairs(rows) do if rel >= r.s and rel < r.e then return i end end
  return nil
end
local function next_want(from)  -- `from` itself first: a target the script abandoned before printing it
  for k = 0, #rows - 1 do
    local i = (from - 1 + k) % #rows + 1
    if rows[i].want then return i end
  end
  return nil
end

local tab, last, cur, written, done_at = {}, {}, nil, nil, nil
local chainp, pendq, saveq = nil, nil, nil  -- patched terminator / patched clear before a chained row (buffer hw idx)
local function rd(i) return u16(BUF + 2 * i) end
local function wr(i, v) w16(BUF + 2 * i, v) end

-- Point the printer at row t (with a {clear} written just before it when `clear`), and when another wanted row is
-- left, turn t's terminating 0xFFFF into {wait} (0xFFF3) so the printer stops there instead of ending the message;
-- the frame handler then chains to the next row.
local tries = {}
local function start(obj, hoff, t, clear, n)
  -- a row the printer never moves into (a choice menu drawn by its own op, a table) gets 2 tries, then is skipped
  tries[t] = (tries[t] or 0) + 1
  if tries[t] > 2 then
    rows[t].want = false; left = left - 1
    L.log(string.format("SKIP %d f%d", t, n))
    local u = next_want(t)
    if not u then L.log(string.format("FORCE done f%d", n)); done_at = n + 600; return nil end
    t = u
    tries[t] = (tries[t] or 0) + 1
  end
  cur = t
  local s = hoff + rows[t].s
  -- a row opening with its FFFB key (op 0x90 looks messages up by it and starts the printer after it): start there
  if SKIPKEY and rd(s) == 0xFFFB then s = s + 2 end
  local at = s
  if clear then
    pendq, saveq = s - 1, rd(s - 1)
    wr(s - 1, 0xFFF2)
    at = s - 1
  end
  local nb = BUF + 2 * at
  w16(obj, nb % 65536); w16(obj + 2, math.floor(nb / 65536)); w16(obj + 0x10, 0)
  written = at
  local more = false
  for k, r in ipairs(rows) do if r.want and k ~= t then more = true; break end end
  if more then
    for p = s, hoff + rows[t].e - 1 do
      if rd(p) == 0xFFFF then chainp = p; wr(p, 0xFFF3); break end
    end
  end
  L.log(string.format("FORCE %d f%d%s", t, n, chainp and " chain" or ""))
  return at
end

L.on_frame(function(n)
  local hoff
  for s = 0, 9 do
    local e = 0x8016C5B8 + 8 * s
    local id, off = u16(e), u16(e + 2)
    local v = string.format("%d %d", id, off)
    if tab[s] ~= v then tab[s] = v; L.log(string.format("SCR %d %s", s, v)) end
    if id == ID then hoff = off end
  end
  if done_at and n >= done_at then L.finish(0) end
  local hi = u16(0x8001A4BA)
  if not (hi >= 0x8000 and hi < 0x8020) then return end
  local obj = u32(0x8001A4B8)
  if u16(obj + 8) ~= 0 then return end  -- name/insert sub-stream
  local base = u32(obj)
  if base < BUF or base >= 0x80180000 then return end
  local bidx = (base - BUF) / 2
  local idx = bidx + u16(obj + 0x10)
  if not hoff and chainp then L.log(string.format("UNLOAD f%d", n)) end
  if not hoff then chainp, pendq = nil, nil end  -- the file left the buffer: its patches went with it
  if hoff and not done_at then
    if pendq and idx > pendq then wr(pendq, saveq); pendq = nil end
    local rel = idx - hoff
    if cur and rows[cur].want and rel > rows[cur].s and rel < rows[cur].e then
      rows[cur].want = false; left = left - 1
      L.log(string.format("SHOWN %d f%d", cur, n))
    end
    if chainp then
      if idx == chainp or idx == chainp + 1 then  -- at the {wait} that replaced the terminator: chain
        wr(chainp, 0xFFFF); chainp = nil
        local t = next_want(cur)
        if t then idx = start(obj, hoff, t, true, n) or idx; rel = idx - hoff end
      elseif idx < hoff + rows[cur].s - 1 or idx > chainp + 1 then  -- the script moved the printer elsewhere
        L.log(string.format("UNCHAIN %d at %d idx %d f%d", cur, chainp, idx, n))
        wr(chainp, 0xFFFF); chainp = nil
      end
    end
    local i = row_of(rel)
    if i and rows[i].choice and i ~= cur then
      rows[i].choice = false
      L.log(string.format("CHOICE %d f%d", i, n))
      cur = i
    elseif not chainp and i and i ~= cur and idx ~= written then
      local t = (rows[i].want and rel == rows[i].s) and i or next_want(cur or i)
      if t == nil then
        L.log(string.format("FORCE done f%d", n)); done_at = n + 600  -- let the last page draw, then stop
      elseif t == i and rel == rows[t].s then
        cur = t
      else
        -- the print op points obj+0 at its message and counts obj+0x10 from 0: move both
        idx = start(obj, hoff, t, false, n) or idx
      end
    end
  end
  if idx ~= last[obj] then
    last[obj] = idx
    if idx ~= written then L.log(string.format("PIDX %d %X f%d", idx, obj, n)) end
  end
end)
