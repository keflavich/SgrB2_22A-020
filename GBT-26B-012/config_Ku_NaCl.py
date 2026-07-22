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
restfreq  = 13026.061       # NaCl v=0 J=1-0  (LSR rest, MHz)  <-- PRIMARY
dopplertrackfreq = 13026.061

bandwidth = 187.5           # MHz  (VEGAS Mode 4)
nchan     = 32768           # -> 5.72 kHz = 0.13 km/s at 13 GHz

# In-band frequency switching (proposal: "In-Band Frequency Switching").
swmode    = "sp"            # switched power WITH cal
swper     = 0.4            # switching period (s)
swfreq    = 0.0, 14.305    # throw (MHz) = 2500 x 5.722 kHz channels.
                          # 14.3 MHz > the ~8.7 MHz (+/-100 km/s) line
                          # complex, so signal/reference do not overlap;
                          # well inside the +/-93.75 MHz half-window.
                          # (Integer #channels avoids the fsw artifact.)
tint      = 1.6           # dump time; 4 phases x 0.4 s.  At 8'/min scan
                          # rate -> 12.8"/sample < FWHM/4 (FWHM ~ 57").

vlow      = 0
vhigh     = 0
vframe    = "lsrk"         # LSR kinematic (standard for Galactic work)
vdef      = "Radio"
noisecal  = "lo"
pol       = "Circular"

# ---------------------------------------------------------------------
# Ku-band line reference (MHz, LSR rest):
#   NaCl v=0 1-0  13026.061   <-- PRIMARY target (emission)
#   [window spans ~12932-13120 MHz; also contains H79alpha 13088.85]
# Beam FWHM ~ 57" at 13 GHz.  Excited-vib NaCl (v>=1, 12.6-12.9 GHz) is
# NOT in this window and is descoped (severe RFI region regardless).
# ---------------------------------------------------------------------
