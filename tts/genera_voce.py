#!/usr/bin/env python3
"""
Genera comunicazioni radio per DCS World: sintesi vocale Piper + effetto radio con ffmpeg.
Output: file .ogg mono pronti per i trigger DCS ("Sound to All", "Radio transmission", ecc.).

Uso singolo:
  python genera_voce.py --voce ryan-high --testo "Viper one one, Overlord, picture clean." --out awacs_clean
Uso batch (un file di battute):
  python genera_voce.py --batch battute.txt
Rigenera una sola battuta del batch:
  python genera_voce.py --batch battute.txt --solo awacs_picture
Solo voce, senza effetto radio:
  python genera_voce.py --batch battute.txt --pulito
"""
import argparse, shutil, subprocess, sys, tempfile, wave
from pathlib import Path

BASE = Path(__file__).resolve().parent
DIR_VOCI = BASE / "voci"
DIR_OUT = BASE / "output"

# Parametri dell'effetto radio (quelli del test approvato)
RADIO = {
    "highpass": 380,        # Hz, taglio basse
    "lowpass": 2700,        # Hz, taglio alte
    "rumore": 0.035,        # ampiezza fruscio di fondo (0 = nessuno)
    "crush_mix": 0.25,      # quanta "sporcizia" digitale (0-1)
    "guadagno": 2.2,
    "pre": 0.25,            # secondi di fruscio prima della voce
    "post": 0.25,           # secondi di fruscio dopo la voce
    "fade_out": 0.12,       # dissolvenza finale (evita lo schiocco)
}


def trova_modello(voce: str) -> Path:
    p = Path(voce)
    if p.suffix == ".onnx" and p.exists():
        return p
    candidati = sorted(DIR_VOCI.rglob(f"*{voce}*.onnx"))
    if not candidati:
        sys.exit(f"Voce '{voce}' non trovata in {DIR_VOCI}. Vedi README per scaricarla.")
    return candidati[0]


def sintetizza(testo: str, modello: Path, wav_out: Path, velocita: float):
    cmd = [sys.executable, "-m", "piper", "-m", str(modello), "-f", str(wav_out),
           "--length-scale", str(velocita), "--sentence-silence", "0.25"]
    r = subprocess.run(cmd, input=testo.encode("utf-8"),
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode != 0:
        sys.exit(f"Errore di Piper:\n{r.stderr.decode('utf-8', 'replace')}")


def durata(path: Path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def effetto_radio(wav_in: Path, ogg_out: Path, r=RADIO) -> float:
    tot = durata(wav_in) + r["pre"] + r["post"]
    ms = int(r["pre"] * 1000)
    filtro = (
        f"[0:a]aresample=44100,adelay={ms}|{ms},apad=pad_dur={r['post']},"
        f"highpass=f={r['highpass']},lowpass=f={r['lowpass']},"
        f"acompressor=threshold=-22dB:ratio=6:attack=5:release=60,"
        f"acrusher=bits=12:mix={r['crush_mix']},volume={r['guadagno']},alimiter=limit=0.9[v];"
        f"[1:a]aresample=44100,highpass=f=300,lowpass=f=3500[n];"
        f"[v][n]amix=inputs=2:duration=shortest:normalize=0,"
        f"afade=t=in:d=0.03,afade=t=out:st={tot - r['fade_out']:.3f}:d={r['fade_out']},"
        f"aformat=channel_layouts=mono[o]"
    )
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(wav_in),
           "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude={r['rumore']}:d={tot:.3f}",
           "-filter_complex", filtro, "-map", "[o]", "-c:a", "libvorbis", "-q:a", "5", str(ogg_out)]
    subprocess.run(cmd, check=True)
    return tot


def solo_conversione(wav_in: Path, ogg_out: Path) -> float:
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(wav_in), "-af", "aresample=44100",
           "-ac", "1", "-c:a", "libvorbis", "-q:a", "5", str(ogg_out)]
    subprocess.run(cmd, check=True)
    return durata(wav_in)


def genera(nome: str, voce: str, testo: str, velocita: float, pulito: bool = False):
    DIR_OUT.mkdir(exist_ok=True)
    modello = trova_modello(voce)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "raw.wav"
        sintetizza(testo, modello, wav, velocita)
        out = DIR_OUT / f"{nome}.ogg"
        sec = solo_conversione(wav, out) if pulito else effetto_radio(wav, out)
    # La durata serve per i messaggi di testo (outText) e per il comando TransmitMessage
    print(f"OK  {out.name:<40} {sec:5.1f} s  ({modello.stem})")


def leggi_batch(path: Path):
    """Righe 'nome | voce | testo [| velocita]'; # = commento."""
    for n, riga in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        riga = riga.strip()
        if not riga or riga.startswith("#"):
            continue
        campi = [x.strip() for x in riga.split("|")]
        if len(campi) not in (3, 4) or not all(campi[:3]):
            sys.exit(f"{path.name}, riga {n}: formato atteso 'nome | voce | testo [| velocita]'")
        nome, voce, testo = campi[:3]
        if " " in nome:
            sys.exit(f"{path.name}, riga {n}: niente spazi nel nome file ('{nome}')")
        velocita = float(campi[3]) if len(campi) == 4 else None
        yield nome, voce, testo, velocita


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", help="file di battute: nome | voce | testo [| velocita]  (una per riga)")
    ap.add_argument("--solo", help="con --batch: genera solo la battuta con questo nome")
    ap.add_argument("--voce", default="ryan-high")
    ap.add_argument("--testo")
    ap.add_argument("--out", help="nome file senza estensione")
    ap.add_argument("--velocita", type=float, default=0.92, help="<1 più veloce, >1 più lento")
    ap.add_argument("--pulito", action="store_true", help="niente effetto radio (solo voce)")
    a = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg non trovato nel PATH. Vedi README.")
    try:
        import piper  # noqa: F401
    except ImportError:
        sys.exit("Piper non installato: pip install piper-tts")

    if a.batch:
        trovate = 0
        for nome, voce, testo, vel in leggi_batch(Path(a.batch)):
            if a.solo and nome != a.solo:
                continue
            trovate += 1
            genera(nome, voce, testo, vel or a.velocita, a.pulito)
        if a.solo and not trovate:
            sys.exit(f"Nessuna battuta '{a.solo}' in {a.batch}")
    elif a.testo and a.out:
        genera(a.out, a.voce, a.testo, a.velocita, a.pulito)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
