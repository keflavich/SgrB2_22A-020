########################################################
# Started Logging At: 2022-05-09 19:22:55
########################################################

########################################################
# # Started Logging At: 2022-05-09 19:22:55
########################################################
from spectral_cube import SpectralCube
get_ipython().run_line_magic('ls', '-d *image')
for fn in glob.glob("*.image"):
    cube = SpectralCube.read(fn, use_dask=True)
    cube = cube[int(cube.size[0]*0.05):int(cube.size[0]*0.95),:,:]
    med = cube.median(axis=0)
    msub = cube-med
    msub.write(f'{fn}.contsub.fits')
    
import glob
for fn in glob.glob("*.image"):
    cube = SpectralCube.read(fn, use_dask=True)
    cube = cube[int(cube.size[0]*0.05):int(cube.size[0]*0.95),:,:]
    med = cube.median(axis=0)
    msub = cube-med
    msub.write(f'{fn}.contsub.fits')
    
for fn in glob.glob("*.image"):
    cube = SpectralCube.read(fn, use_dask=True)
    cube = cube[int(cube.shape[0]*0.05):int(cube.shape[0]*0.95),:,:]
    med = cube.median(axis=0)
    msub = cube-med
    msub.write(f'{fn}.contsub.fits')
    
