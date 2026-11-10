-- Esempio di configurazione per iads.lua: caricare questo file PRIMA di iads.lua.
-- I nomi tra parentesi quadre sono i nomi dei GRUPPI nel Mission Editor (esatti, maiuscole comprese).

IADS_DEBUG = true   -- messaggi a schermo quando una batteria accende/spegne il radar (false in gioco)

IADS_DATI = {
  [1] = {   -- coalizione rossa
    sam = {
      -- tipo: etichetta libera usata per il tempo di guida (sa2, sa3, sa5, sa6, sa8, hawk; altri = 60 s)
      -- portata: metri; la batteria si accende quando una traccia e' entro l'85% di questa distanza
      -- mobile: true per i sistemi che dopo il tiro si spostano (SA-6, SA-8, Hawk)
      -- riserva: true = resta spenta finche' la rete non perde un'altra batteria
      -- p_harm, p_vicine (facoltativi): probabilita' di silenzio se bersaglio / minacciata da un antiradar;
      --   se mancano valgono quelle del tipo di radar del gruppo (PROFILI_SAM in iads.lua)
      ["SA-2 Damasco"]  = { tipo = "sa2", portata = 40000, mobile = false, riserva = false },
      ["SA-3 Damasco"]  = { tipo = "sa3", portata = 22000, mobile = false, riserva = false },
      ["SA-6 Bekaa"]    = { tipo = "sa6", portata = 25000, mobile = true,  riserva = false },
      ["SA-6 Riserva"]  = { tipo = "sa6", portata = 25000, mobile = true,  riserva = true  },
      ["SA-8 Fronte"]   = { tipo = "sa8", portata = 10000, mobile = true,  riserva = false, p_harm = 0.3 },
    },
    sensori = {
      ["EWR Costa"]      = "radar",   -- radar di sorveglianza: rileva con il radar
      ["EWR Antilibano"] = "radar",
      ["AWACS Rosso"]    = "awacs",   -- aereo radar: probabilita' e ritardo dal suo tipo (A-50: 80%, +15 s)
      ["Carri Passo"]    = "vista",   -- unita' a terra: avvistamento a vista/ottico
    },
  },
  [2] = {   -- coalizione blu (facoltativa)
    sam = {
      ["Hawk Jounieh"] = { tipo = "hawk", portata = 35000, mobile = true, riserva = false },
    },
    sensori = {
      -- forma a tabella: valori propri che vincono sul profilo del tipo (PROFILI_SENSORI in iads.lua)
      ["E-2C Lantern"] = { ruolo = "awacs", p_passa = 0.6, ritardo = 25 },
      ["Marines"]      = "vista",
    },
  },
}
