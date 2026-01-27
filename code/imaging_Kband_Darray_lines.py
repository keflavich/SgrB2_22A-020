# sbatch --job-name=casa_22A-020_KD_lines --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KD_lines_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kband_Darray_lines.py"

import os
import shutil
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Darray')

def logprint(string, origin='imaging_Kband_Darray.py', priority='INFO', flush=True):
    print(string, flush=flush)
    casalog.post(string, origin=origin, priority=priority)

logprint(f"CASA log file: {casalog.logfile()}")
# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854998_1_1.59785.110016307866/pipeline-20220726T015648/html/t2-1.html?sidebar=sidebar_22A_020_sb41854998_1_1_59785_110016307866_ms&subpage=listobs.txt

# NaCl v=0 2-1; 26.0518979GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# NaCl v=1 2-1; 25.8582961GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# spw13: v=0 2-1
# spw14: v=1 2-1
# spw36: water

vis = ['../22A-020_sb41854998_1_1.59785.110016307866/22A-020_sb41854998_1_1.59785.110016307866.ms']
listobs(vis[0], listfile='Kband_Darray.listobs', overwrite=True)

contspw = [4,5,6,7,8,9,10,11, 27,28,29,30,31,32,33,34]
# 4-11, 27-34


for spw in (13,): # NaCl v=0
    for robust in (0, 2):
        if not os.path.exists(f'Kband_Darray.center.robust{robust}.spw{spw}.big-coarse.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'Kband_Darray.center.robust{robust}.spw{spw}.big-coarse.liteclean',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[500],
                   cell=['0.5arcsec'], specmode='cube', weighting='briggs',
                   robust=robust, parallel=False)

if False:
    for spw in (range(39,2,-1)):
        if spw in contspw:
            continue
        if not os.path.exists(f'Kband_Darray.sgrb2.spw{spw}.robust0.5.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'Kband_Darray.sgrb2.spw{spw}.robust0.5.liteclean',
                   #phasecenter='ICRS 17h47m19.87 -28d22m18.5',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[500],
                   cell=['0.5arcsec'], specmode='cube', weighting='briggs',
                   robust=0.5, parallel=False)

logprint("Step 3: Non-selfcal imaging of NaCl line spws BEFORE deep cleaning/selfcal")
# UV continuum subtraction for spw 13 (NaCl v=0 2-1)
uvcontsub_vis_spw13_noselfcal = vis_split.replace('.ms', '.spw13.contsub')
if not os.path.exists(uvcontsub_vis_spw13_noselfcal):
    uvcontsub(vis=vis_split,
              outputvis=uvcontsub_vis_spw13_noselfcal,
              spw='13',
              field='sgr b2b',
              fitspec='13:100~800',
              fitorder=0)

# Clean spw 13 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw13.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw13_noselfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 13 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    contmodel = f'Kband_Darray.center.robust{robust}.continuum.big-coarse.liteclean.model.tt0',
    imagename = f'Kband_Darray.center.spw13.robust{robust}.withcont.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 13 cube images to save space
