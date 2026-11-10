"""Prova di iads.lua in DCS simulato (fuori dal gioco). Uso: pip install lupa; python3 test/prova_iads.py
1) la rete rileva un F/A-18 -> l'SA-6 si accende solo dopo il ritardo di rete;
2) un aereo non rilevato (basso dietro le montagne) -> l'SA-6 resta spento anche se e' vicino;
3) bersaglio uscito dalla portata -> spegnimento dopo la tenuta;
4) HARM sull'SA-6 acceso -> silenzio (con probabilita', qui forzata);
5) l'SA-6 spara -> si sposta a radar spento;
6) radar di sorveglianza distrutto -> rete cieca, ricerca autonoma periodica."""
import os
from lupa import lua51

QUI = os.path.dirname(os.path.abspath(__file__))
L = lua51.LuaRuntime()
L.execute(open(os.path.join(QUI, 'mock_dcs.lua'), encoding='utf-8').read())
L.execute('''
Unit.Category = { AIRPLANE = 0, HELICOPTER = 1, GROUND_UNIT = 2 }
Controller = { Detection = { VISUAL = 1, OPTIC = 2, RADAR = 4 } }
AI = { Option = { Ground = { id = { ALARM_STATE = 9 }, val = { ALARM_STATE = { AUTO = 0, GREEN = 1, RED = 2 } } } } }
land.SurfaceType = { LAND = 1, SHALLOW_WATER = 2, WATER = 3, ROAD = 4, RUNWAY = 5 }
land.getSurfaceType = function() return 1 end
STATO = { allarme = {}, compiti = {}, vivi = { ["SA-6 X"] = true, ["EWR"] = true } }
RILEVA = {}          -- RILEVA[nome sensore] = lista di oggetti rilevati
local function aereo(nome, x, z)
  return { getName = function() return nome end, isExist = function() return true end,
           getCoalition = function() return 2 end, getDesc = function() return { category = 0 } end,
           getPoint = function() return { x = x, y = 1000, z = z } end }
end
F18 = aereo("F18", 15000, 0)
BASSO = aereo("BASSO", 5000, 0)
LONTANO = aereo("LONTANO", 80000, 0)
local function gruppo(nome, x, z)
  local ctrl = { setOption = function(_, id, v) STATO.allarme[nome] = v end,
                 setTask = function(_, t) STATO.compiti[nome] = t end,
                 getDetectedTargets = function() local out = {}; for i, o in ipairs(RILEVA[nome] or {}) do out[i] = { object = o } end; return out end }
  local unita = { getPoint = function() return { x = x, y = 0, z = z } end, getController = function() return ctrl end,
                  getGroup = function() return GRUPPI[nome] end }
  return { isExist = function() return STATO.vivi[nome] == true end, getSize = function() return STATO.vivi[nome] and 1 or 0 end,
           getUnits = function() return { unita } end, getUnit = function() return unita end,
           getController = function() return ctrl end, getName = function() return nome end }
end
GRUPPI = { ["SA-6 X"] = gruppo("SA-6 X", 0, 0), ["EWR"] = gruppo("EWR", 30000, 0) }
Group.getByName = function(n) return GRUPPI[n] end
IADS_DATI = { [1] = { sam = { ["SA-6 X"] = { tipo = "sa6", portata = 25000, mobile = true } },
                         sensori = { ["EWR"] = "radar" } } }
math.random = function(a, b) if a then return a end return 0.1 end    -- deterministico
''')
L.execute(open(os.path.join(QUI, "..", "iads.lua"), encoding="utf-8").read().replace("local S = {}", "S = {}"))
ROSSO, VERDE = 2, 1


def passo(sec):
    # il simulatore esegue i timer con l'ora di fine intervallo: avanzare a passi di 1 s come DCS
    for _ in range(sec):
        L.execute('MOCK.avanza(1)')
def allarme():
    return L.eval('STATO.allarme["SA-6 X"]')

passo(6)
assert allarme() == VERDE, 'all\'avvio i radar devono essere spenti'
# 2) aereo vicino ma non rilevato
L.execute('RILEVA["EWR"] = {}')
passo(30)
assert allarme() == VERDE, 'senza rilevamento la batteria non deve accendersi'
# 1) rilevato: acceso solo dopo il ritardo di rete
L.execute('RILEVA["EWR"] = { F18 }')
passo(10)
primo = allarme()
passo(10)
assert allarme() == ROSSO, 'la batteria deve accendersi dopo il ritardo'
print('rilevato: dopo il primo ciclo', 'acceso' if primo == ROSSO else 'spento', '-> poi acceso')
# 3) bersaglio fuori portata -> spegnimento dopo la tenuta
L.execute('RILEVA["EWR"] = { LONTANO }')
passo(80)
assert allarme() == VERDE, 'deve spegnersi quando il bersaglio esce dalla portata'
# 4) HARM sull'SA-6 acceso
L.execute('RILEVA["EWR"] = { F18 }')
passo(30)
assert allarme() == ROSSO
L.execute('''
local harm = { getTypeName = function() return "AGM_88" end,
               getTarget = function() return { getGroup = function() return GRUPPI["SA-6 X"] end } end }
for _, h in ipairs(MOCK.handlers) do h:onEvent({ id = world.event.S_EVENT_SHOT, weapon = harm, initiator = F18 }) end
''')
passo(9)
assert allarme() == VERDE, 'deve spegnersi per l\'HARM'
passo(30)
assert allarme() == VERDE, 'resta in silenzio dopo l\'HARM'
passo(200)
assert allarme() == ROSSO, 'dopo il silenzio torna ad accendersi se il bersaglio c\'e\''
# 5) l'SA-6 spara -> spostamento
L.execute('''
local sam = { getTypeName = function() return "9M336" end }
for _, h in ipairs(MOCK.handlers) do h:onEvent({ id = world.event.S_EVENT_SHOT, weapon = sam,
  initiator = GRUPPI["SA-6 X"]:getUnit(1) }) end
''')
passo(100)
assert L.eval('STATO.compiti["SA-6 X"]') is not None, 'dopo il tiro deve spostarsi'
assert allarme() == VERDE, 'si sposta a radar spento'
# 6) EWR distrutto: rete cieca, ricerca autonoma
passo(400)
L.execute('STATO.vivi["EWR"] = false; RILEVA["EWR"] = {}')
cambi = []
for _ in range(60):
    passo(10)
    cambi.append(allarme())
assert ROSSO in cambi and VERDE in cambi, 'rete cieca: deve accendersi per brevi ricerche'
print('ricerca autonoma: acceso %d cicli su 60' % cambi.count(ROSSO))
print('OK')
