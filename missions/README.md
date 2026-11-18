# Missioni

## `Test_siria.miz`

Missione di prova sulla mappa Siria (1 giugno 1999, 08:00, durata prevista 2 ore).

**Blu**
- Strike/SEAD da Incirlik contro il settore del SA-6 vicino a Raqqa.
- Il giocatore pilota BUD 1-1 (F-15E).
- Un E-3A (`Aerial-1`) orbita sopra la Turchia meridionale.

**Rosso**, a sud e a ovest del **FLOT**, la linea tratteggiata "FLOT" nel livello Author dell'editor:
- SA-6 `SAM_RED-SA-6-1`;
- tre EWR 55G6;
- artiglieria Msta con supporto e 2S6 Tunguska vicino al SA-6;
- sei voli CAP.

### Pattuglie rosse (CAP)

Il rosso difende il fronte **senza sapere da dove attaccherà il nemico**. Le pattuglie seguono un copione fisso di priorità che cambiano, e ogni cambio turno va in un settore diverso.

- **Posizione dei circuiti:** tutti dal lato rosso del FLOT, tra 27 e 67 km dietro la linea, dentro l'area delle operazioni. L'area è il poligono disegnato nell'editor, con vertici stimati da uno screenshot (errore di circa 10 km).
- **Assi dei circuiti:** seguono più o meno l'andamento locale del FLOT, con 10–25° di variazione.
- **Raggio di ingaggio:** Su-27 75 km, MiG-23 50 km. In questo modo non inseguono oltre circa 25 km al di là della linea.
- **Inizio ricerca (WP3):** 100 km prima del circuito, lungo la rotta di arrivo.
- **Pattuglie attive:** dal minuto 22 ci sono sempre almeno 2 pattuglie in zona (tra WP3 e WP5), in media 2,3.

| Settore | Centro circuito | Lunghezza |
|---|---|---|
| Raqqa – settore del SA-6 | 35,50N 38,95E | 45 km |
| Aleppo – fronte di Azaz | 36,25N 37,15E | 40 km |
| Manbij – ansa dell'Eufrate | 35,85N 37,70E | 40 km |
| Eufrate a est di Raqqa | 35,38N 39,20E | 45 km |
| Idlib – fronte dell'Hatay | 35,72N 36,62E | 40 km |
| Diga di Tabqa | 35,50N 38,40E | 45 km |

| Fase | Volo | Aerei | Settore | Partenza | Attesa | Quota | Asse | In zona (min, stima) | Abilità |
|---|---|---|---|---|---|---|---|---|---|
| 1 – allarme generale | RED CAP 1 | 4× Su-27 | Raqqa – SA-6 | 08:00 | 35′ | FL260 | 115°/295° | 21–69 | Excellent, High, High, Good |
| 1 – allarme generale | RED CAP 2 | 2× MiG-23MLD | Aleppo | 08:00 | 20′ | FL180 | 090°/270° | 22–54 | High, Good |
| 2 – pressione su Eufrate e fianco est | RED CAP 3 | 4× MiG-23MLD | Manbij | 08:35 | 22′ | FL210 | 038°/218° | 52–86 | High, Good, Good, Average |
| 2 – pressione su Eufrate e fianco est | RED CAP 4 | 2× Su-27 | Eufrate a est di Raqqa | 08:35 | 35′ | FL290 | 080°/260° | 56–104 | High, Good |
| 3 – fronte ovest e diga | RED CAP 5 | 3× MiG-23MLD | Idlib | 09:05 | 25′ | FL160 | 110°/290° | 83–121 | Good, Good, Average |
| 3 – fronte ovest e diga | RED CAP 6 | 3× Su-27 | Tabqa | 09:05 | 40′ | FL240 | 095°/275° | 84–136 | High, Good, Average |

I Su-27 partono da Al-Dumayr e i MiG-23 da Sayqal. Le durate dei MiG-23 sono tenute sotto il carburante utile stimato (circa 27 minuti su Aleppo).

Cosa è stato modificato sui voli:

- **Voli esistenti** RED CAP 1 e 2: WP3–WP5, il raggio di ingaggio, il circuito (quota, velocità, durata), l'orario di partenza, le abilità e il numero di aerei.
- **Voli nuovi** RED CAP 3–6: copie dei due voli esistenti, con lo stesso decollo, trasferimento, rientro, carico e livrea.

Parcheggi:

| Base | Posti (etichetta / indice interno) |
|---|---|
| Al-Dumayr | 63/56, 64/7, 65/19, 66/50 |
| Sayqal | 53/1, 52/3, 51/6, 50/5 |

- Indici e coordinate vengono dai dati della mappa Siria della libreria `pydcs`, verificati sui posti già usati nella missione originale.
- I voli della stessa base partono ad almeno 30 minuti di distanza e riusano gli stessi posti.

### IADS

La missione carica lo script [`iads/iads.lua`](../iads/README.md) con la configurazione [`Test_siria_iads_config.lua`](Test_siria_iads_config.lua). Entrambi i file sono incorporati nel `.miz` e caricati dal trigger **MISSION START** chiamato "IADS", prima la configurazione e poi lo script.

| Ruolo | Gruppo | Note |
|---|---|---|
| SAM | `SAM_RED-SA-6-1` | SA-6, portata 25 km, mobile: si sposta dopo il tiro |
| Sensore radar | `RED_EWR-1` | 55G6, Tabqa |
| Sensore radar | `RED_EWR-2` | 55G6, Manbij |
| Sensore radar | `RED_EWR-3` | 55G6, Al-Bab |

- **Radar del SA-6:** resta spento finché un EWR non vede un bersaglio entro l'85% della sua portata.
- **EWR distrutti:** se cadono tutti, il SA-6 fa brevi ricerche con il proprio radar.
- **Tunguska (`RED_AAA-1`):** non è nella rete e resta autonoma come difesa ravvicinata.
- **`IADS_DEBUG = true`:** mostra a schermo ogni accensione e spegnimento. Per il gioco va messo a `false`.
- **Se modifichi `iads.lua` o la configurazione:** va aggiornata la copia dentro il `.miz`. Il modo più semplice è ricaricare il file nell'azione DO SCRIPT FILE del trigger.

Note:

- Il circuito d'attesa va avanti e indietro tra WP4 e WP5. La durata è un tempo fisso, ma gli AI rientrano prima se scendono sotto la soglia di carburante.
- I tempi "in zona" includono circa 5 minuti stimati per rullaggio e decollo.
- Le priorità sono a copione e non reagiscono agli eventi della missione.
