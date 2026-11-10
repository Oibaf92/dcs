"""Prova di iads.lua in DCS simulato (fuori dal gioco). Uso: pip install lupa; python3 test/prova_iads.py
1) la rete rileva un F/A-18 -> l'SA-6 si accende solo dopo il ritardo di rete;
2) un aereo non rilevato (basso dietro le montagne) -> l'SA-6 resta spento anche se e' vicino;
3) bersaglio uscito dalla portata -> spegnimento dopo la tenuta;
4) HARM sull'SA-6 acceso -> silenzio (con probabilita', qui forzata);
5) l'SA-6 spara -> si sposta a radar spento;
6) radar di sorveglianza distrutto -> rete cieca, ricerca autonoma periodica;
7) la rete rileva solo armi (HARM, proiettile) -> l'SA-6 resta spento: contano solo aerei ed elicotteri;
8) HARM lanciato da un aereo che nessun radar della rete vede -> nessuna reazione;
9) HARM senza bersaglio noto da un aereo visto -> si spegne la batteria davanti al lanciatore, non quella
   alle sue spalle, e mai le batterie della coalizione che lancia;
10) profili per tipo di unita' DCS: valore dalla tabella, dalla configurazione del gruppo, di riserva;
11) l'SA-6 spara di nuovo prima dello spostamento -> si sposta solo quando ha finito di guidare;
12) AWACS: un solo sorteggio per contatto. Un contatto non passato resta non passato finche' l'AWACS
    lo segue; perso per piu' di 30 s e ritrovato, viene sorteggiato di nuovo;
13) gruppi non ancora presenti: ad attivazione ritardata o creati durante la missione restano in attesa
    (non sono distrutti, non svegliano le riserve) ed entrano nella rete a radar spento quando compaiono;
    una batteria distrutta che ricompare con lo stesso nome rientra nella rete."""
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
STATO = { allarme = {}, compiti = {}, attivo = { ["SA-6 Tardi"] = false }, vivi = { ["SA-6 X"] = true, ["EWR"] = true, ["SA-8 Dietro"] = true, ["Hawk Blu"] = true,
                                             ["AWACS Blu"] = true, ["SA-6 Tardi"] = true } }
RILEVA = {}          -- RILEVA[nome sensore] = lista di oggetti rilevati
local function aereo(nome, x, z, coal)
  return { getName = function() return nome end, isExist = function() return true end,
           getPosition = function() return { x = { x = -1, y = 0, z = 0 } } end,
           getCategory = function() return Object.Category.UNIT end, getCoalition = function() return coal or 2 end, getDesc = function() return { category = 0 } end,
           getPoint = function() return { x = x, y = 1000, z = z } end }
end
F18 = aereo("F18", 15000, 0)
BASSO = aereo("BASSO", 5000, 0)
LONTANO = aereo("LONTANO", 80000, 0)
INVISIBILE = aereo("INVISIBILE", 15000, 0)   -- nessun radar della rete lo vede
MIG = aereo("MIG", 8000, 1000, 1)              -- rosso, vicino all'Hawk blu
-- armi rilevate: per un'arma getDesc().category e' Weapon.Category (MISSILE = 1, SHELL = 0)
local function arma(nome, cat, x, z)
  return { getName = function() return nome end, isExist = function() return true end,
           getCategory = function() return Object.Category.WEAPON end, getCoalition = function() return 2 end,
           getDesc = function() return { category = cat } end,
           getPoint = function() return { x = x, y = 3000, z = z } end }
end
HARM_VOLO = arma("AGM_88", 1, 10000, 0)
PROIETTILE = arma("M61_20_HE", 0, 5000, 0)
local function gruppo(nome, x, z, tipo)
  local ctrl = { setOption = function(_, id, v) STATO.allarme[nome] = v end,
                 setTask = function(_, t) STATO.compiti[nome] = t end,
                 getDetectedTargets = function() local out = {}; for i, o in ipairs(RILEVA[nome] or {}) do out[i] = { object = o } end; return out end,
                 isTargetDetected = function(_, o) for _, t in ipairs(RILEVA[nome] or {}) do if t == o then return true, true end end
                                                   return false, false end }
  local unita = { getPoint = function() return { x = x, y = 0, z = z } end, getController = function() return ctrl end,
                  getGroup = function() return GRUPPI[nome] end, getTypeName = function() return tipo end,
                  isActive = function() return STATO.attivo[nome] ~= false end }
  return { isExist = function() return STATO.vivi[nome] == true end, getSize = function() return STATO.vivi[nome] and 1 or 0 end,
           getUnits = function() return { unita } end, getUnit = function() return unita end,
           getController = function() return ctrl end, getName = function() return nome end }
