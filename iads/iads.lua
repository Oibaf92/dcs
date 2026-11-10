--[[
  IADS per DCS World - rete di difesa aerea "senza onniscienza"
  (estratto dalla campagna "Fuoco sul Levante 1989"; istruzioni complete in README.md)

  - i radar di tiro dei SAM stanno SPENTI e si accendono solo quando la rete segnala un bersaglio
    dentro la loro portata, per il tempo necessario;
  - la rete "vede" solo cio' che i suoi sensori rilevano davvero (getDetectedTargets): radar di
    sorveglianza, AWACS, SAM gia' accesi, osservatori a terra a vista. DCS calcola orizzonte radar e
    rilievo: chi vola basso dietro le montagne non viene visto;
  - se i sensori della rete sono distrutti le batterie sono cieche: ogni tanto accendono il proprio
    radar per cercare (esponendosi agli HARM);
  - l'allarme arriva alla batteria con un ritardo; l'AWACS condivide solo in parte, con piu' ritardo;
  - reazione ai missili antiradar solo se un radar della rete (EWR, AWACS, SAM acceso) vede l'aereo
    nel momento del lancio; spengono, con probabilita', le batterie minacciate: quella bersaglio
    (P_HARM) e quelle accese davanti al lanciatore entro PORTATA_HARM (P_HARM_VICINE). Le batterie
    della coalizione che lancia non reagiscono mai;
  - il radar resta acceso finche' guida i propri missili (GUIDA);
  - i SAM mobili (mobile = true) dopo aver sparato si spostano di 0,8-1,5 km a radar spento, non prima
    di 90 s dal tiro e solo quando hanno finito di guidare i missili in volo;
  - le batterie di riserva (riserva = true) restano spente finche' la rete non perde una batteria.

  Configurazione (da caricare PRIMA di questo file):
  IADS_DATI = { [coalizione] = {           -- 1 = rossi, 2 = blu
      sam = { ["nome gruppo"] = { tipo = "sa6", portata = metri, mobile = true, riserva = false }, ... },
      sensori = { ["gruppo EWR"] = "radar", ["gruppo AWACS"] = "awacs", ["gruppo carri"] = "vista", ... } } }
  Facoltativi: nei SAM p_harm e p_vicine; un sensore puo' essere { ruolo = "awacs", p_passa = ..., ritardo = ... }.
  Senza questi valori valgono i profili per tipo di unita' DCS (PROFILI_SAM, PROFILI_SENSORI).
  (accettato anche il nome LEVANTE_IADS usato dalla campagna)
  IADS_DEBUG = true  -> messaggi a schermo quando una batteria accende o spegne il radar.

  Non richiede MOOSE, MIST ne' la modifica di MissionScripting.lua.
]]

-- funziona da solo o insieme a levante_core.lua (che fornisce LEVANTE.debug e LEVANTE.annota)
LEVANTE = LEVANTE or {}
LEVANTE.annota = LEVANTE.annota or function() end
if not LEVANTE.debug then
  LEVANTE.debug = function(m)
    env.info("[IADS DEBUG] " .. m)
    if IADS_DEBUG then trigger.action.outText("IADS: " .. m, 10) end
  end
end


local DATI = IADS_DATI or LEVANTE_IADS or {}
local CICLO = 10                 -- s tra due controlli della rete
local RITARDO_RETE = 8           -- s dall'avvistamento alla batteria
local RITARDO_AWACS = 20         -- s in piu' per i dati dell'AWACS
local P_AWACS = 0.7              -- probabilita' che una traccia AWACS venga passata alla rete
local ATTIVAZIONE = 0.85         -- frazione della portata entro cui la batteria si accende
local TENUTA = 45                -- s di radar acceso dopo l'ultimo bersaglio in portata
local P_HARM, P_HARM_VICINE = 0.65, 0.3
local PORTATA_HARM = 100000      -- m dal lanciatore entro cui una batteria accesa e' minacciata
local CONO_HARM = 45             -- gradi ai lati della prua del lanciatore entro cui una batteria e' minacciata
local GUIDA = { sa5 = 180, sa2 = 90, sa3 = 60, sa6 = 60, sa8 = 30, hawk = 60 }   -- s di guida dopo il lancio
local SPENTO_HARM = { 60, 120 }  -- s di silenzio dopo un antiradar
local RICERCA_OGNI, RICERCA_DURATA = 300, 30   -- batteria cieca: ricerca autonoma
local ANTIRADAR = { "AGM_88", "AGM_45", "AGM_122", "Kh-58", "Kh-25MP", "X_58", "X_25MP", "AGM-88", "AGM-45" }

