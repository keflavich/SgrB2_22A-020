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

# ---- session / pointing control ----
maps_this_session = 11    # ~11 x 12.9 min + pointing ~= 3 h.  131 total.
maps_this_session = 50    # let the operator / observer quit at the end of time (50>>length of session, but the ASTRID validator runs each loop so 1000 is a bad idea)
point_every       = 3     # re-point every 3 maps (~40 min); Sgr B2 is low.

for ii in range(maps_this_session):

    if ii % point_every == 0:
        AutoPeakFocus(beamName="1")
        Configure(PROJPATH + "/config_Ku_NaCl.py")
        Slew("SgrB2N")
        Balance()

    # ALTERNATE orthogonal scan directions (basketweave):
    if ii % 2 == 0:
        # RA-scanned rows, stepped in Dec:
        RALongMap("SgrB2N",
            hLength = Offset("J2000", mapsize, 0.0, cosv=True),
            vLength = Offset("J2000", 0.0, mapsize, cosv=True),
            vDelta  = Offset("J2000", 0.0, rowsep, cosv=True),
            scanDuration = scanDur,
            beamName = "1")
    else:
        # Dec-scanned rows, stepped in RA (orthogonal to the above):
        DecLatMap("SgrB2N",
            hLength = Offset("J2000", mapsize, 0.0, cosv=True),
            vLength = Offset("J2000", 0.0, mapsize, cosv=True),
            hDelta  = Offset("J2000", rowsep, 0.0, cosv=True),
            scanDuration = scanDur,
            beamName = "1")
