"""
GBT-26B-012 -- Ku-band (13 GHz) NaCl J=1-0 OTF map of Sgr B2(N).

6' x 6' on-the-fly map centered on SgrB2N, run as an RA/Dec basketweave.
One basketweave pass (RALongMap + DecLatMap) takes ~45-50 min including
turnaround overhead and gives ~80 s of integration per beam.  The proposal
target is ~4 mK rms per beam (native ~0.13 km/s, smoothed to ~1 km/s),
which needs ~3600 s per point => ~40 h total => repeat the basketweave
~45 times across the semester.

Sequence per scheduling block:
    1. Run pointing_Ku.py first (pointing + focus + Configure).
    2. Run this script (one or more basketweave passes).
    3. Re-run pointing_Ku.py every ~45-60 min.

Mapping strategy follows the GBT pipeline / Langston recommendations used
in our earlier GC Ku maps: no per-scan reference, basketweave in RA & Dec.
"""

# ---- EDIT to the project's script directory on the GBT system ----
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_Ku_NaCl.py")

Slew("SgrB2N")
Balance()

# ---- map geometry ----
amintodeg  = 1/60.
mapsize    = 6.0      # arcmin, square map (encompasses N, M, G0.693)
rowsep     = 15.0/60. # arcmin  (15" ~ FWHM/3.8 at 57" beam; < Nyquist 24")
scanrate   = 8.0      # arcmin/min  -> 12.8"/sample at tint=1.6 (< FWHM/4)
scanDur    = mapsize/scanrate * 60.   # 45 s per row

nrep = 1   # number of RA+Dec basketweave passes in THIS block; increase to
           # fill the scheduled time (~48 min per pass).

for i in range(nrep):

    # Rows scanned in RA, stepped in Dec:
    RALongMap("SgrB2N",
        hLength = Offset("J2000", mapsize*amintodeg, 0.0, cosv=True),
        vLength = Offset("J2000", 0.0, mapsize*amintodeg, cosv=True),
        vDelta  = Offset("J2000", 0.0, rowsep, cosv=True),
        scanDuration = scanDur,
        beamName = "1")

    # Rows scanned in Dec, stepped in RA (basketweave, suppresses stripes):
    DecLatMap("SgrB2N",
        hLength = Offset("J2000", mapsize*amintodeg, 0.0, cosv=True),
        vLength = Offset("J2000", 0.0, mapsize*amintodeg, cosv=True),
        hDelta  = Offset("J2000", rowsep, 0.0, cosv=True),
        scanDuration = scanDur,
        beamName = "1")