-- Profili per tipo di unita' DCS (getTypeName). Per ogni gruppo vale il primo tipo del gruppo che
-- compare nella tabella; un valore scritto nella configurazione del gruppo vince sulla tabella;
-- se nessun tipo e' elencato valgono i valori di riserva (P_HARM/P_HARM_VICINE, PROFILO_RUOLO).
-- SAM: p_harm = silenzio se e' la batteria bersaglio, p_vicine = silenzio se e' minacciata.
local PROFILI_SAM = {
  ["SNR_75V"]              = { p_harm = 0.75, p_vicine = 0.40 },   -- SA-2: sito fisso, dottrina di spegnimento
  ["snr s-125 tr"]         = { p_harm = 0.70, p_vicine = 0.35 },   -- SA-3: sito fisso
  ["RPC_5N62V"]            = { p_harm = 0.50, p_vicine = 0.25 },   -- SA-5: spegnere = perdere il missile
  ["Kub 1S91 str"]         = { p_harm = 0.60, p_vicine = 0.30 },   -- SA-6: mobile
  ["Osa 9A33 ln"]          = { p_harm = 0.40, p_vicine = 0.20 },   -- SA-8: corto raggio, mobile
  ["SA-11 Buk SR 9S18M1"]  = { p_harm = 0.50, p_vicine = 0.25 },   -- SA-11
  ["SA-11 Buk LN 9A310M1"] = { p_harm = 0.50, p_vicine = 0.25 },
  ["S-300PS 40B6M tr"]     = { p_harm = 0.40, p_vicine = 0.15 },   -- SA-10: puo' ingaggiare gli antiradar
  ["Tor 9A331"]            = { p_harm = 0.20, p_vicine = 0.10 },   -- SA-15: progettato contro gli antiradar
  ["Hawk tr"]              = { p_harm = 0.60, p_vicine = 0.30 },   -- I-Hawk
  ["Patriot str"]          = { p_harm = 0.30, p_vicine = 0.15 },   -- Patriot: puo' ingaggiare gli antiradar
}
-- Sensori: p_passa = probabilita' che il dato arrivi alla rete, ritardo = s in piu' oltre RITARDO_RETE.
local PROFILI_SENSORI = {
  ["p-19 s-125 sr"] = { p_passa = 1.0,  ritardo = 4 },    -- P-19 usato come EWR: vecchio, tracciamento manuale
  ["1L13 EWR"]      = { p_passa = 1.0,  ritardo = 2 },
  ["55G6 EWR"]      = { p_passa = 1.0,  ritardo = 0 },
  ["FPS-117"]       = { p_passa = 1.0,  ritardo = 0 },
  ["A-50"]          = { p_passa = 0.80, ritardo = 15 },
  ["E-3A"]          = { p_passa = 0.85, ritardo = 10 },   -- collegamento dati migliore
  ["E-2C"]          = { p_passa = 0.70, ritardo = 20 },
}
local PROFILO_RUOLO = {   -- sensori di tipo non elencato
  radar = { p_passa = 1.0,     ritardo = 0 },
  awacs = { p_passa = P_AWACS, ritardo = RITARDO_AWACS },
}

local S = {}   -- stato per coalizione: batterie, tracce
local function dbg(m) LEVANTE.debug(m) end

local function log(msg) env.info("[IADS] " .. msg) end

local function gruppoVivo(nome)
  local g = Group.getByName(nome)
  if g and g:isExist() and g:getSize() > 0 then return g end
  return nil
end

