# sbatch --job-name=casa_22A-020_KuA_line --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KuA_line_%j.log --wrap "xvfb-run -a /orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kuband_Aarray_lines.py"

# imaging Ku-band A-array (both EBs combined)
import os
import shutil
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Aarray')

def logprint(string, origin='imaging_Kuband_Aarray.py', priority='INFO', flush=True):
    print(string, flush=flush)
    casalog.post(string, origin=origin, priority=priority)

logprint(f"CASA log file: {casalog.logfile()}")
vis = ['../22A-020.sb41257746.eb41788351.59700.31502699074/22A-020.sb41257746.eb41788351.59700.31502699074.ms',
       '../22A-020.sb41257746.eb41789929.59703.295863067135/22A-020.sb41257746.eb41789929.59703.295863067135.ms']

contspw = [8, 9, 10, 11, 12, 13, 14, 15, 31, 32, 33, 34, 35, 36, 37, 38]


for vv in vis:
    if not os.path.exists(vv.replace(".ms", "_spw30_NaCl.split")):
        split(vis=vv, outputvis=vv.replace(".ms", "_spw30_NaCl.split"),
              width=8, field='sgr b2b', spw='30')
for spw in (30,):
    if not os.path.exists(f'Kuband_Aarray.center.robust2.downsample.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=[vv.replace(".ms", "_spw30_NaCl.split") for vv in vis],
               imagename=f'Kuband_Aarray.center.robust2.downsample.spw{spw}.big-coarse.clean',
               niter=2000000, threshold='10mJy', field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=False)

for spw in (16, 30, 39):
    if not os.path.exists(f'Kuband_Aarray.center.spw{spw}.big-coarse.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'Kuband_Aarray.center.spw{spw}.big-coarse.liteclean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)

for spw in (30,31):
    if not os.path.exists(f'Kuband_Aarray.center.robust2.spw{spw}.big-coarse.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'Kuband_Aarray.center.robust2.spw{spw}.big-coarse.liteclean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=False)

for spw in (16, 30, 39):
    if not os.path.exists(f'Kuband_Aarray.center.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=vis,
               imagename=f'Kuband_Aarray.center.spw{spw}.big-coarse.clean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)

for spw in (30,31):
    if not os.path.exists(f'Kuband_Aarray.center.robust2.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=vis,
               imagename=f'Kuband_Aarray.center.robust2.spw{spw}.big-coarse.clean',
               niter=1000000, threshold='10mJy', spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=False)


logprint("Step 3: Non-selfcal imaging of NaCl line spws BEFORE deep cleaning/selfcal")
# UV continuum subtraction for spw 30 (NaCl line)
uvcontsub_vis_spw30_noselfcal = []
for vs in vis_split:
    uv = vs.replace('.ms', '.spw30.contsub')
    uvcontsub_vis_spw30_noselfcal.append(uv)
    if not os.path.exists(uv):
        uvcontsub(vis=vs,
                  outputvis=uv,
                  spw='30',
                  fitspec='30:50~460', # 512 channels
                  fitorder=0)

# Clean spw 30 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kuband_Aarray.center.spw30.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw30_noselfcal,               datacolumn='data',               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='30',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[2000],
               cell=['0.1arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 30 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    contmodel = f'Kuband_Aarray.center.robust{robust}.continuum.big-coarse.liteclean.model.tt0',
    imagename = f'Kuband_Aarray.center.spw30.robust{robust}.withcont.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=vis_split,
               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='30',
               field='sgr b2b',
               imsize=[2000],
               cell=['0.1arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)
# Cleanup: Remove .pb, .mask, .psf files for spw 30 cube images to save space
logprint("Cleaning up spw 30 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Aarray.center.spw30.robust{robust}.contsub.noselfcal.clean',
                       f'Kuband_Aarray.center.spw30.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)
# Cleanup: Remove .pb, .mask, .psf files for spw 30 cube images to save space
logprint("Cleaning up spw 30 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Aarray.center.spw30.robust{robust}.contsub.noselfcal.clean',
                       f'Kuband_Aarray.center.spw30.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)


if False:
    for spw in (range(42,0,-1)):
        if not os.path.exists(f'Kuband_Aarray.sgrb2n.spw{spw}.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'Kuband_Aarray.sgrb2n.spw{spw}.liteclean',
                   phasecenter='ICRS 17h47m19.87 -28d22m18.5',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
                   cell=['0.02arcsec'], specmode='cube', weighting='briggs',
                   robust=0.5, parallel=False)
        if not os.path.exists(f'Kuband_Aarray.sgrb2m.spw{spw}.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'Kuband_Aarray.sgrb2m.spw{spw}.liteclean',
                   phasecenter='ICRS 17h47m20.16 -28d23m04.5',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
                   cell=['0.02arcsec'], specmode='cube', weighting='briggs',
                   robust=0.5, parallel=False)

logprint("Step 7: Selfcal imaging of NaCl line spws AFTER selfcal")
# UV continuum subtraction for spw 30 (selfcal data)
uvcontsub_vis_spw30_selfcal = []
for vsc in vis_selfcal:
    uv = vsc.replace('.ms', '.spw30.contsub')
    uvcontsub_vis_spw30_selfcal.append(uv)
    if os.path.exists(uv):
        shutil.rmtree(uv)
    
    uvcontsub(vis=vsc,
              outputvis=uv,
              spw='30',
              fitspec='30:100~800',
              fitorder=0)

# Clean spw 30 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'Kuband_Aarray.center.spw30.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw30_selfcal,               datacolumn='data',               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='30',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[2000],
               cell=['0.1arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 30 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'Kuband_Aarray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'Kuband_Aarray.center.spw30.robust{robust}.withcont.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=vis_selfcal,
               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='30',
               field='sgr b2b',
               imsize=[2000],
               cell=['0.1arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 30 selfcal cube images to save space
loglogprint("Cleaning up spw 30 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Aarray.center.spw30.robust{robust}.contsub.selfcal.clean',
                       f'Kuband_Aarray.center.spw30.robust{robust}.withcont.selfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

logprint("Imaging complete!")
logprint("Cleaning up spw 30 selfcal cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Aarray.center.spw30.robust{robust}.contsub.selfcal.clean',
                       f'Kuband_Aarray.center.spw30.robust{robust}.withcont.selfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

logprint("Imaging complete!")
               deconvolver='mtmfs',
               nterms=2,
               robust=robust,
               parallel=False,
               mask='clean_mask.crtf',
               savemodel='modelcolumn')

