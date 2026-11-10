# Usare i file audio in DCS World

DCS legge `.ogg` (Vorbis) e `.wav`. I file di `genera_voce.py` (`.ogg` mono 44,1 kHz) vanno bene
così come sono. Ogni file usato viene copiato dentro il `.miz` (cartella `l10n/DEFAULT/`):
il `.miz` cresce di conseguenza, quindi niente file inutili.

## 1. Mission Editor (senza script)

Crea un trigger (`ONCE`, `SWITCHED CONDITION`, ...) con la condizione che ti serve
(tempo, unità in zona, flag...) e una di queste azioni:

| Azione | Chi sente | Note |
|---|---|---|
| **SOUND TO ALL** | tutti | non serve sintonizzare nulla: suona "in cuffia" |
| **SOUND TO COALITION** | una coalizione | il caso tipico per l'AWACS amico |
| **SOUND TO COUNTRY** | un paese | |
| **SOUND TO GROUP** | un gruppo | utile in multiplayer: solo il volo interessato |
| **SOUND TO UNIT** | una singola unità | |
| **RADIO TRANSMISSION** | chi è sintonizzato | file, zona di partenza, frequenza (MHz), AM/FM, potenza (W), loop, nome |
| **STOP RADIO TRANSMISSION** | — | ferma una trasmissione col nome dato |

- `SOUND TO ...` è il più semplice e sicuro: il giocatore sente sempre il messaggio.
- `RADIO TRANSMISSION` è il più realistico: si sente solo con la radio sulla frequenza e
  modulazione giuste e in portata dalla zona di partenza (dipende da potenza e linea di vista).
  Con `loop` attivo diventa un "radiofaro" (ATIS, beacon), da fermare con
  `STOP RADIO TRANSMISSION`.
- Sottotitoli: aggiungi nello stesso trigger **MESSAGE TO ALL / TO COALITION / TO GROUP** con il
  testo della battuta e come durata quella stampata da `genera_voce.py` (+1-2 s).
- Sequenze di battute (domanda → risposta): trigger separati con condizione **TIME SINCE FLAG**,
  oppure un flag impostato dal primo trigger e un ritardo pari alla durata del primo file.

### Comando "Transmit Message" sulle unità IA

Su un gruppo IA (ad es. l'AWACS stesso), nelle azioni del waypoint o con il trigger
**AI TASK PUSH**: `Perform command` → **Set Frequency** (frequenza e modulazione), poi
`Perform command` → **Transmit Message** (file, sottotitolo, durata, loop). Il messaggio parte
dalla posizione reale dell'aereo: la portata segue l'aereo che si muove.

## 2. Script Lua (DO SCRIPT / DO SCRIPT FILE)

Prima cosa: **il file deve essere dentro il `.miz`**. Se lo usi solo da script, il Mission Editor
non lo sa e non lo include. Trucco classico: un trigger che non scatta mai (ad es. `ONCE`,
condizione `FLAG IS TRUE` su un flag mai usato) con un'azione `SOUND TO ALL` per ogni file.
Da script il file si indica con il percorso dentro il `.miz`: `"l10n/DEFAULT/nome.ogg"`.

```lua
-- Suono "in cuffia", senza radio
trigger.action.outSound("l10n/DEFAULT/awacs_picture.ogg")
trigger.action.outSoundForCoalition(coalition.side.BLUE, "l10n/DEFAULT/awacs_picture.ogg")
trigger.action.outSoundForGroup(Group.getByName("Viper 1"):getID(), "l10n/DEFAULT/awacs_bogey_dope.ogg")

-- Sottotitolo abbinato (durata in secondi)
trigger.action.outTextForCoalition(coalition.side.BLUE,
  "OVERLORD: Viper 1-1, picture clean.", 6)

-- Trasmissione radio da un punto: si sente solo sintonizzati su 251.000 AM
local p = trigger.misc.getZone("AWACS_TX").point
trigger.action.radioTransmission("l10n/DEFAULT/awacs_picture.ogg", p,
  radio.modulation.AM, false, 251000000, 1000, "awacs_picture")  -- frequenza in Hz, potenza in W
-- trigger.action.stopRadioTransmission("awacs_picture")

-- Trasmissione da un'unità IA (segue l'aereo)
local ctrl = Group.getByName("Overlord"):getController()
ctrl:setCommand({ id = "SetFrequency", params = { frequency = 251000000, modulation = radio.modulation.AM } })
ctrl:setCommand({ id = "TransmitMessage", params = {
  file = "l10n/DEFAULT/awacs_picture.ogg",
  subtitle = "Viper 1-1, Overlord, picture, two groups...",
  duration = 17,      -- secondi: quella stampata da genera_voce.py
  loop = false,
}})
```

Battute in sequenza da script (domanda e risposta):

```lua
local function dopo(sec, file)
  timer.scheduleFunction(function()
    trigger.action.outSoundForCoalition(coalition.side.BLUE, "l10n/DEFAULT/" .. file)
  end, nil, timer.getTime() + sec)
end
dopo(0,   "viper11_request_picture.ogg")
dopo(4.5, "awacs_picture.ogg")          -- 4.5 = durata della prima battuta + pausa
```

## 3. Multiplayer con SRS

Con SimpleRadio Standalone (SRS) i giocatori usano le radio di SRS, non quelle di DCS: i suoni
`SOUND TO ...` arrivano comunque (sono audio di gioco), mentre le trasmissioni radio di DCS
possono non essere sentite sulle radio SRS. Per far "parlare" un file su una frequenza SRS si usa
lo strumento audio esterno di SRS (`DCS-SR-ExternalAudio.exe`, che accetta anche file `.ogg`)
richiamato da script lato server (ad es. STTS o la classe `MSRS` di MOOSE). Richiede la
sanitizzazione di `os`/`io` disattivata nel `MissionScripting.lua` del server: valuta bene la
sicurezza prima di farlo.

## Problemi comuni

| Sintomo | Causa probabile |
|---|---|
| Da script non suona niente | il file non è nel `.miz` (vedi il trucco del trigger fittizio) o percorso sbagliato |
| `RADIO TRANSMISSION` muto | frequenza/modulazione diverse dalla radio, zona troppo lontana, potenza bassa |
| Schiocco a fine file | aumenta `fade_out` in `RADIO` |
| Voce troppo veloce/lenta | `--velocita` (o il quarto campo in `battute.txt`) |
| Messaggi sovrapposti | ritardo tra le battute più corto della durata del file |