-- primo tipo di unita' del gruppo presente nella tabella: profilo e nome del tipo
local function cercaProfilo(g, tabella)
  for _, u in ipairs(g:getUnits() or {}) do
    local ok, tipo = pcall(function() return u:getTypeName() end)
    if ok and tipo and tabella[tipo] then return tabella[tipo], tipo end
  end
  return nil, nil
end

-- risolve il profilo di un sensore la prima volta che il suo gruppo esiste (anche se attivato dopo)
local function profiloSensore(nome, s, g)
  if s.risolto or s.ruolo == "vista" then return end
  local prof, tipo = cercaProfilo(g, PROFILI_SENSORI)
  local base = PROFILO_RUOLO[s.ruolo] or PROFILO_RUOLO.radar
  prof = prof or base
  s.p_passa = s.cfg.p_passa or prof.p_passa or base.p_passa
  s.ritardo = s.cfg.ritardo or prof.ritardo or base.ritardo
  s.risolto = true
  env.info(string.format("[IADS] sensore %s (%s): profilo %s, passa %.2f, ritardo +%d s",
    nome, s.ruolo, tipo or ("riserva " .. s.ruolo), s.p_passa, s.ritardo))
end

local function centro(g)
  local sx, sz, n = 0, 0, 0
  for _, u in ipairs(g:getUnits() or {}) do
    local p = u:getPoint()
    sx, sz, n = sx + p.x, sz + p.z, n + 1
  end
  if n == 0 then return nil end
  return { x = sx / n, z = sz / n }
end

local function radar(nome, acceso)
  local g = gruppoVivo(nome)
  if not g then return end
  if g.enableEmission then
    pcall(function() g:enableEmission(acceso) end)
  end
  local c = g:getController()
  c:setOption(AI.Option.Ground.id.ALARM_STATE,
    acceso and AI.Option.Ground.val.ALARM_STATE.RED or AI.Option.Ground.val.ALARM_STATE.GREEN)
end

------------------------------------------------------------------------
-- Sensori della rete: solo bersagli realmente rilevati
------------------------------------------------------------------------
-- il sensore passa alla rete questo contatto? Un solo sorteggio (p_passa) per contatto, valido
-- finche' il sensore continua a vederlo; perso per piu' di 3 * CICLO, al ritorno si sorteggia di nuovo
local function passa(s, id, ora)
  if s.p_passa >= 1 then return true end
  local e = s.esiti[id]
  if not e or ora - e.visto > 3 * CICLO then
    e = { passa = math.random() < s.p_passa }
    s.esiti[id] = e
  end
  e.visto = ora
  return e.passa
end

