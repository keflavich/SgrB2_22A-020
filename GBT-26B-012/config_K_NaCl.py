# =====================================================================
# GBT-26B-012  --  Salt in Sgr B2(N)
# K-band (26 GHz) VEGAS + KFPA configuration: NaCl v=0 J=2-1 (ABSORPTION)
# =====================================================================
# Matches the submitted proposal resource table (GBT-26B-012.pdf, p.2):
#   VEGAS Mode 4, 187.5 MHz bandwidth, 32768 channels -> 5.722 kHz
#   (0.065 km/s at 26 GHz), a SINGLE spectral window on NaCl v=0 2-1,
#   ALL 7 KFPA beams, in-band frequency switching.
#
# 187.5 MHz gives ~2160 km/s of coverage leaving room for a frequency-switch
# throw (see swfreq below).  The 7-beam KFPA gives the sqrt(7) mapping-speed
# gain.  Native resolution is far finer than needed; smooth to ~1 km/s in
# reduction.
#
# !! ASTRID RULE !!  Configure() evaluates each "keyword = value" line in its
# OWN namespace, so a value may NOT refer to another keyword.  Writing
#     swfreq = 0.0, bandwidth*2**-4
# fails with "NameError: name 'bandwidth' is not defined".  All values below
# are self-contained literals.
# =====================================================================

receiver  = 'RcvrArray18_26'   # K-band Focal Plane Array (KFPA), 18.0-27.5 GHz.
                              # 26.05 GHz is ~1.4 GHz inside the band edge.
beam      = '1,2,3,4,5,6,7'    # all 7 KFPA beams (proposal: 7 spectrometers)
obstype   = 'Spectroscopy'
backend   = 'VEGAS'

# Single VEGAS window on the primary line, replicated to all 7 beams.
# (With 7 beams VEGAS allows exactly ONE bank per beam, so one window is the
#  maximum here anyway.)
restfreq  = 26051.898       # NaCl v=0 J=2-1  (LSR rest, MHz)  <-- PRIMARY
dopplertrackfreq = 26051.898   # CHECK: restfreq

bandwidth = 187.5           # MHz  (VEGAS Mode 4)
nchan     = 32768           # -> 5.722 kHz = 0.065 km/s at 26 GHz

# In-band frequency switching (proposal: "In-Band Frequency Switching").
swmode    = 'sp'            # switched power WITH cal
swtype    = 'fsw'           # REQUIRED to actually frequency switch when
                            # swmode='sp'; without it nothing is switched.
swper     = 0.8             # full switching cycle (s).  4 phases -> 200 ms
                            # each; VEGAS blanks ~11 ms (the Mode 4 minimum
                            # integration) at every phase transition, so this
                            # loses ~5.5%.  swper=0.4 gave 100 ms phases and
                            # tripped ASTRID's ">10% of your data will be
                            # blanked in BankX using mode MODE4" warning.
swfreq    = 0.0, 11.71875   # CHECK: (0.0, bandwidth*2**-4)
                            # CHECK: (0.0, 2048*chanwidth)
                            # throw = 187.5/16 MHz = exactly 2048 channels
                            # of 5.722 kHz.  = 135 km/s at 26.05 GHz.
                            # Well inside the +/-93.75 MHz half-window.
                            # NOTE: 135 km/s does NOT fully clear a
                            # +/-100 km/s absorption complex -- the reference
                            # phase self-subtracts over ~35-100 km/s.  Use
                            # swfreq = 0.0, 23.4375 (4096 chan, 270 km/s) if
                            # a fully clean reference is required.
tint      = 1.6             # CHECK: 2*swper
                            # dump time.  At 3.71"/s scan rate
                            # -> 5.9"/sample < FWHM/4 (FWHM ~ 28.5").
                            # VEGAS Mode 4 minimum is 11 ms.

vlow      = 0
vhigh     = 0
vframe    = 'lsrk'
vdef      = 'Radio'
noisecal  = 'lo'
pol       = 'Circular'      # KFPA feeds have cooled polarizers producing
                            # CIRCULAR polarization -- 'Linear' is wrong here.

# ---------------------------------------------------------------------
# K-band line reference (MHz, LSR rest):
#   NaCl v=0 2-1  26051.898   <-- PRIMARY target (absorption)
#   [window spans ~25958-26146 MHz]
# Beam FWHM ~ 29" at 26 GHz.  Excited-vib NaCl 2-1 (v>=1, 25.3-25.9 GHz)
# is NOT in this window.
#
# KFPA CALIBRATION: the KFPA noise-diode strengths vary between sessions,
# so each session must include a KFPA calibration observation (see the
# KFPA Observer's Guide / pointing_K.py note) for reliable Ta* scaling.
#
# Data rate: 32768 ch x 2 pol x 4 phases x 4 B = 1.05 MB/dump/bank;
# 7 banks / 1.6 s = 4.6 MB/s = ~17 GB/hr.
#
# Run validate_scripts.py after editing anything here: the CHECK: annotations
# above are machine-checked against the literals, since ASTRID itself cannot
# evaluate cross-keyword arithmetic.
# ---------------------------------------------------------------------
