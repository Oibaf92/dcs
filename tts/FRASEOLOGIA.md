# Fraseologia radio per i testi TTS

Le comunicazioni sono in inglese (le voci incluse sono inglesi). Piper legge il testo così com'è:
come lo scrivi, così lo pronuncia. Queste regole servono a farlo suonare come una vera radio.

## Regole di scrittura per Piper

| Scrivi | Non scrivere | Perché |
|---|---|---|
| `three four zero` | `340` | le cifre si leggono una per una in rotte e azimut |
| `twenty thousand` | `20000`, `FL200` | quote in migliaia di piedi |
| `angels twenty` | `angels 20` | quota amica in migliaia di piedi |
| `one one` | `1-1`, `11` | i nominativi si leggono cifra per cifra |
| `niner` | `nine` | pronuncia radio standard (opzionale) |
| `R T B`, `S A M`, `I P` | `RTB`, `SAM` | le sigle senza spazi vengono lette come parole |
| `five zero zero knots` | `500kts` | |
| `two seven zero` (decimali: `two five one point zero`) | `251.0` | frequenze |

- Virgola = pausa breve, punto = pausa lunga. Usali per separare i blocchi informativi.
- Frasi corte. Una picture lunga è meglio divisa in più file (risposta iniziale + gruppi).
- Ascolta sempre il risultato: alcune parole (codici brevity, nomi) vanno scritte "come si
  dicono". Es. `bulls eye` se `bullseye` viene male, `B R A` se `BRAA` viene letto strano.

## Struttura di una chiamata

`<chi viene chiamato>, <chi chiama>, <messaggio>`

```
Viper one one, Overlord, picture clean.
Overlord, Viper one one, checking in, request picture.
```

Nominativi tipici: AWACS `Overlord`, `Magic`, `Darkstar`, `Wizard`, `Focus`; tanker `Texaco`,
`Arco`, `Shell`; JTAC `Axeman`, `Pontiac`, `Warrior`.

## Riferimenti di posizione

| Formato | Ordine | Esempio |
|---|---|---|
| **Bullseye** (per tutti) | bullseye, rotta, distanza (nm), quota | `bullseye three four zero, forty five, twenty thousand` |
| **BRAA** (per un singolo aereo) | rotta, distanza, quota, aspetto | `BRAA two seven zero, thirty, angels fifteen, hot` |

Aspetto del bersaglio: `hot` (verso di te), `flank` / `flanking north`, `beam` / `beaming south`,
`drag` / `cold` (si allontana).

Quote: `high` (oltre 40.000 ft), `low` (sotto 10.000 ft), oppure il numero.

## Codici brevity più usati

| Codice | Significato |
|---|---|
| `picture` | situazione aerea generale |
| `picture clean` | nessun contatto |
| `bogey dope` | chiede il contatto più vicino (BRAA) |
| `declare` | chiede l'identificazione di un contatto |
| `hostile` / `bandit` / `bogey` / `friendly` / `neutral` | ostile autorizzato / ostile / sconosciuto / amico / neutrale |
| `group`, `single`, `heavy` (3+), `contacts` | composizione |
| `pop up` | gruppo comparso all'improvviso |
| `commit` / `committing` | si va a ingaggiare |
| `engaged` / `defensive` | in combattimento / difensivo |
| `spike` | ricevitore radar che indica un radar nemico agganciato |
| `mud spike` | radar di terra (SAM) |
| `fox one / two / three` | lancio di missile (semiattivo / IR / attivo) |
| `splash` | abbattimento confermato |
| `magnum` | lancio di missile antiradar |
| `winchester` | munizioni finite |
| `bingo` / `joker` | carburante per rientrare / carburante di riserva |
| `R T B` | rientro alla base |
| `tally` / `no joy` | ho il contatto in vista / non lo vedo |
| `visual` / `blind` | vedo il gregario / non lo vedo |
| `wilco` / `copy` | eseguirò / ricevuto |
| `say again` | ripeti |
| `fence in` / `fence out` | ingresso / uscita dalla zona ostile |
| `push` | cambio di frequenza o inizio dell'azione |

## Modelli pronti

Sostituisci `<...>`. Formato per `battute.txt`: `nome | voce | testo`.

### AWACS

```
awacs_checkin_ack | ryan-high | <Viper one one>, Overlord, radar contact, picture clean.
awacs_picture_1 | ryan-high | <Viper one one>, Overlord, picture, single group, bullseye <three four zero>, <forty five>, <twenty thousand>, track <south>, hostile.
awacs_picture_2 | ryan-high | <Viper one one>, Overlord, picture, two groups, azimuth <twelve>. North group, bullseye <...>, <...>, <...>, hostile. South group, bullseye <...>, <...>, <...>, hostile.
awacs_bogey_dope | ryan-high | <Viper one one>, Overlord, single group, BRAA <three four zero>, <forty>, <twenty thousand>, hot, hostile.
awacs_threat | ryan-high | <Viper one one>, Overlord, threat, BRAA <zero one zero>, <twenty>, low, hot, hostile.
awacs_declare_friendly | ryan-high | <Viper one one>, Overlord, friendly.
awacs_vector_tanker | ryan-high | <Viper one one>, Overlord, Texaco is <two two zero>, <sixty>, angels <twenty two>.
```

