# GBT-26B-012 -- K-band (KFPA) pointing & focus.  Run at the start of each
# session and every ~30-45 min (K-band needs more frequent pointing than
# Ku, especially at Sgr B2's low elevation and during the day).
#
# Nighttime / good-weather scheduling is preferred at 26 GHz.

# ---- EDIT this to the project's script directory on the GBT system ----
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_K_NaCl.py")

Slew("SgrB2N")
# Point/focus with the reference beam near the science frequency.
AutoPeakFocus(frequency=26052.0, beamName="1")

Break("Check pointing & focus solutions, then re-Configure for science.")
Configure(PROJPATH + "/config_K_NaCl.py")
