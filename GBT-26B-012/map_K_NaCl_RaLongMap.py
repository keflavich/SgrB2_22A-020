"""
GBT-26B-012 -- K-band (26 GHz) NaCl v=0 J=2-1 OTF map of Sgr B2(N), KFPA.

Target: map the NaCl 2-1 ABSORPTION against the Sgr B2 continuum and
localize which continuum sources it absorbs against.  Config: VEGAS Mode 4,
single 187.5 MHz window on NaCl v=0 2-1, all 7 KFPA beams, in-band freq sw.

From proposal: (19 s/beam, ~13 min/map) for a 6'x6' map at 26.052 GHz:
    FWHM 28.3" | slew 3.71"/s
    row separation 51.4"  ->  8 rows | scanDuration 97.0 s/row
    ==> 12.9 min on-source per (single-direction) map, ~19 s/beam.
Sample spacing along the scan is 5.9" < FWHM/4 at tint=1.6 s.

10-sigma on the ~15 mK peak => ~3 mK/beam
=> ~6000 s/beam single-beam, ~2200 s/beam with the sqrt(7) KFPA gain =>
116 maps => ~41 h on-source, ~51 h w/ overhead, 17 x 3 h sessions.

Each map is ONE single-direction OTF pass; we ALTERNATE RA- and Dec-scanned
passes to basketweave.  Run verbatim.  Track the cumulative count toward 116.
"""

# assumed to be the same as last time I observed a decade ago...
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_K_NaCl.py")

# ---- calculator-matched geometry (KFPA, 7 beams) ----
arcsec   = 1/3600.
mapsize  = 6/60.          # 0.1 deg square
rowsep   = 51.43*arcsec   # 8 rows over 6'; rotating KFPA fills between rows
rowsep   = 51.43 / 3 * arcsec # 24 rows: I want fully-sampled maps for each beam.  34m per scan is OK
scanDur  = 97.0           # s per row (6' / 3.71"/s) at 1.6s sampling gives 5.9"/sample
# 97s * 21 rows = 34m, so probably there's 5m extra for turnaround?

# One map per SB (the recommended GBT practice).  Pointing is NOT handled
# here -- run pointing_K.py first, and again every ~35-40 min.
Slew("SgrB2N")
Balance()

# RA-scanned rows, stepped in Dec:
RALongMap("SgrB2N",
    hLength = Offset("J2000", mapsize, 0.0, cosv=True),
    vLength = Offset("J2000", 0.0, mapsize, cosv=True),
    vDelta  = Offset("J2000", 0.0, rowsep, cosv=True),
    scanDuration = scanDur,
    beamName = "1")
