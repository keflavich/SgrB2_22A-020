# =====================================================================
# GBT-26B-012  --  Salt in Sgr B2(N)
# K-band (26 GHz) VEGAS + KFPA configuration: NaCl J=2-1 ladder (ABSORPTION)
# =====================================================================
# Science goal: map the NaCl v=0 J=2-1 absorption (26.052 GHz) against the
# Sgr B2 continuum, and localize which continuum sources it absorbs against.
# We use the KFPA (7-beam) for mapping speed with VEGAS 23.44-MHz sub-bands,
# one per vibrational state.  23.44 MHz gives ~270 km/s coverage at 26 GHz
# -- matching the ~200 km/s the Sgr B2 line-of-sight requires -- at very
# fine native resolution (smooth to ~0.5-1 km/s in reduction).
#
# Switching: in-band frequency switching (swmode='sp', with cal).  The
# proposal's sensitivity budget assumes freq switching (with reference
# averaging) as the efficient route to the ~4-6 mK target in K-band.
#
# Frequencies (MHz, LSR rest): NaCl 2-1 ladder.  v=0..4 span 25285-26052
# MHz (< 1 GHz), so all fit in one KFPA/VEGAS IF.  5 sub-bands:
#   v=4 (25284.9) and Na37Cl v=1 (25307.3) are 22 MHz apart -> combined
#   into ONE 23.44-MHz window centered at 25296.1.
# =====================================================================

receiver  = 'RcvrArray18_26'   # K-band Focal Plane Array (KFPA), 18-26.5 GHz
                              # NaCl 2-1 at 26.05 GHz sits at the top edge
                              # of the KFPA band -- expect slightly reduced
                              # aperture efficiency; confirm with GBT staff.
beam      = '1,2,3,4,5,6,7'    # all 7 KFPA beams for OTF mapping
obstype   = 'Spectroscopy'
backend   = 'VEGAS'

# One VEGAS sub-band per NaCl v-state (v=4 shares a window with Na37Cl v=1).
restfreq  = 26051.898, 25858.296, 25665.929, 25474.796, 25296.100
#           v=0         v=1        v=2        v=3        v=4 + Na37Cl v=1
deltafreq = 0, 0, 0, 0, 0

bandwidth = 23.44             # MHz per sub-band  (VEGAS 23.44-MHz mode)
nchan     = 32768            # -> ~0.72 kHz native; ~270 km/s coverage.
                            # (VERIFY exact VEGAS mode # in the config tool.)

swmode    = "sp"            # switched power WITH cal (frequency switching)
swtype    = "fsw"
swper     = 0.4
swfreq    = 0.0, -2.0      # in-band freq-switch throw (MHz); small because
                          # the window is only 23.44 MHz wide.
tint      = 1.6           # dump time (4 phases * 0.4 s).  At 4'/min scan
                          # rate -> ~6.4"/sample < FWHM/4 (FWHM ~ 29").

vlow      = 0
vhigh     = 0
vframe    = "lsrk"
vdef      = "Radio"
noisecal  = "lo"
pol       = "Circular"
spect.levels = 9

# ---------------------------------------------------------------------
# K-band line reference (MHz, LSR rest):
#   NaCl v=0 2-1  26051.898   <-- PRIMARY target (absorption)
#   NaCl v=1 2-1  25858.296
#   NaCl v=2 2-1  25665.929
#   NaCl v=3 2-1  25474.796
#   Na37Cl v=1    25307.254   (shares the v=4 window)
#   NaCl v=4 2-1  25284.898
# Beam FWHM ~ 29" at 26 GHz.
# NOTE (KFPA): confirm the beam list and OTF row spacing against the
# current KFPA Observer's Guide -- the 7-beam footprint changes the
# effective sampling relative to the single-beam numbers used in map_K.
# ---------------------------------------------------------------------