local function raccogliTracce(coal, st, ora)
  local nemico = (coal == 1) and 2 or 1
  local function aggiungi(obj, ritardo, sensore)
    if not obj or not obj.isExist or not obj:isExist() then return end
    -- solo unita': getDetectedTargets puo' restituire anche armi (missili, proiettili), e per
    -- un'arma getDesc().category usa Weapon.Category (MISSILE = 1 come HELICOPTER, SHELL = 0 come AIRPLANE)
    local oko, tipo = pcall(Object.getCategory, obj)
    if not oko or tipo ~= Object.Category.UNIT then return end
    local ok, c = pcall(function() return obj:getCoalition() end)
    if not ok or c ~= nemico then return end
    local okc, cat = pcall(function() return obj:getDesc().category end)
    if not okc or (cat ~= Unit.Category.AIRPLANE and cat ~= Unit.Category.HELICOPTER) then return end
    local id = obj:getName()
    if sensore and not passa(sensore, id, ora) then return end
    local p = obj:getPoint()
    local t = st.tracce[id]
    local pronto = ora + ritardo
    if t and t.pronto < pronto then pronto = t.pronto end
    st.tracce[id] = { x = p.x, y = p.y, z = p.z, visto = ora, pronto = pronto }
  end
  local quanti = 0
  for nome, s in pairs(st.sensori) do
    local ruolo = s.ruolo
    local g = gruppoVivo(nome)
    if g then
      quanti = quanti + 1
      profiloSensore(nome, s, g)
      local u = g:getUnit(1)
      if u then
        local ok, rilevati = pcall(function()
          if ruolo == "vista" then
            return u:getController():getDetectedTargets(Controller.Detection.VISUAL, Controller.Detection.OPTIC)
          end
          return u:getController():getDetectedTargets(Controller.Detection.RADAR)
        end)
        if ok and rilevati then
          for _, r in pairs(rilevati) do
            if ruolo == "vista" then
              aggiungi(r.object, RITARDO_RETE)
            else
              aggiungi(r.object, RITARDO_RETE + s.ritardo, s)
            end
          end
        end
      end
    end
  end
  -- i SAM gia' accesi sono sensori anche loro (senza ritardo per se stessi, con ritardo per gli altri)
  for nome, b in pairs(st.batterie) do
    if b.acceso then
      local g = gruppoVivo(nome)
      local u = g and g:getUnit(1)
      if u then
        local ok, rilevati = pcall(function() return u:getController():getDetectedTargets(Controller.Detection.RADAR) end)
        if ok and rilevati then
          for _, r in pairs(rilevati) do aggiungi(r.object, RITARDO_RETE) end
        end
      end
    end
  end
  -- tracce vecchie e sorteggi dei contatti persi
  for id, t in pairs(st.tracce) do
    if ora - t.visto > 3 * CICLO then st.tracce[id] = nil end
  end
  for _, s in pairs(st.sensori) do
    for id, e in pairs(s.esiti) do
      if ora - e.visto > 3 * CICLO then s.esiti[id] = nil end
    end
  end
  st.sensoriVivi = quanti
end

------------------------------------------------------------------------
-- Ciclo della rete
------------------------------------------------------------------------
local function ciclo(coal, ora)
  local st = S[coal]
  raccogliTracce(coal, st, ora)
  for nome, b in pairs(st.batterie) do
    local g = gruppoVivo(nome)
    if not g then
      st.batterie[nome] = nil
      if not st.batteriaPersa then
        st.batteriaPersa = true
        for n2, b2 in pairs(st.batterie) do
          if b2.riserva then dbg(n2 .. ": la rete ha perso " .. nome .. ", la riserva entra in azione") end
        end
      end
    elseif b.riserva and not st.batteriaPersa then
      -- riserva: resta spenta e nascosta finche' la rete non perde una batteria
    elseif ora >= (b.silenzioFino or 0) and not b.inMovimento then
      local c = centro(g)
      local inPortata = false
      if c then
        for _, t in pairs(st.tracce) do
          if t.pronto <= ora and math.sqrt((t.x - c.x) ^ 2 + (t.z - c.z) ^ 2) < b.portata * ATTIVAZIONE then
            inPortata = true
            break
          end
        end
      end
      if inPortata then
        b.ultimoBersaglio = ora
        if not b.acceso then radar(nome, true); b.acceso = true; dbg(nome .. ": radar ACCESO (bersaglio segnalato dalla rete)") end
      elseif b.acceso and ora - (b.ultimoBersaglio or 0) > TENUTA and ora >= (b.ricercaFino or 0)
             and ora >= (b.guidaFino or 0) then
        radar(nome, false); b.acceso = false
        dbg(nome .. ": radar spento (nessun bersaglio in portata)")
      elseif not b.acceso and st.sensoriVivi == 0 and ora - (b.ultimaRicerca or -1e9) > RICERCA_OGNI then
        -- rete cieca: breve ricerca con il proprio radar
        b.ultimaRicerca, b.ricercaFino = ora, ora + RICERCA_DURATA
        radar(nome, true); b.acceso = true
        dbg(nome .. ": rete cieca, breve ricerca con il proprio radar")
      end
    end
  end
end

------------------------------------------------------------------------
-- Antiradar e spostamento dopo il tiro
------------------------------------------------------------------------
local function eAntiradar(arma)
  local ok, nome = pcall(function() return arma:getTypeName() end)
  if not ok or not nome then return false end
  for _, k in ipairs(ANTIRADAR) do
    if string.find(nome, k, 1, true) then return true end
  end
  return false
end

