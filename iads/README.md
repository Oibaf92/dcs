# IADS per DCS World — rete di difesa aerea "senza onniscienza"

Script Lua per DCS World che gestisce i radar dei SAM come una vera rete di difesa aerea integrata.
Le batterie tengono il radar spento e lo accendono solo quando la rete ha davvero visto un
bersaglio. Estratto dalla campagna dinamica "Fuoco sul Levante 1989"; funziona da solo, senza
MOOSE, MIST o altri script.

Come funziona il codice internamente (stato, ciclo, eventi, prova): [DOCUMENTAZIONE.md](DOCUMENTAZIONE.md).

## Cosa fa
- **Radar spenti di default.** All'avvio tutti i SAM della configurazione vanno in allarme GREEN
  con emissioni spente. Una batteria si accende quando una traccia della rete entra nell'85% della
  sua portata, e si spegne 45 s dopo l'ultimo bersaglio in portata.
- **Niente onniscienza.** La rete conosce solo i bersagli che i suoi sensori rilevano davvero
  (`Controller:getDetectedTargets`): radar di sorveglianza, AWACS, osservatori a terra e SAM già
  accesi. Orizzonte radar e rilievo li calcola DCS: chi vola basso dietro una montagna non viene
  visto e non fa accendere niente.
- **Ritardi.** L'allarme arriva alla batteria dopo 8 s, più il ritardo del sensore che l'ha visto.
  Ogni tipo di radar ha il suo profilo (vedi "Profili per tipo di radar"): un vecchio P-19 aggiunge
  4 s; un E-2C passa il 70% dei contatti, con 20 s in più. Il sorteggio è uno per contatto: un
  aereo che l'AWACS non passa resta ignoto alla rete finché l'AWACS lo segue, e viene sorteggiato
  di nuovo solo se l'AWACS lo perde per più di 30 s e poi lo ritrova.
- **Guida dei missili.** Dopo un lancio il radar resta acceso per il tempo di guida del sistema
  (SA-2 90 s, SA-3 60, SA-5 180, SA-6 60, SA-8 30, Hawk 60): niente missili persi perché la
  batteria si è spenta da sola.
- **Missili antiradar.** Quando viene lanciato un antiradar (AGM-88, AGM-45, AGM-122, Kh-58,
  Kh-25MP), la rete reagisce solo se in quel momento un suo radar vede l'aereo che lancia: un EWR,
  un SAM acceso o un AWACS (se passa quel contatto alla rete, vedi "Ritardi"); gli osservatori a vista
  non contano. Chi lancia basso dietro il rilievo o fuori copertura non provoca reazioni. Spengono il
  radar dopo 3-8 s le batterie minacciate: quella bersaglio e quelle accese entro 100 km davanti al
  lanciatore (±45° dalla prua), con una probabilità che dipende dal tipo di SAM (per esempio SA-2
  75%/40%, SA-15 20%/10%; per i tipi non elencati 65%/30%). Le batterie della coalizione che lancia
  non reagiscono mai. Il silenzio dura 60-120 s.
- **Spostamento dopo il tiro.** I SAM mobili, 90 s dopo aver sparato, si spostano di 0,8-1,5 km
  fuori strada a radar spento, poi tornano operativi. Se hanno ancora missili da guidare, anche
  sparati dopo il primo, lo spostamento aspetta la fine della guida.
- **Rete cieca.** Se nessun sensore della coalizione è vivo (distrutti, non ancora attivati, o
  nessuno configurato), le batterie accendono il proprio radar per 30 s circa ogni 5 minuti,
  esponendosi agli HARM. Le ricerche sono sfalsate: ogni batteria fa la prima a un istante a caso
  entro 5 minuti, poi ogni 3,5-6,5 minuti, così la rete non si accende tutta insieme. Nel `dcs.log`
  compare una riga quando la rete diventa cieca e quando torna ad avere sensori.
- **Riserva.** Le batterie con `riserva = true` restano spente finché la rete non perde la prima
  batteria.
