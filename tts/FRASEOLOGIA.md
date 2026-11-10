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

### Torre / ATC

```
tower_takeoff | ryan-medium | <Viper one one>, <Batumi> tower, runway <one three>, wind <one two zero> at <eight>, cleared for takeoff.
tower_landing | ryan-medium | <Viper one one>, runway <one three>, cleared to land.
```