local function silenzio(nome, b, ora)
  timer.scheduleFunction(function()
    radar(nome, false)
    b.acceso = false
    b.silenzioFino = timer.getTime() + math.random(SPENTO_HARM[1], SPENTO_HARM[2])
  end, nil, ora + math.random(3, 8))
end

-- la rete della coalizione coal vede l'oggetto in questo istante? Solo radar: EWR ("radar") e AWACS,
-- se passano quel contatto alla rete (passa), e SAM accesi; le unita' "vista" no.
local function reteVede(coal, obj)
  local function vede(nome)
    local g = gruppoVivo(nome)
    local u = g and g:getUnit(1)
    if not u then return false end
    local ok, rilevato, visibile = pcall(function()
      return u:getController():isTargetDetected(obj, Controller.Detection.RADAR)
    end)
    return ok and rilevato and visibile
  end
  for nome, s in pairs(S[coal].sensori) do
    if s.ruolo ~= "vista" then
      local g = gruppoVivo(nome)
      if g then profiloSensore(nome, s, g) end
      -- stesso sorteggio della traccia: se il sensore non passa quel contatto, non passa neanche il lancio
      if g and vede(nome) then
        local okn, id = pcall(function() return obj:getName() end)
        if okn and id and passa(s, id, timer.getTime()) then return true end
      end
    end
  end
  for nome, b in pairs(S[coal].batterie) do
    if b.acceso and vede(nome) then return true end
  end
  return false
end

-- batteria accesa minacciata dal lancio: entro PORTATA_HARM e davanti al lanciatore (entro CONO_HARM)
local function minacciata(c, pt, prua)
  local dx, dz = c.x - pt.x, c.z - pt.z
  local d = math.sqrt(dx * dx + dz * dz)
  if d >= PORTATA_HARM then return false end
  if not prua or d == 0 then return true end
  return (dx * prua.x + dz * prua.z) / d >= math.cos(math.rad(CONO_HARM))
end

local function reazioneHarm(e)
  local arma, lanciatore = e.weapon, e.initiator
  if not lanciatore then return end
  local ora = timer.getTime()
  local okp, pt = pcall(function() return lanciatore:getPoint() end)
  if not okp or not pt then return end
  local okc, coalLancio = pcall(function() return lanciatore:getCoalition() end)
  if not okc then coalLancio = nil end
  local prua = nil
  pcall(function()
    local x = lanciatore:getPosition().x
    local m = math.sqrt(x.x * x.x + x.z * x.z)
    if m > 0 then prua = { x = x.x / m, z = x.z / m } end
  end)
  local bersaglio = nil
  pcall(function() local t = arma:getTarget(); bersaglio = t and t:getGroup() and t:getGroup():getName() end)
  for coal, st in pairs(S) do
    -- solo le reti nemiche del lanciatore, e solo se un loro radar lo vede mentre lancia
    if coal ~= coalLancio and reteVede(coal, lanciatore) then
      for nome, b in pairs(st.batterie) do
        if b.acceso then
          local p = 0
          if nome == bersaglio then
            p = b.p_harm
          else
            local g = gruppoVivo(nome)
            local c = g and centro(g)
            if c and minacciata(c, pt, prua) then p = b.p_vicine end
          end
          if p > 0 and math.random() < p then
            silenzio(nome, b, ora)
            LEVANTE.annota("iads_silenzio_harm", { gruppo = nome })
            dbg(nome .. ": missile antiradar rilevato, radar in silenzio")
          end
        end
      end
    end
  end
end

