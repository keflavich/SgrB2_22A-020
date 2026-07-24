# =====================================================================
# GBT-26B-012  --  Salt in Sgr B2(N)
# Ku-band (13 GHz) VEGAS configuration:  NaCl v=0 J=1-0  (EMISSION)
# =====================================================================
# Matches the submitted proposal resource table (GBT-26B-012.pdf, p.2):
#   VEGAS Mode 4, 187.5 MHz bandwidth, ~32768 channels -> 5.7 kHz
#   (0.13 km/s at 13 GHz), a SINGLE spectral window on NaCl v=0 1-0,
#   both Ku beams, in-band frequency switching.
#
# 187.5 MHz gives ~4300 km/s of coverage -- far more than the ~200 km/s
# Sgr B2 line-of-sight needs -- so one window covers the science line
# with room to spare.  We do NOT put separate windows on the excited
# vibrational states (they fall outside this window and were descoped in
# the submitted setup; they also sit in Ku DBS RFI).  Native resolution
# is far finer than needed; smooth to ~1 km/s in reduction.
# =====================================================================

receiver  = 'Rcvr12_18'      # Ku-band receiver (12-18 GHz), dual-beam
beam      = 'B12'           # BOTH beams (proposal: 2 beams / 2 spectrometers)
obstype   = 'Spectroscopy'
backend   = 'VEGAS'


# Single VEGAS window on the primary line, replicated to both beams.
# restfreq  = 13026.061       # NaCl v=0 J=1-0  (LSR rest, MHz)  <-- PRIMARY
# bandwidth = 187.5           # MHz  (VEGAS Mode 4)

# 4-tuning window covering other vibrationally excited lines (but we know they're not detected...)
# H78a is at 13088
# below 12706 RFI gets super ratty (in PRIMOS)
# these middle two are pretty empty - we could pick something else - maybe H2CO or H213CO or something
restfreq  = 13026.061, 12929.260, 12833.076, 13088.0
bandwidth = 187.5, 187.5, 187.5, 187.5           # MHz  (VEGAS Mode 4)

dopplertrackfreq = 13026.061
nchan     = 32768           # -> 5.72 kHz = 0.13 km/s at 13 GHz

# In-band frequency switching
swmode    = "sp"            # switched power WITH cal
swper     = 0.4            # switching period (s)

# 11.7 MHz (recommended in docs: https://gbtdocs.readthedocs.io/en/latest/references/observing/configure.html#swfreq-float-float)
# 270 km/s
# known bright line at 13043 = 17 MHz.  _just_ misses the line
swfreq    = 0.0, bandwidth*2**-4

tint      = 0.4           # dump time; 4 phases x 0.4 s.  At 8'/min = 8"/s scan
                          # rate -> 3.2"/sample < FWHM/4 (FWHM ~ 57").
                          # minimum allowed is 11ms
                          # "However, the integration time (tint), switching period (swper), and the frequency switching offset (swfreq) values must each be the same for all banks. "

vlow      = 0
vhigh     = 0
vframe    = "lsrk"         # LSR kinematic (standard for Galactic work)
vdef      = "Radio"
noisecal  = "lo"
pol       = "Linear"

# ---------------------------------------------------------------------
# Ku-band line reference (MHz, LSR rest):
#   NaCl v=0 1-0  13026.061   <-- PRIMARY target (emission)
#   [window spans ~12932-13120 MHz; also contains H79alpha 13088.85]
# Beam FWHM ~ 57" at 13 GHz.  Excited-vib NaCl (v>=1, 12.6-12.9 GHz) is
# NOT in this window and is descoped (severe RFI region regardless).
# ---------------------------------------------------------------------
