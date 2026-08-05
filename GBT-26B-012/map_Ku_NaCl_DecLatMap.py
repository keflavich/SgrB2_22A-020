"""
GBT-26B-012 -- Ku-band (13 GHz) NaCl v=0 J=1-0 OTF map of Sgr B2(N).

6'x6' map at 13.026 GHz:
    FWHM 56.7" | slew 7.42"/s
    row separation 24"  ->  16 rows | scanDuration 48.5 s/row
    ==> 12.9 min on-source per (single-direction) map, ~19 s/beam.

Proposal plan (GBT-26B-012): 10-sigma on the ~30 mK peak => ~3 mK/beam
=> ~2500 s/beam => 131 maps => ~28 h on-source, ~36 h w/ overhead,
12 x 3 h sessions (~11 maps/session).

Each map is one single-direction OTF pass, and we alternate RA and
Dec passes.

Config: VEGAS Mode 4, single 187.5 MHz window on NaCl v=0 1-0, both Ku beams,
in-band freq sw.

Track the cumulative map count toward 131 across sessions.
"""

PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_Ku_NaCl.py")

# ---- calculator-matched geometry ----
arcsec   = 1/3600.
mapsize  = 6/60.          # 0.1 deg square (encompasses N, M, G0.693)
rowsep   = 24.0*arcsec    # Nyquist at 57" beam -> 16 rows over 6'
scanDur  = 48.5           # s per row (6' / 7.42"/s)

# One map per SB (the recommended GBT practice).  Pointing is NOT handled
# here -- run pointing_Ku.py first, and again every ~40 min.
Slew("SgrB2N")
Balance()

# Dec-scanned rows, stepped in RA (orthogonal to the RALongMap version):
DecLatMap("SgrB2N",
    hLength = Offset("J2000", mapsize, 0.0, cosv=True),
    vLength = Offset("J2000", 0.0, mapsize, cosv=True),
    hDelta  = Offset("J2000", rowsep, 0.0, cosv=True),
    scanDuration = scanDur,
    beamName = "1")
