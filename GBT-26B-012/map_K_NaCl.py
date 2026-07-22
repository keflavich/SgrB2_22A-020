"""
GBT-26B-012 -- K-band (26 GHz) NaCl v=0 J=2-1 OTF map of Sgr B2(N), KFPA.

Target: map the NaCl 2-1 ABSORPTION against the Sgr B2 continuum and
localize which continuum sources it absorbs against.  Config: VEGAS Mode 4,
single 187.5 MHz window on NaCl v=0 2-1, all 7 KFPA beams, in-band freq sw.

GEOMETRY -- IMPORTANT, CONFIRM WITH THE KFPA MAPPING CALCULATOR:
The row spacing below (12" = Nyquist for the ~28" central beam) FULLY
samples with a single beam and is therefore always safe, but it does NOT
exploit the 7-beam KFPA footprint -- a single-beam 6' map at this spacing
is ~50 min.  The proposal's sensitivity budget assumes the KFPA sqrt(7)
gain, which comes from WIDENING the row spacing so the array interleaves
(the KFPA branch of the GBT Mapping Calculator outputs the correct value;
scaling the single-beam calc, ~36" rows -> ~18 min/map at ~19 s/beam).
--> Run the KFPA mapping calculator for the final `rowsep`/`scanDur`
    before submission; keep `rowsep = 12"` only as a safe fallback.

Proposal budget (GBT-26B-012): 10-sigma on the ~15 mK peak => ~3 mK/beam
=> ~6000 s/beam single-beam, ~2200 s/beam with the sqrt(7) KFPA gain =>
116 map repeats => ~41 h on-source, ~51 h with overhead, 17 x 3 h sessions.

Each "map" is one single-direction OTF pass; alternate RA/Dec to basketweave.
"""

# ---- EDIT to the project's script directory on the GBT system ----
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_K_NaCl.py")

# ---- geometry (see header: confirm rowsep/scanDur with KFPA calculator) ----
arcsec   = 1/3600.
mapsize  = 6/60.          # 0.1 deg square
rowsep   = 12.0*arcsec    # Nyquist for the 28" central beam (SAFE fallback).
                          # KFPA-array value from the calculator is wider.
scanDur  = 97.0           # s per row (6' / 3.71"/s), single-beam scaling.

# ---- session / pointing control ----
maps_this_session = 7     # tune to ~3 h once the KFPA map time is fixed. 116 total.
point_every       = 2     # re-point every 2 maps -- K-band + low elevation
                          # decorrelate fast; treat ~30 min as a hard floor.

for i in range(maps_this_session):

    if i % point_every == 0:
        AutoPeakFocus(frequency=26052.0, beamName="1")
        Configure(PROJPATH + "/config_K_NaCl.py")
        Slew("SgrB2N")
        Balance()

    if i % 2 == 0:
        # RA-scanned rows, stepped in Dec:
        RALongMap("SgrB2N",
            hLength = Offset("J2000", mapsize, 0.0, cosv=True),
            vLength = Offset("J2000", 0.0, mapsize, cosv=True),
            vDelta  = Offset("J2000", 0.0, rowsep, cosv=True),
            scanDuration = scanDur,
            beamName = "1")
    else:
        # Dec-scanned rows, stepped in RA (basketweave):
        DecLatMap("SgrB2N",
            hLength = Offset("J2000", mapsize, 0.0, cosv=True),
            vLength = Offset("J2000", 0.0, mapsize, cosv=True),
            hDelta  = Offset("J2000", rowsep, 0.0, cosv=True),
            scanDuration = scanDur,
            beamName = "1")
