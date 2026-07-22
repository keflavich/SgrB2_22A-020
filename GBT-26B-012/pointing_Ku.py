# GBT-26B-012 -- Ku-band pointing & focus.  Run at the start of each
# session and every ~45-60 min (or after a large slew / elevation change).
#
# Sgr B2 transits at low elevation from Green Bank; point/focus often.

# ---- EDIT this to the project's script directory on the GBT system ----
PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")
Configure(PROJPATH + "/config_Ku_NaCl.py")

Slew("SgrB2N")
# AutoPeakFocus auto-selects a nearby bright pointing source; point near
# the science line frequency so the pointing model is well matched.
AutoPeakFocus(frequency=13026.0, beamName="1")

Break("Check pointing & focus solutions, then re-Configure for science.")
Configure(PROJPATH + "/config_Ku_NaCl.py")
