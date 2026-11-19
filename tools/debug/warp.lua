-- Favorite Dear debug warp: cold boot -> any scene, no save and no savestate needed.
-- Normally run through tools/debug/warp.py SCENE, which reads tools/debug/scenes.tsv and sets these globals:
--   KIND   'title' | 'load' | 'option' | 'newgame' | 'week' | 'map' | 'event' | 'exec' | 'save'
--   EVENT  event-script name for KIND 'event' (any name in the PSX.EXE event-name table, e.g. 'SEND01')
--   EXE    program for KIND 'exec' (GOVER FD_BALL EPILOG FIN FD_MOV PS_MOV), started from the week-1 screen
--   SAVE   save number (1-3) for KIND 'save': loads it from the memory card given with emu.py --sav; arrival is
--          the week screen reached through the hub's 予定, so a rejected or corrupt save never arrives
--   PROOF  frames from arrival to the proof shot arrived.png (default 30)
--   AFTER  'mash' (default: press circle every MASH_EVERY frames once there) | 'hold' (no input once there)
--   MASH_EVERY  frames between circle presses after arrival (default 45)
--   POST   presses after arrival, route syntax with ';' between steps ("60 -;6 cross;500 -"): submenus of a
--          scene. Shot post.png when they are done; STATE is then saved there instead.
--   STATE  absolute path: save a savestate here 60 frames after arrival
--   TRACE  any value: log every change of the MODE/PHASE flags ("TRACE mode/phase 5/1 f1234")
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

-- KIND 'exec': from the week screen, jump the CPU into PSX.EXE's exec(path) at 0x8003C7D4 (it hands the path to
-- _LOADE.EXE, which loads the program), with a0 = the path string "\<EXE>.EXE;1" found in PSX.EXE's data.
-- Arrival = the CPU has gone through _LOADE.EXE (0x801C0000-0x801C6800) and left it again.
local EXEC_FN, EXEC_FIRST = 0x8003C7D4, 0x27BDFFE8   -- addiu sp, sp, -0x18 (checked before jumping)
local BATTLE_FN = 0x800D08E4
BATTLE = BATTLE or 1
local function rd32(a) a = a & 0x1FFFFF; return rd16(a) | (rd16(a + 2) << 16) end
local function find_str(s, lo, hi)
  local b1 = s:byte(1)
  for a = lo & 0x1FFFFF, (hi & 0x1FFFFF) - #s do
    if mem[a] == b1 then
      local ok = true
      for i = 2, #s do if mem[a + i - 1] ~= s:byte(i) then ok = false; break end end
      if ok then return 0x80000000 | a end
    end
  end
end
local function in_loader(pc) return pc >= 0x801C0000 and pc < 0x801C6800 end

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

local EXE_PATHS = { GOVER = "\\GOVER.EXE;1", FD_BALL = "\\FD_BALL.EXE;1", EPILOG = "\\TITLE\\EPILOG.EXE;1",
                    FIN = "\\DATA\\FIN.EXE;1", FD_MOV = "\\TITLE\\FD_MOV.EXE;1", PS_MOV = "\\PS_MOV.EXE;1" }
local exec_seen = false
PROOF = PROOF or 30

local stage = "boot"
local arrived_at = nil
local patched = false
local map_at = nil
local post_done = nil
local function go(s) stage = s; L.log(string.format("WARP %s f%d", s, L.frame)) end
local function arrive()
  arrived_at = L.frame
  go("arrived")
  L.log(string.format("WARP OK %s f%d", KIND == "event" and EVENT or KIND == "exec" and EXE or KIND, L.frame))
end

