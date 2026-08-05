# GBT-26B-012 — Salt in Sgr B2(N)

ASTRID observing scripts for the GBT mapping proposal that follows up the
22A-020 VLA non-detection of NaCl in Sgr B2(N). We map a **6′ × 6′** region
centered on **Sgr B2(N)** (encompassing Sgr B2(M) and G0.693−0.027) at both
Ku- and K-band on-the-fly (OTF), to localize the extended NaCl emission
(13 GHz, seen by PRIMOS, resolved out by the VLA) and the 26 GHz absorption.

## Files

| File | Purpose |
|------|---------|
| `sgrb2_salt.cat` | ASTRID source catalog (SgrB2N; J2000, LSR) |
| `config_Ku_NaCl.py` | Ku-band VEGAS config — NaCl v=0 **1‑0** (13 GHz, emission) |
| `config_K_NaCl.py` | K-band VEGAS + KFPA config — NaCl v=0 **2‑1** (26 GHz, absorption) |
| `pointing_Ku.py` | Ku pointing + focus + configure |
| `pointing_K.py` | K pointing + focus + configure |
| `map_Ku_NaCl.py` | Ku 6′×6′ OTF basketweave map |
| `map_K_NaCl.py` | K 6′×6′ OTF basketweave map (KFPA) |

## Per-session sequence

Each `map_<band>_NaCl.py` **"self-manages" pointing**: it runs
`AutoPeakFocus` at the start and every `point_every` maps, re-Configures,
`Balance`s, then loops single-direction OTF maps (alternating RA/Dec to
basketweave). So a 3-h session is just:

1. `map_<band>_NaCl.py` — set `maps_this_session` to fill ~3 h.
   (`pointing_<band>.py` remains available for a standalone point/focus check.)
2. Repeat across sessions until the campaign total is reached:
   **131 maps (Ku)** and **116 maps (K)** — track the cumulative count.

Each map is **one single-direction OTF pass**, and the loop **alternates
RA-scanned and Dec-scanned passes** (`i % 2`) so coverage is basketweaved —
orthogonal maps suppress scan-direction striping and 1/f drifts.

We do frequent pointing (every ~30-40m) because of the low elevation.

Scripts are meant to run verbatim; they assume the project directory is
`/users/aginsbur/GBT-26B-012` (`PROJPATH`).
They're easy to split up if we need more granular control while on-sky.

## Spectral setup

As proposed:
**VEGAS Mode 4, 187.5 MHz, ~32768 channels (5.7 kHz), a single spectral
window on the primary line, replicated across all beams, with in-band
frequency switching** (`swmode='sp'`, cal on). 187.5 MHz gives thousands
of km/s of coverage so one wide window suffices and leaves room for a clean
freq-switch throw. Native resolution is far finer than needed so we can smooth
to ~1 km/s in reduction.

- **Ku (1‑0):** 2 beams @ **NaCl v=0 1‑0 = 13026.061 MHz** (emission);
  0.13 km/s native. Throw 11.7 MHz. 
  There is a bright line 17 MHz away we need to avoid.
- **K (2‑1):** 7 KFPA beams @ **NaCl v=0 2‑1 = 26051.898 MHz** (absorption);
  0.065 km/s native. Throw 11.7 MHz.


## Map / sensitivity budget

One map = one single-direction 6′ OTF pass giving integration time ~19
s/beam; alternate RA/Dec across repeats to basketweave.

- **Ku** —  FWHM 57″,
  row sep 24″ (Nyquist), 16 rows, 48.5 s/row → 12.9 min/map.
  10σ on the ~30 mK peak → ~3 mK/beam → ~2500 s/beam → 131 maps →
  ~28 h on-source, ~36 h with overhead → 12 × 3 h sessions.
- **K (KFPA)** — FWHM 28″, row sep 51.4″ is the default but I reduced it by 1/3
  to get fully-sampled maps per beam, 8 rows -> 24 rows, 97 s/row →
  12.9 min/map -> 39m/map. The coarse (~1.8 FWHM) rows could fully sample using
  different beams from the 7-beam KFPA, but I want fully-sampled maps in each
  beam. 10σ on the ~15 mK peak → ~3 mK/beam → ~2200 s/beam (with √7) → 116 maps
  (39 using the fully-sampled approach)
  → ~41 h on-source, ~51 h with overhead → 17 × 3 h sessions.
- Total allocation: 87 h.

## Observing notes / to confirm before submission

- **KFPA calibration:** include a per-session KFPA cal observation (diode
  strengths drift between sessions) — see `pointing_K.py`.
- **Freq-switch throws** are set to clear the line and use an integer
  number of channels: 11.71875 MHz = 187.5/16 = exactly 2048 channels.
  At K that is only **135 km/s**, which does *not* fully clear a
  ±100 km/s absorption complex — switch to 23.4375 MHz (4096 chan,
  270 km/s) if a clean reference is needed.
- Edit `PROJPATH` in each script to the project's GBT script directory.

## ASTRID gotchas (learned the hard way)

- **Config values must be self-contained literals.** `Configure()` evaluates
  each `keyword = value` line in its *own* namespace, so
  `swfreq = 0.0, bandwidth*2**-4` fails with
  `NameError: name 'bandwidth' is not defined`. Same for `bandwidth[0]*...`.
- **`bandwidth` is a single float**, even with multiple `restfreq` values.
- **`swtype = 'fsw'` is required** alongside `swmode = 'sp'`; without it
  nothing is frequency-switched.
- **`beam` takes comma-separated integers** (`'1,2'`), not `'B12'`.
- **Both Rcvr12_18 and the KFPA are circular-polarization** receivers, so
  `pol = 'Circular'`.
- **Always `Balance()`** after the science `Configure()`, on-source, at the
  observing elevation — and always re-`Configure()` after `AutoPeakFocus`,
  which runs its own continuum config.
- **VEGAS bank limits:** dual-beam ⇒ ≤4 banks/beam (so 4 windows × 2 Ku beams
  = 8 banks is exactly at the limit); 5+ beams ⇒ 1 bank/beam (so the 7-beam
  KFPA setup can only have one spectral window).
- Raster legs must be ≥30 s (48.5 s Ku / 97 s K — fine).
