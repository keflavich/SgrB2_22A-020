# GBT-26B-012 -- Ku-band pointing & focus.  Run at the start of each
# session and every ~45-60 min (or after a large slew / elevation change).
#
# Sgr B2 transits at low elevation from Green Bank; point/focus often.

PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")

# AutoPeakFocus runs its own continuum configuration and auto-selects a nearby
# bright pointing source, so do NOT Configure or Slew to the source first --
# both would be thrown away.  Point near the science line frequency so the
# pointing model is well matched.
AutoPeakFocus(beamName="1")

Break("Check pointing & focus solutions, then re-Configure for science.")

# ALWAYS reconfigure after AutoPeakFocus, then slew on-source and balance
# at the observing elevation.
Configure(PROJPATH + "/config_Ku_NaCl.py")
Slew("SgrB2N")
Balance()
