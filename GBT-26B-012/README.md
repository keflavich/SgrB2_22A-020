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
| `config_Ku_NaCl.py` | Ku-band VEGAS config — NaCl **1‑0** ladder (13 GHz, emission) |
| `config_K_NaCl.py` | K-band VEGAS + KFPA config — NaCl **2‑1** ladder (26 GHz, absorption) |
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

Both bands use **in-band frequency switching** (`swmode='sp'`, cal on), one
VEGAS sub-band per NaCl vibrational state. Native resolution is far finer
than needed; smooth to ~0.5–1 km/s in reduction.

- **Ku (1‑0):** 187.5 MHz windows (widest VEGAS mode with <1 km/s res),
  ~0.13 km/s native. v=0 window also holds H79α; v=4 window holds Na³⁷Cl v=1.
  Primary: **NaCl v=0 1‑0 = 13026.061 MHz** (emission).
- **K (2‑1):** 23.44 MHz windows (~270 km/s coverage, matching Sgr B2's
  −100…+100 km/s line-of-sight). v=4 + Na³⁷Cl v=1 share one window.
  Primary: **NaCl v=0 2‑1 = 26051.898 MHz** (absorption).

Line lists are in each config's footer; 1‑0 values are consistent to ~1 km/s
with the VLA project catalog (`../instrument_configurations/KuLineCatalog.txt`).

## Map / sensitivity budget (from proposal + `OTFplanning.txt`)

- Beam FWHM ≈ 57″ (Ku), ≈ 29″ (K). Row spacing 15″ (Ku) / 10″ (K); scan
  rate 8′/min (Ku) / 4′/min (K) keeps <¼-beam smear at `tint=1.6 s`.
- One Ku basketweave ≈ 48 min → ~80 s/beam. Target **~4 mK** needs
  ~3600 s/beam → **~40 h** (≈45 passes).
- K-band target **~4–6 mK**: ~2300 s with freq switching + reference
  averaging → **~25 h**.

## To verify with GBT staff / the config tool before observing

- **VEGAS mode numbers** — confirm the exact mode giving 187.5 MHz/32768 ch
  (Ku) and 23.44 MHz (K); `bandwidth`/`nchan` here should map to those.
- **KFPA** beam list and OTF row spacing for the 7-beam footprint (`map_K`
  uses single-beam sampling logic; the array densifies it). Note 26.05 GHz
  is at the top edge of the KFPA band — check aperture efficiency.
- **Frequency-switch throw** (`swfreq`) and confirmation that freq switching
  vs. total-power OTF is the intended scheme for each band.
- Regenerate the OTF `scanDuration`/row counts with the **GBT Mapping
  Calculator** for the final 6′ geometry (see `OTFplanning.txt`).
