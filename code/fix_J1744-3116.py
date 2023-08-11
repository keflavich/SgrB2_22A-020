"""
Run from the top-level directory (one above code/, such that */*.ms hits something)
"""
from astropy import units as u, coordinates
import numpy as np
import glob, shutil

simbad_coord = coordinates.SkyCoord('17 44 23.57824 -31 16 36.2943', unit=(u.h, u.deg), frame='icrs')

for vis in glob.glob("*/*.ms"):
    shutil.copytree(vis+"/FIELD", vis+"/FIELD.backup")
    tb.open(vis+"/FIELD")
    phasedir = tb.getcol('PHASE_DIR')
    rownr = np.argmax(tb.getcol('NAME') == 'J1744-3116')
    assert rownr != 0
    phasedir[:, 0, rownr] = simbad_coord.fk5.ra.wrap_at(180*u.deg).rad, simbad_coord.fk5.dec.rad
    tb.open(vis+"/FIELD", nomodify=False)
    tb.putcol(columnname='PHASE_DIR', value=phasedir)
    tb.flush()
    tb.close()
