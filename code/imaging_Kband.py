import os
# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41852157_1_1.59747.288797835645/pipeline-20220627T225838/html/t2-1.html?sidebar=sidebar_22A_020_sb41852157_1_1_59747_288797835645_ms&subpage=t2-2-2.html

# NaCl v=0 2-1; 26.0518979GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# NaCl v=1 2-1; 25.8582961GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true

vis = ['../22A-020_sb41852157_1_1.59747.288797835645/22A-020_sb41852157_1_1.59747.288797835645.ms']

contspw = [18,19,20,21,22,23,24,25,30,31,32,33,34,46,47,48]

for spw in (45,):
    for robust in (0, 2):
        if not os.path.exists(f'KbandAarray.center.robust{robust}.spw{spw}.big-coarse.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'KbandAarray.center.robust{robust}.spw{spw}.big-coarse.liteclean',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
                   cell=['0.05arcsec'], specmode='cube', weighting='briggs',
                   robust=2, parallel=False)

for spw in (range(48,2,-1)):
    if spw in contspw:
        continue
    if not os.path.exists(f'KbandAarray.sgrb2n.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KbandAarray.sgrb2n.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)
    if not os.path.exists(f'Kband.sgrb2m.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KbandAarray.sgrb2m.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m20.16 -28d23m04.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)



if not os.path.exists(f'KbandAarray.center.robust{robust}.continuum.big-coarse.liteclean.psf'):
    tclean(vis=vis,
           imagename=f'KbandAarray.center.robust{robust}.continuum.big-coarse.liteclean',
           niter=1000, spw=",".join(map(str,contspw)), field='sgr b2b', imsize=[2000],
           cell=['0.05arcsec'], specmode='mfs', weighting='briggs',
           robust=2, parallel=False)

