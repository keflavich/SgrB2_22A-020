import numpy as np
import glob
from astropy import units as u
import os
from spectral_cube import SpectralCube
import warnings
from spectral_cube.utils import SpectralCubeWarning


with np.errstate(all='ignore'):
    with warnings.catch_warnings():

        warnings.filterwarnings(action='ignore', category=SpectralCubeWarning,
                                append=True)

        for fn in glob.glob("*.image"):
            try:
                cube = SpectralCube.read(fn, use_dask=True)
                frq = cube.spectral_axis.to(u.GHz).mean()
                if not os.path.exists(f'{fn}.contsub.fits'):
                    print(fn, frq)
                    cube = cube[int(cube.shape[0]*0.05):int(cube.shape[0]*0.95),:,:]
                    med = cube.median(axis=0)
                    msub = cube-med
                    msub.write(f'{fn}.contsub.fits')
                frqtxt = f'{frq.value:0.2f}'
                if not os.path.exists(f'{fn}.contsub.{frqtxt}.fits'):
                    os.link(f'{fn}.contsub.fits',
                            f'{fn}.contsub.{frqtxt}.fits')
            except Exception as ex:
                print(f"Failure for {fn} {frq}")
                print(ex)