- **Gruppi che compaiono dopo.** Un SAM ad attivazione ritardata, creato durante la missione o
  ricreato con lo stesso nome dopo essere stato distrutto entra nella rete quando compare, a radar
  spento. Finché non c'è resta in attesa: non conta come batteria distrutta e non sveglia le riserve.

Il carico sul simulatore è basso: un solo controllo della rete ogni 10 s più un gestore
degli eventi di lancio e di nascita delle unità.

## Requisiti
- DCS World 2.9 (provato con 2.9.31, Syria). Non serve modificare `MissionScripting.lua`.
- Un gruppo per batteria: radar di scoperta, radar di tiro e lanciatori **nello stesso gruppo**
  (per esempio SA-2: `SNR_75V`, `p-19 s-125 sr`, lanciatori `S_75M_Volhov`).
- Sensori: ogni sensore è un gruppo. Lo script interroga **la prima unità** del gruppo, quindi in
  un gruppo radar o AWACS il radar deve essere l'unità 1.
- I nomi dei gruppi nel Mission Editor devono coincidere esattamente con quelli della configurazione.
  Un gruppo con il nome sbagliato non entra mai nella rete: nel `dcs.log` compare
  `[IADS] <nome>: gruppo non presente, in attesa (...)`. Se la riga riguarda un gruppo che dovrebbe
  esistere fin dall'inizio, controlla il nome.

## Installazione nella missione
1. Copia `iads.lua` e il tuo file di configurazione (parti da `esempio_config.lua`) dove preferisci.
2. Nel Mission Editor crea un trigger:
   - tipo **MISSION START**, nessuna condizione;
   - azione 1: **DO SCRIPT FILE** → il file di configurazione;
   - azione 2: **DO SCRIPT FILE** → `iads.lua`.

   L'ordine conta: la configurazione deve essere caricata prima di `iads.lua`. In alternativa la
   configurazione può stare in un'azione **DO SCRIPT** incollata direttamente.
3. Salva e vola. Nel `dcs.log` deve comparire una riga per coalizione:
   `[IADS] coalizione 1: N batterie, radar spenti`, e una riga per batteria e per sensore con il
   profilo riconosciuto (`[IADS] SA-6 Bekaa: nella rete, radar spento; profilo Kub 1S91 str, ...`).
   "di riserva" vuol dire che
   nessun tipo di unità del gruppo è nelle tabelle.

Con `IADS_DEBUG = true` ogni accensione e spegnimento compare a schermo; i messaggi vanno sempre
nel `dcs.log` con il prefisso `[IADS DEBUG]`.

