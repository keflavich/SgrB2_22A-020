"""
GBT-26B-012 -- K-band (26 GHz) NaCl J=2-1 OTF map of Sgr B2(N).

6' x 6' on-the-fly map centered on SgrB2N, run as an RA/Dec basketweave
with the KFPA (7 beams).  Target: map the NaCl 2-1 ABSORPTION against the
Sgr B2 continuum and localize which continuum sources it absorbs against.

Proposal sensitivity target ~4-6 mK rms per beam (native fine, smoothed to
~1 km/s), reached most efficiently with in-band frequency switching and
reference averaging: ~25 h total (see README / proposal technical.txt).

Sequence per scheduling block:
    1. Run pointing_K.py first (pointing + focus + Configure).
    2. Run this script (one or more basketweave passes).
    3. Re-run pointing_K.py every ~30-45 min (K-band decorrelates faster).

NOTE (KFPA sampling): with 7 beams the effective footprint differs from a
single beam.  Confirm the beam list and row spacing against the current
KFPA Observer's Guide; the values below sample the ~29" central beam and
the extra beams densify further.
"""

# ---- EDIT to the project's script directory on the GBT system ----
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_K_NaCl.py")

Slew("SgrB2N")
Balance()

# ---- map geometry ----
amintodeg  = 1/60.
mapsize    = 6.0      # arcmin, square map
rowsep     = 10.0/60. # arcmin  (10" < Nyquist ~12" at 29" beam)
scanrate   = 4.0      # arcmin/min  -> 6.4"/sample at tint=1.6 (< FWHM/4)
scanDur    = mapsize/scanrate * 60.   # 90 s per row

nrep = 1   # RA+Dec basketweave passes in THIS block; increase to fill time.

for i in range(nrep):

    # Rows scanned in RA, stepped in Dec:
    RALongMap("SgrB2N",
        hLength = Offset("J2000", mapsize*amintodeg, 0.0, cosv=True),
        vLength = Offset("J2000", 0.0, mapsize*amintodeg, cosv=True),
        vDelta  = Offset("J2000", 0.0, rowsep, cosv=True),
        scanDuration = scanDur,
        beamName = "1")

    # Rows scanned in Dec, stepped in RA (basketweave):
    DecLatMap("SgrB2N",
        hLength = Offset("J2000", mapsize*amintodeg, 0.0, cosv=True),
        vLength = Offset("J2000", 0.0, mapsize*amintodeg, cosv=True),
        hDelta  = Offset("J2000", rowsep, 0.0, cosv=True),
        scanDuration = scanDur,
        beamName = "1")
