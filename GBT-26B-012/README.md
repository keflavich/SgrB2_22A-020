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

1. `pointing_<band>.py` — point/focus on a nearby calibrator, then re-Configure.
2. `map_<band>_NaCl.py` — run one or more RA/Dec basketweave passes (set `nrep`).
3. Re-run pointing every ~45–60 min (Ku) / ~30–45 min (K). Sgr B2 transits at
   low elevation from Green Bank; K-band prefers night / good weather.

> **Before submitting:** edit `PROJPATH` at the top of each script to the
> project's directory on the GBT filesystem (placeholder: `/users/aginsbur/GBT-26B-012`).

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

## Map / sensitivity budget (from the submitted proposal)

- Beam FWHM ≈ 57″ (Ku), ≈ 29″ (K). Row spacing 15″ (Ku) / 10″ (K); scan
  rate 8′/min (Ku) / 4′/min (K) keeps <¼-beam smear at `tint=1.6 s`.
- **Ku:** 10σ on the ~30 mK peak → ~3 mK rms → ~2500 s/pointing.
  ~29 h on-source, **~36 h** with overhead → **12 × 3 h** sessions.
- **K:** 10σ on the ~15 mK peak → ~3 mK rms → ~6000 s/pointing single-beam,
  ~2200 s with the √7 KFPA gain. ~41 h on-source, **~51 h** with overhead
  → **17 × 3 h** sessions. (Total request **87 h**.)
- The proposal's OTF calculator gave ~19 s/beam per ~12–13 min map, 131
  (Ku) / 116 (K) repeats. Regenerate the exact `scanDuration`/row counts
  with the **GBT Mapping Calculator** for the final geometry; the values
  in the map scripts are a well-sampled starting point.

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
