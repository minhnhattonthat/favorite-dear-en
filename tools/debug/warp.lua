-- Favorite Dear debug warp: cold boot -> any scene, no save and no savestate needed.
-- Normally run through tools/debug/warp.py SCENE, which reads tools/debug/scenes.tsv and sets these globals:
--   KIND   'title' | 'load' | 'option' | 'newgame' | 'week' | 'map' | 'event'
--   EVENT  event-script name for KIND 'event' (any name in the PSX.EXE event-name table, e.g. 'SEND01')
--   AFTER  'mash' (default: press circle every MASH_EVERY frames once there) | 'hold' (no input once there)
--   MASH_EVERY  frames between circle presses after arrival (default 45)
--   POST   presses after arrival, route syntax with ';' between steps ("60 -;6 cross;500 -"): submenus of a
--          scene. Shot post.png when they are done; STATE is then saved there instead.
--   STATE  absolute path: save a savestate here 60 frames after arrival
-- Shots: arrived.png 30 frames after arrival (the proof); AFTER 'hold' ends the run 90 frames after arrival.
-- Log lines: "WARP <stage> f<frame>"; "WARP OK" once the scene is reached (warp.py fails the run without it).
--
-- How it works (docs/re/debug.md): the opening is driven with the newgame route, then circle until the week screen
-- flag (0x8001A4A8 == 5 and 0x8001A654 == 1); the week-1 route sends both fairies to hero search, which makes the
-- game load event MYH16 (id 32). For KIND 'event' the 9-byte name slot of MYH16 in the event-name table
-- (RAM 0x80173640 + 9 * id) is overwritten with EVENT, so the game's own loader fetches that script instead.
local mem = PCSX.getMemPtr()
local function rd16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
local function rdstr(a, n)
  local t = {}
  a = a & 0x1FFFFF
  for i = 0, n - 1 do
    local c = mem[a + i]
    if c == 0 then break end
    t[#t + 1] = string.char(c)
  end
  return table.concat(t)
end

local NAMES = 0x80173640        -- event-name table, 9 bytes per id
local SLOT = 32                 -- MYH16: first event of week 1 with both fairies on hero search
local ENTRIES = 0x8016C5B8      -- loaded-event table: 10 x (u16 id, u16 offset, u16, u16)
local MODE, PHASE = 0x8001A4A8, 0x8001A654

KIND = KIND or "event"
AFTER = AFTER or "mash"
MASH_EVERY = MASH_EVERY or 45

local function week_screen() return rd16(MODE) == 5 and rd16(PHASE) == 1 end
local function exe_loaded() return rdstr(NAMES + 9 * 150, 9) == "MAPSYS" end
local function event_loaded(id)
  for i = 0, 9 do if rd16(ENTRIES + 8 * i) == id then return true end end
  return false
end

local function route(steps) for _, s in ipairs(steps) do L.press(s[2], s[1]) end end
-- past logos and the opening movie to the title menu (New Game / Load Game / Option is up from f~3700)
local TITLE = { {1500, "-"}, {6, "start"}, {300, "-"}, {6, "start"}, {300, "-"}, {6, "start"}, {600, "-"},
                {6, "start"}, {900, "-"}, {6, "start"}, {120, "-"} }
-- tools/routes/newgame.txt: title menu -> New Game
local NEWGAME = { {6, "circle"}, {600, "-"} }
-- title menu -> Load Game / Option (cursor moves need ~40 frames between presses)
-- (Option shows a memory-card notice for ~250 frames first; Load shows Now Loading, then the angel's card menu)
local TITLE_SUB = { load = { {6, "down"}, {40, "-"}, {6, "circle"}, {1800, "-"} },
                    option = { {60, "-"}, {6, "down"}, {60, "-"}, {6, "down"}, {60, "-"}, {6, "circle"}, {600, "-"} } }
-- tools/routes/week1.txt: both fairies -> hero search, confirm
local WEEK1 = { {30, "-"}, {6, "right"}, {40, "-"}, {6, "circle"}, {60, "-"}, {6, "down"}, {40, "-"}, {6, "circle"},
                {90, "-"}, {6, "right"}, {40, "-"}, {6, "circle"}, {60, "-"}, {6, "down"}, {40, "-"}, {6, "circle"},
                {90, "-"}, {6, "left"}, {40, "-"}, {6, "left"}, {40, "-"}, {6, "circle"}, {90, "-"}, {6, "down"},
                {40, "-"}, {6, "circle"}, {90, "-"} }

local stage = "boot"
local arrived_at = nil
local patched = false
local map_at = nil
local post_done = nil
local function go(s) stage = s; L.log(string.format("WARP %s f%d", s, L.frame)) end
local function arrive()
  arrived_at = L.frame
  go("arrived")
  L.log(string.format("WARP OK %s f%d", KIND == "event" and EVENT or KIND, L.frame))
end

if KIND == "event" then
  assert(type(EVENT) == "string" and #EVENT >= 1 and #EVENT <= 8, "EVENT must be a 1-8 char event name")
end

route(TITLE)
if TITLE_SUB[KIND] then route(TITLE_SUB[KIND]) elseif KIND ~= "title" then route(NEWGAME) end
go("newgame")

L.on_frame(function(n)
  if KIND == "event" and not patched and exe_loaded() then
    local a = (NAMES + 9 * SLOT) & 0x1FFFFF
    for i = 0, 8 do mem[a + i] = i < #EVENT and EVENT:byte(i + 1) or 0 end
    patched = true
    L.log(string.format("WARP patched slot %d -> %s f%d", SLOT, EVENT, n))
  end

  if stage == "newgame" then
    if KIND == "title" or TITLE_SUB[KIND] then
      if L.route_done() then arrive() end
    elseif KIND == "newgame" then
      if rd16(MODE) == 2 and n > 5000 then arrive() end  -- name entry panel
    elseif L.route_done() then
      go("opening")
    end
  elseif stage == "opening" then
    if week_screen() then
      go("week_wait")
      arrived_at = n
    elseif L.route_done() and n % 20 == 0 then
      L.press("circle", 6)
    end
  elseif stage == "week_wait" then
    if n - arrived_at >= 30 then
      if KIND == "week" then arrive() else route(WEEK1); go("week1") end
    end
  elseif stage == "week1" then
    if L.route_done() then go("to_event"); arrived_at = n end
  elseif stage == "to_event" then
    -- the world map shows ~f400-550 after MODE turns 1 (the orders confirmed; no text in between, so the timing
    -- holds for any build). No cleaner map flag was found.
    if KIND == "map" and rd16(MODE) == 1 then
      if not map_at then map_at = n end
      if n - map_at >= 450 then arrive() end
    elseif KIND == "event" and event_loaded(SLOT) then
      arrive()
    elseif not map_at and L.route_done() and n % 60 == 0 then
      L.press("circle", 6)
    end
  elseif stage == "arrived" then
    local dt = n - arrived_at
    if dt == 30 then
      L.shot("arrived.png")
      if POST then
        for f, keys in POST:gmatch("(%d+)%s+([%w+%-]+)") do L.press(keys, tonumber(f)) end
      end
    end
    if dt > 30 and POST and L.route_done() and not post_done then
      post_done = n
      L.shot("post.png")
      L.log(string.format("WARP POST done f%d", n))
    end
    if STATE and (POST and post_done == n or not POST and dt == 60) then
      L.save_state(STATE); L.log("WARP state " .. STATE)
    end
    if AFTER == "hold" and dt >= 90 and (not POST or post_done) then L.shot("final.png"); L.finish(0) end
    if AFTER == "mash" and dt > 0 and dt % MASH_EVERY == 0 and L.route_done() then L.press("circle", 6) end
  end
end)
