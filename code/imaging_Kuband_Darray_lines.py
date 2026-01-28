# sbatch --job-name=casa_22A-020_KuD_lines --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KuD_lines_%j.log --wrap "xvfb-run -a /orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kuband_Darray_lines.py"


# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854545_1_1.59783.16907671296/pipeline-20220725T214145/html/t2-1.html?sidebar=sidebar_22A_020_sb41854545_1_1_59783_16907671296_ms&subpage=listobs.txt
import os
import shutil
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Darray')
vis = ['../22A-020_sb41854545_1_1.59783.16907671296/22A-020_sb41854545_1_1.59783.16907671296.ms']
listobs(vis[0], listfile='Kuband_Darray.listobs', overwrite=True)

vis_split = vis[0].replace('.ms', '.split.ms')

def logprint(string, origin='imaging_Kuband_Darray.py', priority='INFO', flush=True):
    print(string, flush=flush)
    casalog.post(string, origin=origin, priority=priority)

logprint(f"CASA log file: {casalog.logfile()}")
# 2           1 7.2147e-07     0.434501 13.026012279345801 0.6251501990154984                0.0   v=0-0 J=1-0     0     0     1     0    48    16
# spw13: NaCl 1-0
# KClv=0                       15.378087          2-1
# spw29: KCl 1-0

contspw = [0,2,3,4,6,9,30,31,32]

logprint("Step 2: Non-selfcal imaging of spw 13 BEFORE deep cleaning/selfcal")
# UV continuum subtraction for spw 13 (non-selfcal data only)
uvcontsub_vis_noselfcal = vis_split.replace('.ms', '.spw13.contsub')
if not os.path.exists(uvcontsub_vis_noselfcal):
    uvcontsub(vis=vis_split,
              outputvis=uvcontsub_vis_noselfcal,
              spw='13',
              fitspec='13:250~750',
              fitorder=0,
              )

# Clean spw 13 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kuband_Darray.sgrb2.spw13.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_noselfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 13 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    # Use the lite continuum model created at the beginning
    contmodel = f'Kuband_Darray.center.robust{robust}.continuum.big-coarse.liteclean.model.tt0',

    imagename = f'Kuband_Darray.sgrb2.spw13.robust{robust}.withcont.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False,
               # startmodel does not work, don't know why. startmodel=contmodel,
               # AssertionError: {'startmodel': ['must be of cVariant type']}
               )

# Cleanup: Remove .pb, .mask, .psf files for spw 13 cube images to save space
logprint("Cleaning up spw 13 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Darray.sgrb2.spw13.robust{robust}.contsub.noselfcal.clean',
                       f'Kuband_Darray.sgrb2.spw13.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

logprint("Step 2b: H2CO 14.488 GHz imaging (spw 14)\nUV continuum subtraction for spw 14 (H2CO, non-selfcal data only)")
uvcontsub_vis_spw14_noselfcal = vis_split.replace('.ms', '.spw14.contsub')
if not os.path.exists(uvcontsub_vis_spw14_noselfcal):
    uvcontsub(vis=vis_split,
              outputvis=uvcontsub_vis_spw14_noselfcal,
              spw='14',
              fitspec='14:100~900',  # avoid line channels
              fitorder=0)

# Clean spw 14 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw14_noselfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='14',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 14 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    imagename = f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.withcont.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='14',
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 14 cube images to save space
logprint("Cleaning up spw 14 cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.contsub.noselfcal.clean',
                       f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.withcont.noselfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

# First check what spws exist in vis_selfcal
from casatools import msmetadata
msmd = msmetadata()
msmd.open(vis_selfcal)
spws = msmd.spwsforfield('sgr b2b')
logprint(f"Available spws in {vis_selfcal}: {spws}")
msmd.close()

logprint("Step 7: Selfcal imaging of spw 13 AFTER selfcal")
# UV continuum subtraction for spw 13 (selfcal data)
logprint(f"Creating uvcontsub for selfcal data: vis_selfcal={vis_selfcal}")
uvcontsub_vis_selfcal = vis_selfcal.replace('.ms', '.spw13.contsub')
if os.path.exists(uvcontsub_vis_selfcal):
    shutil.rmtree(uvcontsub_vis_selfcal)

uvcontsub(vis=vis_selfcal,
            outputvis=uvcontsub_vis_selfcal,
            spw='13',
            fitspec='13:250~750',
            fitorder=0,
            )
logprint(f"Created uvcontsub output: {uvcontsub_vis_selfcal}")

# Clean spw 13 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'Kuband_Darray.sgrb2.spw13.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        logprint(f"Cleaning {imagename} from {uvcontsub_vis_selfcal}")
        tclean(vis=uvcontsub_vis_selfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 13 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'Kuband_Darray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'Kuband_Darray.sgrb2.spw13.robust{robust}.withcont.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_selfcal],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='13',
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False,
               #startmodel=contmodel
               )

# Cleanup: Remove .pb, .mask, .psf files for spw 13 selfcal cube images to save space
logprint("Cleaning up spw 13 selfcal cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Darray.sgrb2.spw13.robust{robust}.contsub.selfcal.clean',
                       f'Kuband_Darray.sgrb2.spw13.robust{robust}.withcont.selfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)

logprint("Step 7b: H2CO 14.488 GHz selfcal imaging (spw 14)")
# UV continuum subtraction for spw 14 (selfcal data)
uvcontsub_vis_spw14_selfcal = vis_selfcal.replace('.ms', '.spw14.contsub')
if not os.path.exists(uvcontsub_vis_spw14_selfcal):
    uvcontsub(vis=vis_selfcal,
              outputvis=uvcontsub_vis_spw14_selfcal,
              spw='14',
              fitspec='14:100~900',
              fitorder=0)

logprint("Clean spw 14 WITH uvcontsub (selfcal only)")
for robust in (0, 2):
    imagename = f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw14_selfcal,
               datacolumn='data',
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='14',  # uvcontsub preserves original spw numbering
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 14 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'Kuband_Darray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.withcont.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=[vis_selfcal],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='14',
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Cleanup: Remove .pb, .mask, .psf files for spw 14 selfcal cube images to save space
logprint("Cleaning up spw 14 selfcal cube auxiliary files...")
for robust in (0, 2):
    for suffix in ['pb', 'mask', 'psf']:
        for prefix in [f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.contsub.selfcal.clean',
                       f'Kuband_Darray.sgrb2.spw14.H2CO.robust{robust}.withcont.selfcal.clean']:
            fname = f'{prefix}.{suffix}'
            if os.path.exists(fname):
                logprint(f"  Removing {fname}")
                shutil.rmtree(fname)



if False:
    for spw in (range(32,0,-1)):
        if not os.path.exists(f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean.psf'):
            tclean(vis=vis,
                   imagename=f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean',
                   #phasecenter='ICRS 17h47m19.87 -28d22m18.5',
                   niter=1000, spw=str(spw), field='sgr b2b', imsize=[600],
                   cell=['0.5arcsec'], specmode='cube', weighting='briggs',
                   robust=0.5, parallel=False)
