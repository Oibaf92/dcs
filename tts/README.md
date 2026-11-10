# Voci radio (TTS) per DCS World

Genera comunicazioni radio (AWACS, wingman, ATC, JTAC...) con voce sintetica **Piper** (offline)
ed effetto radio **ffmpeg**. Output `.ogg` mono 44,1 kHz in `output/`, pronti per i trigger DCS.

| File | Contenuto |
|---|---|
| [`genera_voce.py`](genera_voce.py) | lo script: testo → voce Piper → effetto radio → `.ogg` |
| [`battute.txt`](battute.txt) | elenco delle battute da generare (modificalo tu) |
| [`FRASEOLOGIA.md`](FRASEOLOGIA.md) | come scrivere i testi: numeri, nominativi, codici brevity, modelli pronti |
| [`DCS.md`](DCS.md) | come usare i file in DCS: trigger del Mission Editor e script Lua |

`voci/` (i modelli Piper) e `output/` (i file generati) non sono nel repository: vedi `.gitignore`.

## Installazione (una volta)

1. **Python 3.9+**
2. **Piper**: `pip install piper-tts`
3. **ffmpeg** nel PATH
   - Windows: `winget install Gyan.FFmpeg` (poi riapri il terminale)
   - Linux: `sudo apt install ffmpeg`
4. **Voci**: scarica e scompatta nella cartella `voci/`
   - AWACS (maschile, alta qualità): https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-high.tar.gz
   - Pilota (femminile): https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz
   - Maschile alternativa: https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-medium.tar.gz
   - Altre voci/lingue: https://huggingface.co/rhasspy/piper-voices (servono `.onnx` + `.onnx.json`),
     oppure `python -m piper.download_voices en_US-joe-medium --download-dir voci`

   Struttura attesa: `voci/en-us-ryan-high/en-us-ryan-high.onnx` (+ `.onnx.json`). Va bene anche
   tutto direttamente in `voci/`: lo script cerca in tutte le sottocartelle.
   Su Windows i `.tar.gz` si aprono con 7-Zip o con `tar -xzf file.tar.gz` da terminale.

La voce si indica con una parte del nome del file: `ryan-high` trova `en-us-ryan-high.onnx`.
Con le voci scaricate da Hugging Face il nome è diverso (`en_US-ryan-high.onnx`): scrivi
`en_US-ryan-high` o anche solo `ryan-high`, se non ci sono doppioni.

## Uso

Batch (consigliato) — modifica `battute.txt`, una riga per file: `nome | voce | testo [| velocita]`
```
python genera_voce.py --batch battute.txt
```

Rigenera una sola battuta del batch:
```
python genera_voce.py --batch battute.txt --solo awacs_picture
```

Singola battuta senza file:
```
python genera_voce.py --voce ryan-high --out awacs_clean --testo "Viper one one, Overlord, picture clean."
```

Opzioni:
- `--velocita` (default 0.92): valori più bassi = parlato più veloce. Nel batch si può dare
  per singola riga come quarto campo (es. `0.85` per una chiamata concitata).
- `--pulito`: niente effetto radio, solo voce (utile per annunci a terra o per provare la voce).

Per ogni file lo script stampa la **durata in secondi**: serve per i sottotitoli
(`MESSAGE TO ALL` / `outText`) e per il comando `TransmitMessage` (vedi [DCS.md](DCS.md)).

## Regolare l'effetto radio

In cima a `genera_voce.py` c'è il dizionario `RADIO`:
- `highpass` / `lowpass`: banda (più stretta = più "radio")
- `rumore`: fruscio di fondo (0 per disattivarlo)
- `crush_mix`: sporcizia digitale
- `guadagno`: volume prima del limitatore
- `pre` / `post`: secondi di fruscio prima e dopo la voce (simula l'apertura del microfono)
- `fade_out`: dissolvenza finale (è quella che evita lo schiocco a fine file)

Profili indicativi:

| Effetto | highpass | lowpass | rumore | crush_mix |
|---|---|---|---|---|
| UHF/VHF pulita (AWACS vicino) | 300 | 3400 | 0.015 | 0.10 |
| Standard (default) | 380 | 2700 | 0.035 | 0.25 |
| Radio lontana / disturbata | 500 | 2200 | 0.07 | 0.45 |

## Consigli per i testi

In breve (dettagli e modelli in [FRASEOLOGIA.md](FRASEOLOGIA.md)):
- Numeri scritti come si dicono: `three four zero`, `twenty thousand`, `one one`.
- Virgole e punti = pause naturali, utili per separare i gruppi in una picture.
- Sigle lettera per lettera separate da spazi: `R T B`, `S A M`, `J TAC`.
- Prima chi è chiamato, poi chi chiama: `Viper one one, Overlord, ...`.

## In DCS

Mission Editor → trigger → azione **SOUND TO ALL / SOUND TO COALITION / RADIO TRANSMISSION**
→ seleziona il file `.ogg`. Il file viene incluso automaticamente nel `.miz`.
Tutte le opzioni, incluse quelle da script Lua: [DCS.md](DCS.md).
