# =====================================================================
# GBT-26B-012  --  Salt in Sgr B2(N)
# Ku-band (13 GHz) VEGAS configuration:  NaCl J=1-0 ladder (EMISSION)
# =====================================================================
# Science goal: map the extended NaCl v=0 J=1-0 emission (13.026 GHz)
# that PRIMOS detected but the VLA resolved out.  We use VEGAS with
# multiple 187.5-MHz sub-bands, one per vibrational state, at ~0.13 km/s
# native resolution (smooth to ~0.5-1 km/s in reduction).  187.5 MHz is
# the widest VEGAS mode giving < 1 km/s resolution and gives ~4300 km/s
# of coverage per window -- far more than the ~200 km/s Sgr B2 needs.
#
# Switching: in-band frequency switching (swmode='sp', with cal), which
# is what the extended-emission science requires (no clean OFF within
# the field).  4 phases per integration: tint = 4 * swper (1.6 = 4*0.4).
#
# Frequencies (MHz, LSR rest): NaCl 1-0 ladder.  v=0..4 span 12642-13026
# MHz, so each needs its own 187.5-MHz window (5 sub-bands, <= 8 allowed).
#   NaCl v=0  window also contains H79alpha (13088.85) at its high edge.
#   NaCl v=4  window (center 12642.56) also contains Na37Cl v=1 (12653.7).
# Rest freqs from the proposal line list; consistent to ~1 km/s with the
# VLA project catalog (instrument_configurations/KuLineCatalog.txt).
# =====================================================================

receiver  = 'Rcvr12_18'      # Ku-band receiver (12-18 GHz)
beam      = '1'              # single-beam Ku receiver, beam 1
obstype   = 'Spectroscopy'
backend   = 'VEGAS'

# One VEGAS sub-band (spectral window) per NaCl v-state, all in one bank.
# All sub-bands share bandwidth / nchan (VEGAS requirement).
restfreq  = 13026.061, 12929.260, 12833.076, 12737.509, 12642.560
#           v=0(+H79a)  v=1        v=2        v=3        v=4(+Na37Cl v=1)
deltafreq = 0, 0, 0, 0, 0

bandwidth = 187.5            # MHz per sub-band  (VEGAS 187.5-MHz mode)
nchan     = 32768           # -> 5.72 kHz = 0.13 km/s at 13 GHz
                            # (VERIFY the exact VEGAS mode # in AstrID's
                            #  config tool -- 187.5 MHz / 32768 ch.)

swmode    = "sp"            # switched power WITH cal  (frequency switching)
swtype    = "fsw"          # frequency switching
swper     = 0.4            # switching period (s)
swfreq    = 0.0, -12.5     # in-band freq-switch throw (MHz); signal appears
                          # in both phases -> fold in reduction
tint      = 1.6           # integration (dump) time; 4 phases * 0.4 s.
                          # At 8'/min scan rate -> 12.8"/sample < FWHM/4.

vlow      = 0
vhigh     = 0
vframe    = "lsrk"         # LSR kinematic (standard for Galactic work)
vdef      = "Radio"
noisecal  = "lo"
pol       = "Circular"
spect.levels = 9

# ---------------------------------------------------------------------
# Ku-band line reference (MHz, LSR rest):
#   NaCl v=0 1-0  13026.061   <-- PRIMARY target (emission)
#   NaCl v=1 1-0  12929.260
#   NaCl v=2 1-0  12833.076
#   NaCl v=3 1-0  12737.509
#   NaCl v=4 1-0  12642.560
#   Na37Cl v=1    12653.734   (folds into the v=4 window)
#   H79alpha      13088.850   (folds into the v=0 window)
# Beam FWHM ~ 57" at 13 GHz.  See config_ProposalNumbers in README.
# NOTE: vibrationally-excited NaCl lines sit in a region of severe RFI
# (see proposal/technical.txt); treat them as bonus, not required.
# ---------------------------------------------------------------------