end
GRUPPI = { ["SA-6 X"] = gruppo("SA-6 X", 0, 0, "Kub 1S91 str"), ["EWR"] = gruppo("EWR", 30000, 0, "55G6 EWR"),
           ["SA-8 Dietro"] = gruppo("SA-8 Dietro", 30000, 0, "Osa 9A33 ln"),   -- alle spalle di chi lancia da x = 15000 verso -x
           ["Hawk Blu"] = gruppo("Hawk Blu", 5000, 1000, "tipo sconosciuto"),   -- blu, davanti al lanciatore blu
           ["AWACS Blu"] = gruppo("AWACS Blu", 60000, 60000, "E-2C"),           -- profilo E-2C: passa 0.70, +20 s
           ["SA-6 Tardi"] = gruppo("SA-6 Tardi", 0, 20000, "Kub 1S91 str") }    -- attivazione ritardata
CREA_GRUPPO = gruppo   -- per la prova dei gruppi creati durante la missione

Group.getByName = function(n) return GRUPPI[n] end
IADS_DATI = { [1] = { sam = { ["SA-6 X"] = { tipo = "sa6", portata = 25000, mobile = true },
                                 ["SA-8 Dietro"] = { tipo = "sa8", portata = 10000, p_harm = 0.9 },
                                 ["SA-6 Tardi"] = { tipo = "sa6", portata = 25000 },     -- attivazione ritardata
                                 ["SA-3 Nuovo"] = { tipo = "sa3", portata = 22000 } },   -- creato durante la missione
                         sensori = { ["EWR"] = "radar" } },
               [2] = { sam = { ["Hawk Blu"] = { tipo = "hawk", portata = 35000 } },
                       sensori = { ["AWACS Blu"] = "awacs" } } }
CASUALE = 0.1   -- valore restituito da math.random(): deterministico, regolabile dalla prova
math.random = function(a, b) if a then return a end return CASUALE end
''')
L.execute(open(os.path.join(QUI, "..", "iads.lua"), encoding="utf-8").read().replace("local S = {}", "S = {}"))
ROSSO, VERDE = 2, 1


def passo(sec):
    # il simulatore esegue i timer con l'ora di fine intervallo: avanzare a passi di 1 s come DCS
    for _ in range(sec):
        L.execute('MOCK.avanza(1)')
def allarme(nome="SA-6 X"):
    return L.eval('STATO.allarme["%s"]' % nome)

passo(6)
assert allarme() == VERDE, 'all\'avvio i radar devono essere spenti'
# 10) profili per tipo DCS: tabella, valore della configurazione che vince, valori di riserva
def val(espr):
    return L.eval(espr)
assert (val('S[1].batterie["SA-6 X"].p_harm'), val('S[1].batterie["SA-6 X"].p_vicine')) == (0.60, 0.30), 'SA-6: profilo Kub dalla tabella'
assert (val('S[1].batterie["SA-8 Dietro"].p_harm'), val('S[1].batterie["SA-8 Dietro"].p_vicine')) == (0.9, 0.20), \
    'SA-8: p_harm dalla configurazione, p_vicine dalla tabella'
assert (val('S[2].batterie["Hawk Blu"].p_harm'), val('S[2].batterie["Hawk Blu"].p_vicine')) == (0.65, 0.3), 'tipo sconosciuto: riserva'
assert (val('S[1].sensori["EWR"].p_passa'), val('S[1].sensori["EWR"].ritardo')) == (1.0, 0), 'EWR: profilo 55G6'
# 13) gruppi non ancora presenti all'avvio
passo(20)
assert val('S[1].batteriaPersa') is None, 'un gruppo non ancora presente non e\' una batteria distrutta'
assert val('S[1].batterie["SA-6 Tardi"]') is not None and val('S[1].batterie["SA-3 Nuovo"]') is not None, \
    'i gruppi non ancora presenti restano nella configurazione, in attesa'
assert allarme("SA-6 Tardi") is None, 'gruppo non attivo: lo script non lo tocca'
# attivazione ritardata: l'evento di nascita lo fa entrare subito nella rete, a radar spento
L.execute('''
STATO.attivo["SA-6 Tardi"] = true
for _, h in ipairs(MOCK.handlers) do h:onEvent({ id = world.event.S_EVENT_BIRTH, initiator = GRUPPI["SA-6 Tardi"]:getUnit(1) }) end
''')
assert allarme("SA-6 Tardi") == VERDE, 'attivato: entra nella rete a radar spento'
assert (val('S[1].batterie["SA-6 Tardi"].p_harm')) == 0.60, 'attivato: profilo Kub risolto all\'ingresso'
# creato durante la missione, senza evento: entra al ciclo successivo
L.execute('GRUPPI["SA-3 Nuovo"] = CREA_GRUPPO("SA-3 Nuovo", -60000, 0, "snr s-125 tr"); STATO.vivi["SA-3 Nuovo"] = true')
passo(10)
assert allarme("SA-3 Nuovo") == VERDE, 'creato: entra nella rete a radar spento'
assert val('S[1].batteriaPersa') is None
# 7) solo armi rilevate: nessuna accensione
L.execute('RILEVA["EWR"] = { HARM_VOLO, PROIETTILE }')
passo(40)
assert allarme() == VERDE, 'missili e proiettili rilevati non devono accendere la batteria'
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
# 8) HARM sull'SA-6 da un aereo che nessun radar della rete vede: nessuna reazione
L.execute('''
local harm = { getTypeName = function() return "AGM_88" end,
               getTarget = function() return { getGroup = function() return GRUPPI["SA-6 X"] end } end }
