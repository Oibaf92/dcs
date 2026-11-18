-- Configurazione IADS per missions/Test_siria.miz: caricare PRIMA di iads/iads.lua.
-- I nomi tra parentesi quadre sono i nomi dei GRUPPI nel Mission Editor.

IADS_DEBUG = true   -- messaggi a schermo a ogni accensione/spegnimento; mettere false in gioco

IADS_DATI = {
  [1] = {   -- coalizione rossa
    sam = {
      -- SA-6 vicino a Raqqa, circa 6 km dietro il FLOT
      ["SAM_RED-SA-6-1"] = { tipo = "sa6", portata = 25000, mobile = true, riserva = false },
    },
    sensori = {
      ["RED_EWR-1"] = "radar",   -- 55G6, Tabqa
      ["RED_EWR-2"] = "radar",   -- 55G6, Manbij
      ["RED_EWR-3"] = "radar",   -- 55G6, Al-Bab
    },
  },
}