local function spostaDopoTiro(nome, b)
  if b.inMovimento then return end
  local g = gruppoVivo(nome)
  local c = g and centro(g)
  if not c then return end
  for _ = 1, 8 do
    local a, d = math.random() * 2 * math.pi, 800 + math.random() * 700
    local x, z = c.x + d * math.cos(a), c.z + d * math.sin(a)
    local s = land.getSurfaceType({ x = x, y = z })
    if s == land.SurfaceType.LAND or s == land.SurfaceType.ROAD then
      b.inMovimento = true
      radar(nome, false); b.acceso = false
      g:getController():setTask({ id = "Mission", params = { route = { points = {
        { x = c.x, y = c.z, type = "Turning Point", action = "Off Road", speed = 8 },
        { x = x, y = z, type = "Turning Point", action = "Off Road", speed = 8 },
      } } } })
      timer.scheduleFunction(function() b.inMovimento = false end, nil, timer.getTime() + d / 8 + 60)
      LEVANTE.annota("iads_spostamento", { gruppo = nome, metri = math.floor(d) })
      dbg(string.format("%s: si sposta di %d m dopo il tiro", nome, math.floor(d)))
      return
    end
  end
end

local gestore = {}
function gestore:onEvent(e)
  if e.id ~= world.event.S_EVENT_SHOT then return end
  local ok, err = pcall(function()
    if eAntiradar(e.weapon) then reazioneHarm(e) return end
    local g = e.initiator and e.initiator.getGroup and e.initiator:getGroup()
    if not g then return end
    local nome = g:getName()
    for _, st in pairs(S) do
      local b = st.batterie[nome]
      if b then
        -- missile in volo: il radar di tiro deve restare acceso per guidarlo
        b.guidaFino = math.max(b.guidaFino or 0, timer.getTime() + (GUIDA[b.tipo] or 60))
        b.ultimoBersaglio = timer.getTime()
      end
      if b and b.mobile and not b.spostamentoPrevisto then
        b.spostamentoPrevisto = true
        timer.scheduleFunction(function()
          -- missili ancora in volo (anche sparati dopo): lo spostamento aspetta la fine della guida
          local ora = timer.getTime()
          if ora < (b.guidaFino or 0) then
            dbg(string.format("%s: spostamento rinviato di %d s, guida in corso", nome, math.ceil(b.guidaFino - ora)))
            return b.guidaFino + 1
          end
          b.spostamentoPrevisto = false
          spostaDopoTiro(nome, b)
        end, nil, timer.getTime() + 90)
      end
    end
  end)
  if not ok then log("errore evento: " .. tostring(err)) end
end
world.addEventHandler(gestore)

------------------------------------------------------------------------
-- Avvio: tutte le batterie spente
------------------------------------------------------------------------
for coal, d in pairs(DATI) do
  S[coal] = { batterie = {}, tracce = {}, sensori = {}, sensoriVivi = 0 }
  local n = 0
  for nome, cfg in pairs(d.sam or {}) do
    -- probabilita' di silenzio: configurazione del gruppo > tabella per tipo DCS > valori di riserva
    local g = gruppoVivo(nome)
    local prof, tipo = nil, nil
    if g then prof, tipo = cercaProfilo(g, PROFILI_SAM) end
    prof = prof or {}
    local b = { tipo = cfg.tipo, portata = cfg.portata, mobile = cfg.mobile, riserva = cfg.riserva, acceso = false,
                p_harm = cfg.p_harm or prof.p_harm or P_HARM, p_vicine = cfg.p_vicine or prof.p_vicine or P_HARM_VICINE }
    S[coal].batterie[nome] = b
    log(string.format("%s: profilo %s, silenzio bersaglio %.2f, minacciata %.2f",
      nome, tipo or "di riserva", b.p_harm, b.p_vicine))
    pcall(radar, nome, false)
    n = n + 1
  end
  -- sensori: "ruolo" oppure { ruolo = "...", p_passa = ..., ritardo = ... }
  for nome, v in pairs(d.sensori or {}) do
    local cfg = (type(v) == "table") and v or { ruolo = v }
    S[coal].sensori[nome] = { ruolo = cfg.ruolo or "radar", cfg = cfg, esiti = {} }
  end
  log(string.format("coalizione %d: %d batterie, radar spenti", coal, n))
end

local function giro()
  local ora = timer.getTime()
  for coal in pairs(S) do
    local ok, err = pcall(ciclo, coal, ora)
    if not ok then log("errore ciclo: " .. tostring(err)) end
  end
  return ora + CICLO
end
timer.scheduleFunction(function() return giro() end, nil, timer.getTime() + 5)
