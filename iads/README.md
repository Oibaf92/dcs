# IADS per DCS World — rete di difesa aerea "senza onniscienza"

Script Lua per DCS World che gestisce i radar dei SAM come una vera rete di difesa aerea integrata.
Le batterie tengono il radar spento e lo accendono solo quando la rete ha davvero visto un
bersaglio. Estratto dalla campagna dinamica "Fuoco sul Levante 1989"; funziona da solo, senza
MOOSE, MIST o altri script.

## Cosa fa
- **Radar spenti di default.** All'avvio tutti i SAM della configurazione vanno in allarme GREEN
  con emissioni spente. Una batteria si accende quando una traccia della rete entra nell'85% della
  sua portata, e si spegne 45 s dopo l'ultimo bersaglio in portata.
- **Niente onniscienza.** La rete conosce solo i bersagli che i suoi sensori rilevano davvero
  (`Controller:getDetectedTargets`): radar di sorveglianza, AWACS, osservatori a terra e SAM già
  accesi. Orizzonte radar e rilievo li calcola DCS: chi vola basso dietro una montagna non viene
  visto e non fa accendere niente.
- **Ritardi.** L'allarme arriva alla batteria dopo 8 s; dall'AWACS solo il 70% delle tracce, con
  20 s in più.
- **Guida dei missili.** Dopo un lancio il radar resta acceso per il tempo di guida del sistema
  (SA-2 90 s, SA-3 60, SA-5 180, SA-6 60, SA-8 30, Hawk 60): niente missili persi perché la
  batteria si è spenta da sola.
- **Missili antiradar.** Quando viene lanciato un antiradar (AGM-88, AGM-45, AGM-122, Kh-58,
  Kh-25MP), la batteria bersaglio spegne il radar con probabilità 65% dopo 3-8 s; le batterie
  accese entro 100 km dal lanciatore con probabilità 30%. Il silenzio dura 60-120 s.
- **Spostamento dopo il tiro.** I SAM mobili, 90 s dopo aver sparato, si spostano di 0,8-1,5 km
  fuori strada a radar spento, poi tornano operativi.
- **Rete cieca.** Se tutti i sensori della coalizione sono distrutti, le batterie accendono il
  proprio radar per 30 s ogni 5 minuti, esponendosi agli HARM.
- **Riserva.** Le batterie con `riserva = true` restano spente finché la rete non perde la prima
  batteria.

Il carico sul simulatore è basso: un solo controllo della rete ogni 10 s più un gestore
dell'evento di lancio.

## Requisiti
- DCS World 2.9 (provato con 2.9.31, Syria). Non serve modificare `MissionScripting.lua`.
- Un gruppo per batteria: radar di scoperta, radar di tiro e lanciatori **nello stesso gruppo**
  (per esempio SA-2: `SNR_75V`, `p-19 s-125 sr`, lanciatori `S_75M_Volhov`).
- Sensori: ogni sensore è un gruppo. Lo script interroga **la prima unità** del gruppo, quindi in
  un gruppo radar o AWACS il radar deve essere l'unità 1.
- I nomi dei gruppi nel Mission Editor devono coincidere esattamente con quelli della configurazione.

## Installazione nella missione
1. Copia `iads.lua` e il tuo file di configurazione (parti da `esempio_config.lua`) dove preferisci.
2. Nel Mission Editor crea un trigger:
   - tipo **MISSION START**, nessuna condizione;
   - azione 1: **DO SCRIPT FILE** → il file di configurazione;
   - azione 2: **DO SCRIPT FILE** → `iads.lua`.

   L'ordine conta: la configurazione deve essere caricata prima di `iads.lua`. In alternativa la
   configurazione può stare in un'azione **DO SCRIPT** incollata direttamente.
3. Salva e vola. Nel `dcs.log` deve comparire una riga per coalizione:
   `[IADS] coalizione 1: N batterie, radar spenti`.

Con `IADS_DEBUG = true` ogni accensione e spegnimento compare a schermo; i messaggi vanno sempre
nel `dcs.log` con il prefisso `[IADS DEBUG]`.

## Configurazione
```lua
IADS_DATI = {
  [1] = {                                   -- 1 = rossi, 2 = blu
    sam = {
      ["nome gruppo"] = { tipo = "sa6", portata = 25000, mobile = true, riserva = false },
    },
    sensori = {
      ["nome gruppo"] = "radar" | "awacs" | "vista",
    },
  },
}
```
| Campo | Significato |
|---|---|
| `tipo` | etichetta del sistema: decide il tempo di guida (`sa2`, `sa3`, `sa5`, `sa6`, `sa8`, `hawk`; altro = 60 s) |
| `portata` | portata in metri; si accende entro l'85% |
| `mobile` | `true`: dopo il tiro si sposta (SA-6, SA-8, Hawk) |
| `riserva` | `true`: spenta finché la rete non perde una batteria |
| sensore `radar` | radar di sorveglianza (EWR), rilevamento radar |
| sensore `awacs` | aereo radar, tracce passate in parte e in ritardo |
| sensore `vista` | unità a terra (carri, contraerea, fanteria): rilevamento visivo e ottico |

Portate usate nella campagna (metri): SA-2 40000, SA-3 22000, SA-5 150000, SA-6 25000,
SA-8 10000, I-Hawk 35000.

### Parametri regolabili (in testa a `iads.lua`)
| Costante | Valore | Effetto |
|---|---|---|
| `CICLO` | 10 s | intervallo tra due controlli della rete |
| `RITARDO_RETE` | 8 s | ritardo dall'avvistamento alla batteria |
| `RITARDO_AWACS`, `P_AWACS` | 20 s, 0.7 | ritardo in più e probabilità di passaggio delle tracce AWACS |
| `ATTIVAZIONE` | 0.85 | frazione della portata entro cui la batteria si accende |
| `TENUTA` | 45 s | radar acceso dopo l'ultimo bersaglio in portata |
| `P_HARM`, `P_HARM_VICINE` | 0.65, 0.3 | probabilità di silenzio per la batteria bersaglio e per le vicine |
| `SPENTO_HARM` | 60-120 s | durata del silenzio dopo un antiradar |
| `GUIDA` | per tipo | secondi di radar acceso dopo un lancio |
| `RICERCA_OGNI`, `RICERCA_DURATA` | 300 s, 30 s | ricerca autonoma della rete cieca |
| `ANTIRADAR` | elenco | parti del nome dei missili trattati come antiradar |

## Limiti
- Come bersagli contano solo aerei ed elicotteri; i missili da crociera non accendono la rete.
- La reazione agli antiradar si basa sul nome del tipo di arma: per missili di mod va aggiunto il
  loro nome in `ANTIRADAR`.
- Lo spostamento dopo il tiro cerca un punto su terreno o strada; se non ne trova, la batteria resta
  ferma.
- Lo script comanda i radar con `enableEmission` (dove disponibile) e con lo stato di allarme
  GREEN/RED: un altro script che cambia lo stesso stato di allarme degli stessi gruppi entra in
  conflitto.

## Prova fuori dal gioco
`test/prova_iads.py` esegue lo script in un DCS simulato (`test/mock_dcs.lua`) e controlla:
accensione solo dopo il rilevamento e il ritardo, nessuna accensione per un aereo non rilevato,
spegnimento quando il bersaglio esce dalla portata, silenzio dopo un HARM, spostamento dopo il tiro,
ricerca autonoma con la rete cieca.
```
pip install lupa
python3 test/prova_iads.py
```
