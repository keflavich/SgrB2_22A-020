# =====================================================================
# GBT-26B-012  --  Salt in Sgr B2(N)
# K-band (26 GHz) VEGAS + KFPA configuration: NaCl v=0 J=2-1 (ABSORPTION)
# =====================================================================
# Matches the submitted proposal resource table (GBT-26B-012.pdf, p.2):
#   VEGAS Mode 4, 187.5 MHz bandwidth, ~32768 channels -> 5.7 kHz
#   (0.065 km/s at 26 GHz), a SINGLE spectral window on NaCl v=0 2-1,
#   ALL 7 KFPA beams, in-band frequency switching.
#
# 187.5 MHz gives ~2160 km/s of coverage -- far more than the ~200 km/s
# Sgr B2 line-of-sight needs -- leaving ample room for a frequency-switch
# throw that fully clears the absorption complex (see swfreq below).
# The 7-beam KFPA gives the sqrt(7) mapping-speed gain the proposal's
# sensitivity budget assumes.  Native resolution is far finer than
# needed; smooth to ~1 km/s in reduction.
# =====================================================================

receiver  = 'RcvrArray18_26'   # K-band Focal Plane Array (KFPA), 18.0-27.5 GHz.
                              # 26.05 GHz is ~1.4 GHz inside the band edge.
beam      = '1,2,3,4,5,6,7'    # all 7 KFPA beams (proposal: 7 spectrometers)
obstype   = 'Spectroscopy'
backend   = 'VEGAS'

# Single VEGAS window on the primary line, replicated to all 7 beams.
restfreq  = 26051.898       # NaCl v=0 J=2-1  (LSR rest, MHz)  <-- PRIMARY
dopplertrackfreq = 26051.898

bandwidth = 187.5           # MHz  (VEGAS Mode 4)
nchan     = 32768           # -> 5.72 kHz = 0.065 km/s at 26 GHz

# In-band frequency switching (proposal: "In-Band Frequency Switching").
swmode    = "sp"            # switched power WITH cal
swper     = 0.4
swfreq    = 0.0, 28.610    # throw (MHz) = 5000 x 5.722 kHz channels.
                          # 28.6 MHz > the ~17.4 MHz (+/-100 km/s) line
                          # complex, so the shifted reference clears the
                          # absorption; well inside the +/-93.75 MHz
                          # half-window.  (Wide 187.5 MHz window is what
                          # makes a clean in-band throw possible here.)
tint      = 1.6           # dump time; 4 phases x 0.4 s.  At 4'/min scan
                          # rate -> 6.4"/sample < FWHM/4 (FWHM ~ 29").

vlow      = 0
vhigh     = 0
vframe    = "lsrk"
vdef      = "Radio"
noisecal  = "lo"
pol       = "Circular"

# ---------------------------------------------------------------------
# K-band line reference (MHz, LSR rest):
#   NaCl v=0 2-1  26051.898   <-- PRIMARY target (absorption)
#   [window spans ~25958-26146 MHz]
# Beam FWHM ~ 29" at 26 GHz.  Excited-vib NaCl 2-1 (v>=1, 25.3-25.9 GHz)
# is NOT in this window and is descoped.
#
# KFPA CALIBRATION: the KFPA noise-diode strengths vary between sessions,
# so each session must include a KFPA calibration observation (see the
# KFPA Observer's Guide / pointing_K.py note) for reliable Ta* scaling.
# ---------------------------------------------------------------------
