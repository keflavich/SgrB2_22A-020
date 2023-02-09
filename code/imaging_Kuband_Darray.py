# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854545_1_1.59783.16907671296/pipeline-20220725T214145/html/t2-1.html?sidebar=sidebar_22A_020_sb41854545_1_1_59783_16907671296_ms&subpage=listobs.txt
import os
vis = ['../22A-020_sb41854545_1_1.59783.16907671296/22A-020_sb41854545_1_1.59783.16907671296.ms']

# 2           1 7.2147e-07     0.434501 13.026012279345801 0.6251501990154984                0.0   v=0-0 J=1-0     0     0     1     0    48    16
# spw13: NaCl 1-0
# KClv=0                       15.378087          2-1
# spw29: KCl 1-0

contspw = [0,2,3,4,6,9,30,31,32]

for robust in (0,2):
    if not os.path.exists(f'KubandDarray.center.robust{robust}.continuum.big-coarse.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KubandDarray.center.robust{robust}.continuum.big-coarse.liteclean',
               niter=1000, spw=",".join(map(str,contspw)), field='sgr b2b', imsize=[600],
               cell=['0.5arcsec'], specmode='mfs', weighting='briggs',
               nterms=2,
               robust=robust, parallel=False)


for spw in (range(32,0,-1)):
    if not os.path.exists(f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean',
               #phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[600],
               cell=['0.5arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)
