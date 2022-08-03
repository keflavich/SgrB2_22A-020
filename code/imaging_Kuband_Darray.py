# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854545_1_1.59783.16907671296/pipeline-20220725T214145/html/t2-1.html?sidebar=sidebar_22A_020_sb41854545_1_1_59783_16907671296_ms&subpage=listobs.txt
import os
vis = ['../22A-020_sb41854545_1_1.59783.16907671296/22A-020_sb41854545_1_1.59783.16907671296.ms']


contspw = [0,2,3,4,6,9,30,31,32]

for spw in (range(32,0,-1)):
    if not os.path.exists(f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean',
               #phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['1arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)
