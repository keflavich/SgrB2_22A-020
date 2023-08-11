
import os
# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854998_1_1.59785.110016307866/pipeline-20220726T015648/html/t2-1.html?sidebar=sidebar_22A_020_sb41854998_1_1_59785_110016307866_ms&subpage=listobs.txt

# NaCl v=0 2-1; 26.0518979GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# NaCl v=1 2-1; 25.8582961GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# spw13: v=0 2-1
# spw14: v=1 2-1
# spw36: water

vis = ['../22A-020_sb41854998_1_1.59785.110016307866/22A-020_sb41854998_1_1.59785.110016307866.ms']

contspw = [4,5,6,7,8,9,10,11, 27,28,29,30,31,32,33,34]
# 4-11, 27-34

for robust in (0,2):
    if not os.path.exists(f'KbandDarray.center.robust{robust}.continuum.big-coarse.liteclean.psf.tt0'):
        tclean(vis=vis,
               imagename=f'KbandDarray.center.robust{robust}.continuum.big-coarse.liteclean',
               niter=1000, spw=",".join(map(str,contspw)), field='sgr b2b', imsize=[700],
               cell=['0.25arcsec'], specmode='mfs', weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust, parallel=False)

for spw in (13,): # NaCl v=0
    for robust in (0, 2):
        if not os.path.exists(f'KbandDarray.center.robust{robust}.spw{spw}.big-coarse.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'KbandDarray.center.robust{robust}.spw{spw}.big-coarse.liteclean',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[500],
                   cell=['0.5arcsec'], specmode='cube', weighting='briggs',
                   robust=robust, parallel=False)

for spw in (range(39,2,-1)):
    if spw in contspw:
        continue
    if not os.path.exists(f'KbandDarray.sgrb2.spw{spw}.robust0.5.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KbandDarray.sgrb2.spw{spw}.robust0.5.liteclean',
               #phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[500],
               cell=['0.5arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)



