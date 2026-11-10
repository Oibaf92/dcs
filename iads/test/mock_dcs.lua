-- Ambiente DCS simulato, minimo, per provare iads.lua fuori dal gioco.
MOCK = { testi = {}, timers = {}, handlers = {} }
env = { info = function(m) print("ENV: " .. m) end }
world = { event = { S_EVENT_SHOT = 1 } }
function world.addEventHandler(h) table.insert(MOCK.handlers, h) end
land = { SurfaceType = { LAND = 1, SHALLOW_WATER = 2, WATER = 3, ROAD = 4, RUNWAY = 5 } }
function land.getSurfaceType(p) return 1 end
local tempo = 0
timer = { getTime = function() return tempo end, getAbsTime = function() return 27000 + tempo end,
  scheduleFunction = function(f, a, t) table.insert(MOCK.timers, { f = f, a = a, t = t }) end }
function MOCK.avanza(sec)
  tempo = tempo + sec
  local ancora = true
  while ancora do
    ancora = false
    for i, tm in ipairs(MOCK.timers) do
      if tm.t <= tempo then
        table.remove(MOCK.timers, i)
        local r = tm.f(tm.a, tm.t)
        if r then table.insert(MOCK.timers, { f = tm.f, a = tm.a, t = r }) end
        ancora = true
        break
      end
    end
  end
end
trigger = { action = { outText = function(t) table.insert(MOCK.testi, t); print("TESTO: " .. t) end } }
Group = {}
Unit = {}
Object = { Category = { UNIT = 1, WEAPON = 2, STATIC = 3, BASE = 4, SCENERY = 5, CARGO = 6 } }
function Object.getCategory(o) return o:getCategory() end
