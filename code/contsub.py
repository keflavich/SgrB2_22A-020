import glob
from spectral_cube import SpectralCube

for fn in glob.glob("*.image"):
    if not os.path.exists(f'{fn}.contsub.fits'):
        cube = SpectralCube.read(fn, use_dask=True)
        cube = cube[int(cube.shape[0]*0.05):int(cube.shape[0]*0.95),:,:]
        med = cube.median(axis=0)
        msub = cube-med
        msub.write(f'{fn}.contsub.fits')
        
