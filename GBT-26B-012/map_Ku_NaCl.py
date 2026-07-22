"""
GBT-26B-012 -- Ku-band (13 GHz) NaCl v=0 J=1-0 OTF map of Sgr B2(N).

Geometry reproduces the GBT Mapping Calculator result for a 6'x6' map at
13.026 GHz (scaled from the 12' run in ../../.. OTFplanning.txt):
    FWHM 56.7" | Nyquist 23.75" | slew 7.42"/s
    row separation 24"  ->  16 rows
    scanDuration 48.5 s/row  ->  ~12.9 min on-source per (single-direction) map
    ~19 s of integration per beam per map   [matches the proposal]

Proposal budget (GBT-26B-012): 10-sigma on the ~30 mK peak => ~3 mK/beam
=> ~2500 s/beam => 131 map repeats => ~28 h on-source, ~36 h with overhead,
split into 12 x 3 h sessions (~11 maps per session).

Each "map" is one single-direction OTF pass; we alternate RA-scanned and
Dec-scanned passes to basketweave (suppresses scan-direction striping)
across the 131 repeats.  Config: VEGAS Mode 4, single 187.5 MHz window on
NaCl v=0 1-0, both Ku beams, in-band frequency switching.
"""

# ---- EDIT to the project's script directory on the GBT system ----
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_Ku_NaCl.py")

# ---- calculator-matched geometry ----
deg      = 1.0
arcsec   = 1/3600.
mapsize  = 6/60.          # 0.1 deg square (encompasses N, M, G0.693)
rowsep   = 24.0*arcsec    # ~Nyquist at 57" beam -> 16 rows over 6'
scanDur  = 48.5           # s per row (6' / 7.42"/s)

# ---- session / pointing control ----
maps_this_session = 11    # ~11 x 12.9 min + pointing ~= 3 h.  131 total.
point_every       = 3     # re-point every 3 maps (~40 min) -- Sgr B2 is low.

for i in range(maps_this_session):

    if i % point_every == 0:
        # Peak + focus near the science frequency, then restore config.
        AutoPeakFocus(frequency=13026.0, beamName="1")
        Configure(PROJPATH + "/config_Ku_NaCl.py")
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