if KIND == "event" then
  assert(type(EVENT) == "string" and #EVENT >= 1 and #EVENT <= 8, "EVENT must be a 1-8 char event name")
end

-- KIND 'save': Load Game -> slot 1 -> (card check) -> save SAVE (1-3) -> "ロードしますか？" (cursor on いいえ: left,
-- circle) -> the hub; then circle (予定) until the week screen flag: arrival proves the save loaded with no error.
SAVE = SAVE or 1
local SAVE_LOAD = { {6, "circle"}, {900, "-"} }
for _ = 2, SAVE do SAVE_LOAD[#SAVE_LOAD + 1] = {6, "down"}; SAVE_LOAD[#SAVE_LOAD + 1] = {40, "-"} end
for _, s in ipairs({ {6, "circle"}, {300, "-"}, {6, "left"}, {100, "-"}, {6, "circle"}, {1500, "-"} }) do
  SAVE_LOAD[#SAVE_LOAD + 1] = s
end

route(TITLE)
if KIND == "save" then route(TITLE_SUB.load); route(SAVE_LOAD)
elseif TITLE_SUB[KIND] then route(TITLE_SUB[KIND])
elseif KIND ~= "title" then route(NEWGAME) end
go("newgame")

local last_mode, last_events = nil, nil
L.on_frame(function(n)
  if TRACE then
    local m = string.format("%d/%d", rd16(MODE), rd16(PHASE))
    if m ~= last_mode then L.log(string.format("TRACE mode/phase %s f%d", m, n)); last_mode = m end
    local ids = {}
    for i = 0, 9 do
      local id = rd16(ENTRIES + 8 * i)
      if id ~= 0 and id < 462 then ids[#ids + 1] = rdstr(NAMES + 9 * id, 9) end
    end
    local e = table.concat(ids, ",")
    if e ~= last_events then L.log(string.format("TRACE events %s f%d", e, n)); last_events = e end
  end
  if KIND == "event" and not patched and exe_loaded() then
    local a = (NAMES + 9 * SLOT) & 0x1FFFFF
    for i = 0, 8 do mem[a + i] = i < #EVENT and EVENT:byte(i + 1) or 0 end
    patched = true
    L.log(string.format("WARP patched slot %d -> %s f%d", SLOT, EVENT, n))
  end

  if stage == "newgame" then
    if KIND == "save" then
      if L.route_done() then go("loaded") end
    elseif KIND == "title" or TITLE_SUB[KIND] then
      if L.route_done() then arrive() end
    elseif KIND == "newgame" then
      if rd16(MODE) == 2 and n > 5000 then arrive() end  -- name entry panel
    elseif L.route_done() then
      go("opening")
    end
  elseif stage == "loaded" then
    if week_screen() then
      if not arrived_at then arrived_at = n end
      if n - arrived_at >= 30 then arrive() end
    elseif L.route_done() and n % 60 == 0 then
      L.press("circle", 6)
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
      if KIND == "week" then
        arrive()
      elseif KIND == "battle" then
        -- call battle_start(a0 = index into the battle table at 0x80174BD8, a1 = 0) from the vsync wait loop
        -- (0x800E5D88..0x800E5DCC); it returns to 0x800E5D84, which reloads the loop's v1 the call clobbers.
        local r = PCSX.getRegisters()
        local pc = tonumber(r.pc)
        if pc >= 0x800E5D88 and pc <= 0x800E5DCC then
          assert(rd32(BATTLE_FN) == 0x27BDFFE8, "battle_start moved: no addiu sp at 0x800D08E4")
          L.log(string.format("WARP battle %d (pc was %08x) f%d", BATTLE, pc, n))
          r.GPR.n.a0 = BATTLE
          r.GPR.n.a1 = 0
          r.GPR.n.ra = 0x800E5D84
          r.pc = BATTLE_FN
          go("battle_wait")
          arrived_at = n
        end
      elseif KIND == "exec" then
        local path = assert(EXE_PATHS[EXE], "unknown EXE " .. tostring(EXE))
        local s = find_str(path .. "\0", 0x80030000, 0x80040000)
        assert(s, "exec path string not found in PSX.EXE: " .. path)
        assert(rd32(EXEC_FN) == EXEC_FIRST, "exec() moved: no addiu sp at 0x8003C7D4")
        local r = PCSX.getRegisters()
        L.log(string.format("WARP exec %s (a0=%08x, pc was %08x) f%d", path, s, tonumber(r.pc), n))
        r.GPR.n.a0 = s
        r.pc = EXEC_FN
        go("exec_wait")
      else
        route(WEEK1); go("week1")
      end
    end
  elseif stage == "battle_wait" then
    -- the battle has its own screen; arrival once the week-screen flag has dropped for 300 frames
    if week_screen() then arrived_at = n elseif n - arrived_at >= 300 then arrive() end
  elseif stage == "exec_wait" then
    local pc = tonumber(PCSX.getRegisters().pc)
    if in_loader(pc) then exec_seen = true
    elseif exec_seen then arrive() end
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
    if dt == PROOF then
      L.shot("arrived.png")
      if POST then
        for f, keys in POST:gmatch("(%d+)%s+([%w+%-]+)") do L.press(keys, tonumber(f)) end
      end
    end
    if dt > PROOF and POST and L.route_done() and not post_done then
      post_done = n
      L.shot("post.png")
      L.log(string.format("WARP POST done f%d", n))
    end
    if STATE and (POST and post_done == n or not POST and dt == PROOF + 30) then
      L.save_state(STATE); L.log("WARP state " .. STATE)
    end
    if AFTER == "hold" and dt >= PROOF + 60 and (not POST or post_done) then L.shot("final.png"); L.finish(0) end
    if AFTER == "mash" and dt > 0 and dt % MASH_EVERY == 0 and L.route_done() then L.press("circle", 6) end
  end
end)