### Pilota / gregario

```
lead_checkin | lessac-medium | Overlord, <Viper one one>, flight of <two>, <F sixteen>s, checking in, angels <twenty>.
wing_tally | lessac-medium | <Viper one two>, tally, two bandits, nose, low.
wing_fox3 | lessac-medium | <Viper one two>, fox three, north group.
wing_defending | lessac-medium | <Viper one two>, defending, spike, <three> o'clock! | 0.85
wing_winchester | lessac-medium | <Viper one two>, winchester.
wing_joker | lessac-medium | <Viper one two>, joker fuel.
```

### JTAC / attacco al suolo

```
jtac_ready | ryan-medium | <Viper one one>, <Axeman>, type two control, ready to copy nine line?
jtac_target | ryan-medium | Target, <two> T seventy twos, in the open, <three hundred> meters east of the bridge, marked by laser, code <one six eight eight>.
jtac_cleared | ryan-medium | <Viper one one>, cleared hot.
jtac_bda | ryan-medium | Good hits, target destroyed.
```

### ATIS

Modello standard del repo. **Senza orario**: così lo stesso file vale per tutta la missione e
non servono più versioni quasi uguali. Velocità `1.0` (più scandito del default) e in DCS va
trasmesso con `RADIO TRANSMISSION` in **loop** (vedi [DCS.md](DCS.md)). Se cambia il meteo o la
pista, nuovo file con la lettera successiva (`Bravo`, `Charlie`, ...).

```
atis_<aeroporto>_<lettera> | ryan-high | <Batumi> information <Alpha>. Runway in use, <one three>. Wind, <one two zero> degrees, <eight> knots. Visibility, <one zero> kilometers. Clouds, <scattered>, <three thousand> feet. Temperature, <one eight>. Dew point, <one two>. Q N H, <one zero one three>. Transition altitude, <six thousand> feet. <Bird activity in the vicinity of the airfield.> Advise on initial contact you have information <Alpha>. | 1.0
```

- Vento calmo: `Wind, calm.`; visibilità oltre 10 km: `Visibility, one zero kilometers or more.`
- Cielo sereno: `Sky clear.` al posto di `Clouds, ...`
- La riga di avviso (`Bird activity...`) è facoltativa: toglila o sostituiscila
  (es. `Runway one three, work in progress.`).

### Partenza (Ground → Tower → Approach)

Modello standard del repo. Una voce diversa per ente, così si capisce subito chi parla:
pilota `lessac-medium`, Ground `alan-low`, Tower `ryan-medium`, Approach `ryan-high`.
Coerente con l'ATIS: stessa lettera, pista e QNH. **Il pilota non dice mai quote, velocità né distanze**:
le sue battute restano valide qualunque cosa assegni il controllore. Nomi `depNN_...` per tenerli in ordine.
In DCS: un trigger per battuta, con ritardo pari alla durata della battuta precedente + 1 s.

```
dep01_pilota_startup | lessac-medium | <Kutaisi> Ground, <Viper one one>, flight of <two>, <F sixteens>, on parking, with information <Alpha>, request startup.
dep02_ground_startup | alan-low | <Viper one one>, <Kutaisi> Ground, startup approved, Q N H <one zero one five>, call ready for taxi.
dep03_pilota_taxi | lessac-medium | <Kutaisi> Ground, <Viper one one>, ready for taxi.
dep04_ground_taxi | alan-low | <Viper one one>, taxi to holding point, runway <zero seven>, via taxiway <alpha>. Q N H <one zero one five>.
dep05_pilota_readback | lessac-medium | Taxi to holding point, runway <zero seven>, via <alpha>, Q N H <one zero one five>, <Viper one one>.
dep06_ground_handoff | alan-low | <Viper one one>, at holding point, contact <Kutaisi> Tower, <two six three decimal zero>. Good day.
dep07_pilota_tower | lessac-medium | <Kutaisi> Tower, <Viper one one>, holding point runway <zero seven>, ready for departure.
dep08_tower_lineup | ryan-medium | <Viper one one>, <Kutaisi> Tower, runway <zero seven>, line up and wait.
dep09_pilota_readback | lessac-medium | Line up and wait, runway <zero seven>, <Viper one one>.
dep10_tower_takeoff | ryan-medium | <Viper one one>, wind <zero eight zero> degrees, <six> knots, runway <zero seven>, cleared for takeoff.
dep11_pilota_readback | lessac-medium | Cleared for takeoff, runway <zero seven>, <Viper one one>.
dep12_tower_handoff | ryan-medium | <Viper one one>, contact <Kutaisi> Approach, <two five zero decimal five>. Good day.
dep13_pilota_approach | lessac-medium | <Kutaisi> Approach, <Viper one one>, airborne, climbing.
dep14_approach_climb | ryan-high | <Viper one one>, <Kutaisi> Approach, radar contact. Climb flight level <two zero zero>, turn <right> heading <one two zero>.
dep15_pilota_readback | lessac-medium | <Right> heading <one two zero>, <Viper one one>.
```

