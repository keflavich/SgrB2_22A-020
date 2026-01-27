# sbatch --job-name=casa_22A-020_KA_line --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KA_lines_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kband_Aarray_lines.py"

import os
import shutil
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Aarray')

def logprint(string, origin='imaging_Kband_Aarray.py', priority='INFO'):
    print(string)
    casalog.post(string, origin=origin, priority=priority)

logprint(f"CASA log file: {casalog.logfile()}")
# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41852157_1_1.59747.288797835645/pipeline-20220627T225838/html/t2-1.html?sidebar=sidebar_22A_020_sb41852157_1_1_59747_288797835645_ms&subpage=t2-2-2.html

# NaCl v=0 2-1; 26.0518979GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# NaCl v=1 2-1; 25.8582961GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true

vis = ['../22A-020_sb41852157_1_1.59747.288797835645/22A-020_sb41852157_1_1.59747.288797835645.ms']

contspw = [18,19,20,21,22,23,24,25,30,31,32,33,34,46,47,48]

for spw in (45,):
    for robust in (0, 2):
        if not os.path.exists(f'Kband_Aarray.center.robust{robust}.spw{spw}.big-coarse.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'Kband_Aarray.center.robust{robust}.spw{spw}.big-coarse.liteclean',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
                   cell=['0.05arcsec'], specmode='cube', weighting='briggs',
                   robust=robust, parallel=False)

for spw in (range(48,2,-1)):
    if spw in contspw:
        continue
    if not os.path.exists(f'Kband_Aarray.sgrb2n.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'Kband_Aarray.sgrb2n.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)
    if not os.path.exists(f'Kband_Aarray.sgrb2m.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'Kband_Aarray.sgrb2m.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m20.16 -28d23m04.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)


logprint("Step 3: Non-selfcal imaging of NaCl line spws BEFORE deep cleaning/selfcal")
# UV continuum subtraction for spw 45
uvcontsub_vis_spw45_noselfcal = vis_split.replace('.ms', '.spw45.contsub')
if not os.path.exists(uvcontsub_vis_spw45_noselfcal):
    uvcontsub(vis=vis_split,
              outputvis=uvcontsub_vis_spw45_noselfcal,
              spw='45',
              fitspec='45:100~800',
              fitorder=0)

# Clean spw 45 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Aarray.center.spw45.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw45_noselfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='45',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[2000],
               cell=['0.05arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 45 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    contmodel = f'Kband_Aarray.center.robust{robust}.continuum.big-coarse.liteclean.model.tt0',
    imagename = f'Kband_Aarray.center.spw45.robust{robust}.withcont.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='45',
               field='sgr b2b',
               imsize=[2000],
               cell=['0.05arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 45 cube images to save space
logprint("Cleaning up spw 45 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kband_Aarray.center.spw45.robust{robust}.contsub.noselfcal.clean',
                       f'Kband_Aarray.center.spw45.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)


logprint("Step 7: Selfcal imaging of NaCl line spws AFTER selfcal")
# UV continuum subtraction for spw 45 (selfcal data)
uvcontsub_vis_spw45_selfcal = vis_selfcal.replace('.ms', '.spw45.contsub')
if os.path.exists(uvcontsub_vis_spw45_selfcal):
    shutil.rmtree(uvcontsub_vis_spw45_selfcal)

uvcontsub(vis=vis_selfcal,
          outputvis=uvcontsub_vis_spw45_selfcal,
          spw='45',
          fitspec='45:100~800',
          fitorder=0)

# Clean spw 45 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'Kband_Aarray.center.spw45.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw45_selfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='45',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[2000],
               cell=['0.05arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 45 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'Kband_Aarray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'Kband_Aarray.center.spw45.robust{robust}.withcont.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_selfcal],
               imagename=imagename,
               niter=10000,
               threshold='1mJy',
               spw='45',
               field='sgr b2b',
               imsize=[2000],
               cell=['0.05arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 45 selfcal cube images to save space
logprint("Cleaning up spw 45 selfcal cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kband_Aarray.center.spw45.robust{robust}.contsub.selfcal.clean',
                       f'Kband_Aarray.center.spw45.robust{robust}.withcont.selfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)