logprint("Cleaning up spw 13 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kband_Darray.center.spw13.robust{robust}.contsub.noselfcal.clean',
                       f'Kband_Darray.center.spw13.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

logprint("Step 3b: NH3 7-7 25.715 GHz imaging (spw 18)")
# UV continuum subtraction for spw 18 (NH3 7-7, non-selfcal data only)
uvcontsub_vis_spw18_noselfcal = vis_split.replace('.ms', '.spw18.contsub')
if not os.path.exists(uvcontsub_vis_spw18_noselfcal):
    uvcontsub(vis=vis_split,
              outputvis=uvcontsub_vis_spw18_noselfcal,
              spw='18',
              fitspec='18:100~800',  # avoid line channels
              fitorder=0)

# Clean spw 18 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw18_noselfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='18',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 18 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.withcont.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='18',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 18 cube images to save space
logprint("Cleaning up spw 18 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.contsub.noselfcal.clean',
                       f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

logprint("Step 3c: KCl 23.067 GHz imaging (spw 26)")
# UV continuum subtraction for spw 26 (KCl, non-selfcal data only)
uvcontsub_vis_spw26_noselfcal = vis_split.replace('.ms', '.spw26.contsub')
if not os.path.exists(uvcontsub_vis_spw26_noselfcal):
    uvcontsub(vis=vis_split,
              outputvis=uvcontsub_vis_spw26_noselfcal,
              spw='26',
              fitspec='26:100~800',  # avoid line channels
              fitorder=0)

# Clean spw 26 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw26.KCl.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw26_noselfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='26',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 26 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw26.KCl.robust{robust}.withcont.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='26',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 26 cube images to save space
logprint("Cleaning up spw 26 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kband_Darray.center.spw26.KCl.robust{robust}.contsub.noselfcal.clean',
                       f'Kband_Darray.center.spw26.KCl.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)


logprint("Step 7: Selfcal imaging of NaCl line spws AFTER selfcal")
# UV continuum subtraction for spw 13 (selfcal data)
uvcontsub_vis_spw13_selfcal = vis_selfcal.replace('.ms', '.spw13.contsub')
if os.path.exists(uvcontsub_vis_spw13_selfcal):
    shutil.rmtree(uvcontsub_vis_spw13_selfcal)

uvcontsub(vis=vis_selfcal,
          outputvis=uvcontsub_vis_spw13_selfcal,
          spw='13',
          fitspec='13:100~800',
              fitorder=0)

# Clean spw 13 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw13.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw13_selfcal,
               datacolumn='data', # uvcontsub does not populate corrected
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 13 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'Kband_Darray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'Kband_Darray.center.spw13.robust{robust}.withcont.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_selfcal],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

logprint("Step 7b: NH3 7-7 selfcal imaging (spw 18)")
# UV continuum subtraction for spw 18 (selfcal data)
uvcontsub_vis_spw18_selfcal = vis_selfcal.replace('.ms', '.spw18.contsub')
if not os.path.exists(uvcontsub_vis_spw18_selfcal):
    uvcontsub(vis=vis_selfcal,
              outputvis=uvcontsub_vis_spw18_selfcal,
              spw='18',
              fitspec='18:100~800',
              fitorder=0)

# Clean spw 18 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw18_selfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='18',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 18 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'Kband_Darray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_selfcal],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='18',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

logprint("Step 7c: KCl selfcal imaging (spw 26)")
# UV continuum subtraction for spw 26 (selfcal data)
uvcontsub_vis_spw26_selfcal = vis_selfcal.replace('.ms', '.spw26.contsub')
if os.path.exists(uvcontsub_vis_spw26_selfcal):
    shutil.rmtree(uvcontsub_vis_spw26_selfcal)

uvcontsub(vis=vis_selfcal,
          outputvis=uvcontsub_vis_spw26_selfcal,
          spw='26',
          fitspec='26:100~800',
              fitorder=0)

# Clean spw 26 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Darray.center.spw26.KCl.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw26_selfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='26',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 26 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'Kband_Darray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'Kband_Darray.center.spw26.KCl.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_selfcal],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='26',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for all selfcal cube images to save space
logprint("Cleaning up selfcal cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kband_Darray.center.spw13.robust{robust}.contsub.selfcal.clean',
                       f'Kband_Darray.center.spw13.robust{robust}.withcont.selfcal.clean',
                       f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.contsub.selfcal.clean',
                       f'Kband_Darray.center.spw18.NH3_7-7.robust{robust}.withcont.selfcal.clean',
                       f'Kband_Darray.center.spw26.KCl.robust{robust}.contsub.selfcal.clean',
                       f'Kband_Darray.center.spw26.KCl.robust{robust}.withcont.selfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

logprint("Imaging complete!")