Le frequenze sono indicative: usa quelle dell'aeroporto in DCS.

### Arrivo (Approach → Tower → Ground), ILS o overhead

Modello standard del repo, stesse voci della partenza. Parte comune all'inizio (`arr0x`), poi una
delle due varianti, poi parte comune dopo l'atterraggio (`arr9x`). Come nella partenza **il
pilota non dice mai quote, velocità né distanze**.

- **Overhead** (`ovh`): il più tipico per caccia in formazione con bel tempo.
- **ILS** (`ils`): con meteo brutto o visibilità ridotta.

Comune, contatto con Approach:
```
arr01_pilota_checkin | lessac-medium | <Kutaisi> Approach, <Viper one one>, flight of <two>, with information <Alpha>, for landing.
arr02_approach_descend | ryan-high | <Viper one one>, <Kutaisi> Approach, radar contact. Descend <six thousand> feet, Q N H <one zero one five>. Say type of approach.
```

Variante ILS:
```
ils03_pilota_request | lessac-medium | Q N H <one zero one five>, request I L S, runway <zero seven>, <Viper one one>.
ils04_approach_vector | ryan-high | <Viper one one>, turn right heading <zero nine zero>, descend <three thousand> feet, vectors for I L S approach, runway <zero seven>.
ils05_pilota_readback | lessac-medium | Right heading <zero nine zero>, <Viper one one>.
ils06_approach_cleared | ryan-high | <Viper one one>, turn left heading <zero five zero>, cleared I L S approach, runway <zero seven>, report established.
ils07_pilota_readback | lessac-medium | Left heading <zero five zero>, cleared I L S approach, runway <zero seven>, wilco, <Viper one one>.
ils08_pilota_established | lessac-medium | <Viper one one>, established, localizer runway <zero seven>.
ils09_approach_handoff | ryan-high | <Viper one one>, contact <Kutaisi> Tower, <two six three decimal zero>. Good day.
ils10_pilota_tower | lessac-medium | <Kutaisi> Tower, <Viper one one>, established I L S, runway <zero seven>.
ils11_tower_land | ryan-medium | <Viper one one>, <Kutaisi> Tower, wind <zero eight zero> degrees, <six> knots, runway <zero seven>, cleared to land.
ils12_pilota_readback | lessac-medium | Cleared to land, runway <zero seven>, <Viper one one>.
```

Variante overhead break:
```
ovh03_pilota_request | lessac-medium | Q N H <one zero one five>, request overhead, runway <zero seven>, <Viper one one>.
ovh04_approach_initial | ryan-high | <Viper one one>, proceed direct initial, runway <zero seven>, descend <two thousand five hundred> feet, report field in sight.
ovh05_pilota_readback | lessac-medium | Direct initial, runway <zero seven>, wilco, <Viper one one>.
ovh06_pilota_field | lessac-medium | <Viper one one>, field in sight.
ovh07_approach_handoff | ryan-high | <Viper one one>, contact <Kutaisi> Tower, <two six three decimal zero>. Good day.
ovh08_pilota_tower | lessac-medium | <Kutaisi> Tower, <Viper one one>, flight of <two>, initial, runway <zero seven>, for the overhead.
ovh09_tower_break | ryan-medium | <Viper one one>, <Kutaisi> Tower, runway <zero seven>, <left> break approved, report base, gear down.
ovh10_pilota_base | lessac-medium | <Viper one one>, base, gear down, full stop.
ovh11_tower_land | ryan-medium | <Viper one one>, wind <zero eight zero> degrees, <six> knots, runway <zero seven>, cleared to land.
ovh12_pilota_readback | lessac-medium | Cleared to land, runway <zero seven>, <Viper one one>.
```

Comune, dopo l'atterraggio:
```
arr90_tower_vacate | ryan-medium | <Viper one one>, vacate <left> when able, contact <Kutaisi> Ground, <two five nine decimal zero>.
arr91_pilota_readback | lessac-medium | Vacate <left>, Ground <two five nine decimal zero>, <Viper one one>.
arr92_pilota_ground | lessac-medium | <Kutaisi> Ground, <Viper one one>, runway vacated, request taxi to parking.
arr93_ground_taxi | alan-low | <Viper one one>, <Kutaisi> Ground, taxi to parking via taxiway <alpha>.
arr94_pilota_readback | lessac-medium | Taxi to parking via <alpha>, <Viper one one>.
```

Frequenze, lato del break e disponibilità dell'ILS sono indicativi: controllali sull'aeroporto in DCS.

### Torre / ATC

```
tower_takeoff | ryan-medium | <Viper one one>, <Batumi> tower, runway <one three>, wind <one two zero> at <eight>, cleared for takeoff.
tower_landing | ryan-medium | <Viper one one>, runway <one three>, cleared to land.
```
