# GBT-26B-012 -- K-band (KFPA) pointing & focus.  Run at the start of each
# session and every ~30-45 min if no-cal map scripts are used.  (K-band needs
# more frequent pointing than Ku, especially at Sgr B2's low elevation and
# during the day).

PROJPATH = "/users/aginsbur/GBT-26B-012"

Catalog(PROJPATH + "/sgrb2_salt.cat")

# AutoPeakFocus runs its own continuum configuration and picks its own nearby
# bright calibrator, so do NOT Configure or Slew to the source first -- both
# would be thrown away.
# Point/focus near the science frequency.  KFPA beam pairs (3,7) and (4,6) sit
# at equal elevation and are the recommended peak/focus beams; beam 1 (center)
# also works.
AutoPeakFocus(frequency=26052.0, beamName="1")

Break("Check pointing & focus solutions, then re-Configure for science.")

# ALWAYS reconfigure after AutoPeakFocus, then slew on-source and balance
# at the observing elevation.
Configure(PROJPATH + "/config_K_NaCl.py")
Slew("SgrB2N")
Balance()

# KFPA noise-diode strengths drift between sessions -- do a KFPA calibration
# observation each session so Ta* scaling is reliable across all 7 beams.
# (See the KFPA Observer's Guide; typically a short scan on a cal source.)
Break("Perform the per-session KFPA calibration observation before mapping.")
