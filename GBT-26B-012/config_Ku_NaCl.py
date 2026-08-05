# =====================================================================
# GBT-26B-012  --  Salt in Sgr B2(N)
# Ku-band (13 GHz) VEGAS configuration:  NaCl v=0 J=1-0  (EMISSION)
# =====================================================================
# VEGAS Mode 4, 187.5 MHz bandwidth, 32768 channels -> 5.722 kHz
# (0.13 km/s at 13 GHz), FOUR spectral windows, both Ku beams,
# in-band frequency switching.
#
# !! ASTRID RULE !!  Configure() evaluates each "keyword = value" line in its
# OWN namespace, so a value may NOT refer to another keyword.  Both
#     swfreq = 0.0, bandwidth*2**-4
#     swfreq = 0.0, bandwidth[0]*2**-4
# fail with "NameError: name 'bandwidth' is not defined".  Use literals.
#
# !! ASTRID RULE !!  'bandwidth' is a SINGLE float and applies to every
# window; it may not be a comma-separated list even when restfreq is.
# (Per-window bandwidths require the advanced dictionary restfreq syntax.)
# =====================================================================

receiver  = 'Rcvr12_18'     # Ku-band receiver (12-18 GHz), dual-beam
beam      = '1,2'           # BOTH beams.  'beam' takes comma-separated
                            # integers -- 'B12' is not a legal value.
obstype   = 'Spectroscopy'
backend   = 'VEGAS'

# 4-tuning window setup, replicated to both beams.
# 13026.061 = NaCl v=0 1-0 (PRIMARY); 13088 covers H78a; the middle two are
# vibrationally excited NaCl lines (we know they're not detected...).
# these middle two are pretty empty - we could pick something else - maybe
# H2CO or H213CO or something.
# below 12706 RFI gets super ratty (in PRIMOS)
#
# NOTE: 4 windows x 2 beams = 8 VEGAS banks.  A dual-beam receiver is limited
# to 4 banks per beam, so this is exactly at the limit -- no room for a 5th
# window without dropping to a single beam.
restfreq  = 13026.061, 12929.260, 12833.076, 13088.0
bandwidth = 187.5           # MHz (VEGAS Mode 4), single value for all windows
dopplertrackfreq = 13026.061
nchan     = 32768           # -> 5.722 kHz = 0.13 km/s at 13 GHz

# In-band frequency switching
swmode    = 'sp'            # switched power WITH cal
swtype    = 'fsw'           # REQUIRED to actually frequency switch when
                            # swmode='sp'; without it nothing is switched.
swper     = 0.4             # full switching cycle (s); 4 phases -> 0.1 s each
swfreq    = 0.0, 11.71875   # throw = 187.5/16 MHz = exactly 2048 channels of
                            # 5.722 kHz = 270 km/s at 13.026 GHz.
                            # Known bright line at 13043 (+17 MHz) is _just_
                            # missed.  Recommended value in the configure docs:
                            # https://gbtdocs.readthedocs.io/en/latest/references/observing/configure.html#swfreq-float-float
tint      = 0.4             # dump time = 1 x swper.  At 6'/48.5 s = 7.42"/s
                            # -> 3.0"/sample, far finer than FWHM/4 (~14").
                            # VEGAS Mode 4 minimum is 11 ms.
                            # WARNING: this produces ~21 MB/s = ~75 GB/hr
                            # across 8 banks (~2.7 TB for the campaign).
                            # tint = 1.0 still gives 7.4"/sample and cuts
                            # that by 2.5x.
                            # "the integration time (tint), switching period
                            #  (swper), and the frequency switching offset
                            #  (swfreq) values must each be the same for all
                            #  banks."

vlow      = 0
vhigh     = 0
vframe    = 'lsrk'          # LSR kinematic (standard for Galactic work)
vdef      = 'Radio'
noisecal  = 'lo'
pol       = 'Circular'      # Rcvr12_18 has cooled polarizers producing
                            # CIRCULAR polarization -- 'Linear' is wrong here.

# ---------------------------------------------------------------------
# Ku-band line reference (MHz, LSR rest):
#   NaCl v=0 1-0  13026.061   <-- PRIMARY target (emission)
#   [primary window spans ~12932-13120 MHz; also contains H79alpha 13088.85]
# Beam FWHM ~ 57" at 13 GHz.
#
# NOTE: the two Ku feeds are separated by 330" (5.5') in cross-elevation, so
# with beamName='1' in the map scans, beam 2 sweeps a 6'x6' patch ~5.5' away
# from Sgr B2(N) -- it does not add sensitivity on target.
# ---------------------------------------------------------------------
