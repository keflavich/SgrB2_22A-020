import os
vis = ['../22A-020.sb41257746.eb41788351.59700.31502699074/22A-020.sb41257746.eb41788351.59700.31502699074.ms',
       '../22A-020.sb41257746.eb41789929.59703.295863067135/22A-020.sb41257746.eb41789929.59703.295863067135.ms']




for spw in (range(42,0,-1)):
    if not os.path.exists(f'allEBs.sgrb2n.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'allEBs.sgrb2n.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=True)
    if not os.path.exists(f'allEBs.sgrb2m.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'allEBs.sgrb2m.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m20.16 -28d23m04.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=True)


for spw in (16, 30, 39):
    if not os.path.exists(f'allEBs.center.spw{spw}.big-coarse.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'allEBs.center.spw{spw}.big-coarse.liteclean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=True)

for spw in (30,31):
    if not os.path.exists(f'allEBs.center.robust2.spw{spw}.big-coarse.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'allEBs.center.robust2.spw{spw}.big-coarse.liteclean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=True)


for spw in (16, 30, 39):
    if not os.path.exists(f'allEBs.center.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=vis,
               imagename=f'allEBs.center.spw{spw}.big-coarse.clean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=True)

for spw in (30,31):
    if not os.path.exists(f'allEBs.center.robust2.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=vis,
               imagename=f'allEBs.center.robust2.spw{spw}.big-coarse.clean',
               niter=1000000, threshold='10mJy', spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=True)

for vv in vis:
    if not os.path.exists(vv.replace(".ms", "_spw30_NaCl.split")):
        split(vis=vv, outputvis=vv.replace(".ms", "_spw30_NaCl.split"),
              width=8, field='sgr b2b', spw='30')
for spw in (30,):
    if not os.path.exists(f'allEBs.center.robust2.downsample.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=[vv.replace(".ms", "_spw30_NaCl.split") for vv in vis],
               imagename=f'allEBs.center.robust2.downsample.spw{spw}.big-coarse.clean',
               niter=2000000, threshold='10mJy', field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=True)