## Configurazione
```lua
IADS_DATI = {
  [1] = {                                   -- 1 = rossi, 2 = blu
    sam = {
      ["nome gruppo"] = { tipo = "sa6", portata = 25000, mobile = true, riserva = false },
      -- facoltativi: p_harm = 0.6, p_vicine = 0.3   (vincono sul profilo del tipo)
    },
    sensori = {
      ["nome gruppo"] = "radar" | "awacs" | "vista",
      -- oppure: ["nome gruppo"] = { ruolo = "awacs", p_passa = 0.6, ritardo = 25 }
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
| `p_harm`, `p_vicine` | facoltativi: probabilità di silenzio della batteria, se bersaglio o minacciata |
| sensore `p_passa`, `ritardo` | facoltativi (forma a tabella): probabilità che il dato arrivi alla rete e secondi in più |

### Profili per tipo di radar
Le probabilità dipendono dal tipo di unità DCS presente nel gruppo, letto con `getTypeName()`.
Lo script prende il primo tipo del gruppo che compare nelle tabelle `PROFILI_SAM` e
`PROFILI_SENSORI` in testa a `iads.lua`. Un valore scritto nella configurazione del gruppo vince
sulla tabella; un tipo non elencato usa i valori di riserva.

| SAM | Tipo DCS | Silenzio se bersaglio | Se minacciata |
|---|---|---|---|
| SA-2 | `SNR_75V` | 0.75 | 0.40 |
| SA-3 | `snr s-125 tr` | 0.70 | 0.35 |
| SA-5 | `RPC_5N62V` | 0.50 | 0.25 |
| SA-6 | `Kub 1S91 str` | 0.60 | 0.30 |
| SA-8 | `Osa 9A33 ln` | 0.40 | 0.20 |
| SA-11 | `SA-11 Buk SR 9S18M1`, `SA-11 Buk LN 9A310M1` | 0.50 | 0.25 |
| SA-10 | `S-300PS 40B6M tr` | 0.40 | 0.15 |
| SA-15 | `Tor 9A331` | 0.20 | 0.10 |
| I-Hawk | `Hawk tr` | 0.60 | 0.30 |
| Patriot | `Patriot str` | 0.30 | 0.15 |
| altri | — | 0.65 | 0.30 |

| Sensore | Tipo DCS | Passa | Ritardo in più |
|---|---|---|---|
| P-19 come EWR | `p-19 s-125 sr` | 1.0 | 4 s |
| P-14 | `1L13 EWR` | 1.0 | 2 s |
| 55G6 | `55G6 EWR` | 1.0 | 0 |
| AN/FPS-117 | `FPS-117` | 1.0 | 0 |
| A-50 | `A-50` | 0.80 | 15 s |
| E-3 | `E-3A` | 0.85 | 10 s |
| E-2C | `E-2C` | 0.70 | 20 s |
| altri radar | — | 1.0 | 0 |
| altri AWACS | — | 0.70 | 20 s |

I valori sono una prima stima da regolare in gioco. I nomi dei tipi vanno verificati nel `dcs.log`:
per i sistemi di mod va aggiunta una riga con il loro nome.

Portate usate nella campagna (metri): SA-2 40000, SA-3 22000, SA-5 150000, SA-6 25000,
SA-8 10000, I-Hawk 35000.

### Parametri regolabili (in testa a `iads.lua`)
| Costante | Valore | Effetto |
|---|---|---|
| `CICLO` | 10 s | intervallo tra due controlli della rete |
| `RITARDO_RETE` | 8 s | ritardo dall'avvistamento alla batteria |
| `RITARDO_AWACS`, `P_AWACS` | 20 s, 0.7 | ritardo in più e probabilità di passaggio per gli AWACS di tipo non elencato |
| `ATTIVAZIONE` | 0.85 | frazione della portata entro cui la batteria si accende |
| `TENUTA` | 45 s | radar acceso dopo l'ultimo bersaglio in portata |
| `P_HARM`, `P_HARM_VICINE` | 0.65, 0.3 | probabilità di silenzio (bersaglio, minacciata) per i SAM di tipo non elencato |
| `PROFILI_SAM`, `PROFILI_SENSORI` | tabelle | profili per tipo di unità DCS (vedi sopra) |
| `PORTATA_HARM`, `CONO_HARM` | 100 km, 45° | distanza dal lanciatore e angolo dalla sua prua entro cui una batteria accesa è minacciata |
| `SPENTO_HARM` | 60-120 s | durata del silenzio dopo un antiradar |
| `GUIDA` | per tipo | secondi di radar acceso dopo un lancio |
| `RICERCA_OGNI`, `RICERCA_DURATA` | 300 s, 30 s | ricerca autonoma della rete cieca |
| `RICERCA_SCARTO` | 0.3 | variazione casuale dell'intervallo tra due ricerche (±30%) |
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
spegnimento quando il bersaglio esce dalla portata, silenzio dopo un HARM, nessuna reazione a un HARM
lanciato da un aereo che la rete non vede, silenzio solo per le batterie minacciate e mai per quelle di
chi lancia, nessuna accensione per armi rilevate, spostamento dopo il tiro, ricerca autonoma con la rete
cieca.
```
pip install lupa
python3 test/prova_iads.py
```
