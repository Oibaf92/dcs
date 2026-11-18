# Missioni

## `Test_siria.miz`

Missione di prova sulla mappa Siria (1 giugno 1999, 08:00, durata prevista 2 ore). Strike/SEAD blu da Incirlik contro un SA-6 vicino a Raqqa. Il giocatore pilota BUD 1-1 (F-15E).

### Pattuglie rosse (CAP)

Il rosso difende il nord della Siria **senza sapere da dove arriverà il nemico**. L'area delle operazioni è il poligono disegnato nell'editor (Polygon-3, livello Author). I vertici sono stimati da uno screenshot con un errore di circa 10 km: 36,55N 37,15E · 36,57N 39,30E · 35,75N 40,10E · 35,10N 39,20E · 34,95N 37,05E · 34,75N 36,40E · 35,70N 36,10E. Le pattuglie seguono un copione fisso di priorità che cambiano, come se arrivassero segnalazioni diverse durante la missione. Ogni cambio turno va in un'area diversa.

- **Pattuglie attive:** dal minuto 22 ci sono sempre 2–3 pattuglie in zona (tra WP3 e WP5), in media 2,2. Nei primi 20 minuti la copertura cresce, perché gli aerei partono da fermi.
- **Inizio ricerca (WP3):** 100 km prima del circuito, lungo la rotta di arrivo, per ingaggiare già durante l'avvicinamento. Alcuni WP3 cadono sul bordo sud del poligono o appena fuori: la ricerca si attiva prima di entrare nell'area.
- **Raggio di ingaggio:** Su-27 85 km, MiG-23 55 km.
- **Velocità in attesa:** Su-27 600 km/h, MiG-23 550 km/h.

| Area | Centro circuito | Lunghezza |
|---|---|---|
| Diga di Tabqa – Raqqa (SA-6) | 35,85N 38,70E | 45 km |
| Aleppo – Al-Bab | 36,00N 37,35E | 40 km |
| Manbij – attraversamenti dell'Eufrate | 36,10N 38,05E | 40 km |
| Tal Abyad – valle del Balikh | 36,05N 39,30E | 45 km |
| Hama – Idlib, valle dell'Oronte (fianco ovest) | 35,45N 36,80E | 40 km |
| Eufrate a est di Raqqa (fianco est) | 35,75N 39,50E | 45 km |

I circuiti stanno dentro il poligono, ad almeno 23 km dal bordo.

| Fase | Volo | Aerei | Area | Partenza | Attesa | Quota | Asse circuito | In zona (min, stima) | Abilità |
|---|---|---|---|---|---|---|---|---|---|
| 1 – allarme generale | RED CAP 1 | 4× Su-27 | Tabqa – Raqqa | 08:00 | 35′ | FL260 | 060°/240° | 21–69 | Excellent, High, High, Good |
| 1 – allarme generale | RED CAP 2 | 2× MiG-23MLD | Aleppo | 08:00 | 25′ | FL180 | 080°/260° | 20–57 | High, Good |
| 2 – tracce sul confine nord | RED CAP 3 | 4× MiG-23MLD | Manbij | 08:35 | 22′ | FL210 | 035°/215° | 54–88 | High, Good, Good, Average |
| 2 – tracce sul confine nord | RED CAP 4 | 2× Su-27 | Tal Abyad | 08:35 | 35′ | FL290 | 115°/295° | 62–109 | High, Good |
| 3 – segnalazioni sui fianchi | RED CAP 5 | 3× MiG-23MLD | Hama – Idlib | 09:10 | 25′ | FL160 | 160°/340° | 86–123 | Good, Good, Average |
| 3 – segnalazioni sui fianchi | RED CAP 6 | 3× Su-27 | Eufrate a est di Raqqa | 09:10 | 40′ | FL240 | 020°/200° | 95–148 | High, Good, Average |

I Su-27 partono da Al-Dumayr e i MiG-23 da Sayqal. Le aree più a est sono assegnate ai Su-27, perché un MiG-23 laggiù avrebbe poco carburante per l'attesa.

Cosa è stato modificato:

- **Voli esistenti** RED CAP 1 e 2: WP3–WP5, il raggio di ingaggio, il circuito (quota, velocità, durata), l'orario di partenza, le abilità e il numero di aerei.
- **Voli nuovi** RED CAP 3–6: copie dei due voli esistenti, con lo stesso decollo, trasferimento, rientro, carico e livrea. Cambiano solo le stesse voci.
- Il resto della missione è identico all'originale.

Parcheggi:

| Base | Posti (etichetta / indice interno) |
|---|---|
| Al-Dumayr | 63/56, 64/7, 65/19, 66/50 |
| Sayqal | 53/1, 52/3, 51/6, 50/5 |

- Sono posti della stessa fila. Indici e coordinate vengono dai dati della mappa Siria della libreria `pydcs`, che coincidono esattamente con i posti già usati nella missione originale.
- I voli della stessa base partono ad almeno 35 minuti di distanza, quindi riusano gli stessi posti quando il volo precedente è già partito.

Note:

- Il circuito d'attesa va avanti e indietro tra WP4 e WP5. La durata è un tempo fisso, ma gli AI rientrano prima se scendono sotto la soglia di carburante.
- I tempi "in zona" includono circa 5 minuti stimati per rullaggio e decollo.
- Le priorità sono a copione e non reagiscono agli eventi della missione.
