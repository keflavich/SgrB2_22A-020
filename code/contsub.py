import glob
from astropy import units as u
import os
from spectral_cube import SpectralCube

for fn in glob.glob("*.image"):
    cube = SpectralCube.read(fn, use_dask=True)
    frq = cube.spectral_axis.to(u.GHz).mean()
    if not os.path.exists(f'{fn}.contsub.fits'):
        cube = cube[int(cube.shape[0]*0.05):int(cube.shape[0]*0.95),:,:]
        med = cube.median(axis=0)
        msub = cube-med
        msub.write(f'{fn}.contsub.fits')
    frqtxt = f'{frq.value:0.2f}'
    if not os.path.exists(f'{fn}.contsub.{frqtxt}.fits'):
        os.link(f'{fn}.contsub.fits',
                f'{fn}.contsub.{frqtxt}.fits')
        