for _, h in ipairs(MOCK.handlers) do h:onEvent({ id = world.event.S_EVENT_SHOT, weapon = harm, initiator = INVISIBILE }) end
''')
passo(9)
assert allarme() == ROSSO, 'lanciatore non visto dalla rete: la batteria non deve reagire'
# 9) HARM senza bersaglio noto (getTarget nil) da F18, visto dall'EWR: minacciate solo le batterie davanti
#    al lanciatore; l'Hawk blu, davanti ma della stessa coalizione di chi lancia, non reagisce
L.execute('''
for _, nome in ipairs({ "SA-8 Dietro", "Hawk Blu" }) do
  local coal = (nome == "Hawk Blu") and 2 or 1
  S[coal].batterie[nome].acceso = true; S[coal].batterie[nome].ultimoBersaglio = timer.getTime()
  STATO.allarme[nome] = 2
end
RILEVA["Hawk Blu"] = { F18 }   -- anche se un radar blu "vedesse" il lanciatore, la rete blu non c'entra
local harm = { getTypeName = function() return "AGM_88" end, getTarget = function() return nil end }
for _, h in ipairs(MOCK.handlers) do h:onEvent({ id = world.event.S_EVENT_SHOT, weapon = harm, initiator = F18 }) end
''')
passo(9)
assert allarme() == VERDE, 'batteria davanti al lanciatore: minacciata, deve spegnersi'
assert allarme("SA-8 Dietro") == ROSSO, 'batteria alle spalle del lanciatore: non minacciata'
assert allarme("Hawk Blu") == ROSSO, 'le batterie della coalizione che lancia non reagiscono'
L.execute('RILEVA["Hawk Blu"] = {}')
passo(200)
assert allarme() == ROSSO
# 5) l'SA-6 spara -> spostamento; 11) ma non finche' guida un missile sparato dopo
def spara():
    L.execute('''
local sam = { getTypeName = function() return "9M336" end }
for _, h in ipairs(MOCK.handlers) do h:onEvent({ id = world.event.S_EVENT_SHOT, weapon = sam,
  initiator = GRUPPI["SA-6 X"]:getUnit(1) }) end
''')
spara()                  # t0: spostamento previsto a t0 + 90
passo(80)
spara()                  # t0 + 80: guida (SA-6, 60 s) fino a t0 + 140
passo(15)                # t0 + 95
assert L.eval('STATO.compiti["SA-6 X"]') is None, 'non deve spostarsi mentre guida un missile'
assert allarme() == ROSSO, 'radar acceso per la guida'
passo(50)                # t0 + 145: guida finita
assert L.eval('STATO.compiti["SA-6 X"]') is not None, 'finita la guida deve spostarsi'
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
# 12) AWACS E-2C (passa 0.70): un solo sorteggio per contatto
assert allarme("Hawk Blu") == VERDE
L.execute('CASUALE = 0.9; RILEVA["AWACS Blu"] = { MIG }')   # primo contatto: sorteggio fallito
passo(10)
L.execute('CASUALE = 0.1')                                   # i sorteggi successivi riuscirebbero
passo(60)
assert allarme("Hawk Blu") == VERDE, 'contatto non passato: non deve passare ai cicli successivi'
L.execute('RILEVA["AWACS Blu"] = {}')                        # l'AWACS perde il contatto
passo(40)
L.execute('RILEVA["AWACS Blu"] = { MIG }')                   # ritrovato: nuovo sorteggio, riesce
passo(60)
assert allarme("Hawk Blu") == ROSSO, 'contatto ritrovato dopo 30 s: nuovo sorteggio'
# 13, segue) distrutto: esce dalla rete e sveglia le riserve; ricreato con lo stesso nome: rientra
L.execute('STATO.vivi["SA-3 Nuovo"] = false')
passo(10)
assert val('S[1].batteriaPersa') == True, 'batteria distrutta: la rete la perde'
L.execute('STATO.allarme["SA-3 Nuovo"] = nil; STATO.vivi["SA-3 Nuovo"] = true')
passo(10)
assert allarme("SA-3 Nuovo") == VERDE, 'ricreato con lo stesso nome: rientra nella rete a radar spento'
print('OK')
