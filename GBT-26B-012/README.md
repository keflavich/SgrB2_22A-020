# GBT-26B-012 — Salt in Sgr B2(N)

ASTRID observing scripts for the GBT mapping proposal that follows up the
22A-020 VLA non-detection of NaCl in Sgr B2(N). We map a **6′ × 6′** region
centered on **Sgr B2(N)** (encompassing Sgr B2(M) and G0.693−0.027) at both
Ku- and K-band on-the-fly (OTF), to localize the extended NaCl emission
(13 GHz, seen by PRIMOS, resolved out by the VLA) and the 26 GHz absorption.

## Files

| File | Purpose |
|------|---------|
| `sgrb2_salt.cat` | ASTRID source catalog (SgrB2N/M, G0.693; J2000, LSR) |
| `config_Ku_NaCl.py` | Ku-band VEGAS config — NaCl v=0 **1‑0** (13 GHz, emission) |
| `config_K_NaCl.py` | K-band VEGAS + KFPA config — NaCl v=0 **2‑1** (26 GHz, absorption) |
| `pointing_Ku.py` | Ku pointing + focus + configure |
| `pointing_K.py` | K pointing + focus + configure |
| `map_Ku_NaCl.py` | Ku 6′×6′ OTF basketweave map |
| `map_K_NaCl.py` | K 6′×6′ OTF basketweave map (KFPA) |

## Per-session sequence

Each `map_<band>_NaCl.py` **self-manages pointing**: it runs
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

Sgr B2 transits at low elevation from Green Bank; the in-loop pointing
cadence (`point_every`) is a **floor**, especially at K-band.

Scripts are meant to run **verbatim**; they assume the project directory is
`/users/aginsbur/GBT-26B-012` (`PROJPATH`).

## Spectral setup

Matches the submitted proposal resource table (`GBT-26B-012.pdf`, p.2):
**VEGAS Mode 4, 187.5 MHz, ~32768 channels (5.7 kHz), a single spectral
window on the primary line, replicated across all beams, with in-band
frequency switching** (`swmode='sp'`, cal on). 187.5 MHz gives thousands
of km/s of coverage — far more than Sgr B2's ~200 km/s — so one wide
window suffices and leaves room for a clean freq-switch throw. Native
resolution is far finer than needed; smooth to ~1 km/s in reduction.

- **Ku (1‑0):** 2 beams @ **NaCl v=0 1‑0 = 13026.061 MHz** (emission);
  0.13 km/s native. Throw 14.305 MHz (2500 ch). Excited‑vib states are
  outside this window and descoped.
- **K (2‑1):** 7 KFPA beams @ **NaCl v=0 2‑1 = 26051.898 MHz** (absorption);
  0.065 km/s native. Throw 28.610 MHz (5000 ch) — clears the ±100 km/s
  complex.

1‑0 values are consistent to ~1 km/s with the VLA project catalog
(`../instrument_configurations/KuLineCatalog.txt`).

## Map / sensitivity budget (matched to the submitted proposal)

One "map" = one single-direction 6′ OTF pass giving ~**19 s/beam**;
alternate RA/Dec across repeats to basketweave.

- **Ku** — geometry reproduces the GBT Mapping Calculator exactly: FWHM 57″,
  row sep **24″** (Nyquist), **16 rows**, **48.5 s/row** → **12.9 min/map**.
  10σ on the ~30 mK peak → ~3 mK/beam → ~2500 s/beam → **131 maps** →
  ~28 h on-source, **~36 h** with overhead → **12 × 3 h** sessions.
- **K (KFPA)** — geometry reproduces the KFPA mapping-calculator output the
  proposal reports: FWHM 28″, row sep **51.4″**, **8 rows**, **97 s/row** →
  **12.9 min/map**. The coarse (~1.8 FWHM) rows fully sample because the
  alt-az GBT **rotates the 7-beam hexagon** through each track and across
  repeats, filling in between rows and giving the √7 gain. 10σ on the ~15 mK
  peak → ~3 mK/beam → ~2200 s/beam (with √7) → **116 maps** → ~41 h
  on-source, **~51 h** with overhead → **17 × 3 h** sessions.
- **Total request: 87 h.**

## Observing notes / to confirm before submission

- **Semester/elevation:** the GBT is expected to be shut down May–Sep for
  the next several summers, leaving Oct–Jan for 26B, when Sgr B2 transits
  in daytime at ≤ ~23° elevation. Treat the pointing cadence as a **floor**
  (≥ every 30 min at K), and prefer the best weather for K-band.
- **KFPA calibration:** include a per-session KFPA cal observation (diode
  strengths drift between sessions) — see `pointing_K.py`.
- **Freq-switch throws** are set to clear the line and use an integer
  number of channels; confirm against the config tool.
- Edit `PROJPATH` in each script to the project's GBT script directory.
