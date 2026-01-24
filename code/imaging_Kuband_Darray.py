# sbatch --job-name=casa_22A-020_KuD --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KuD_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kuband_Darray.py"


# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854545_1_1.59783.16907671296/pipeline-20220725T214145/html/t2-1.html?sidebar=sidebar_22A_020_sb41854545_1_1_59783_16907671296_ms&subpage=listobs.txt
import os
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Darray')
print(f"CASA log file: {casalog.logfile()}")
vis = ['../22A-020_sb41854545_1_1.59783.16907671296/22A-020_sb41854545_1_1.59783.16907671296.ms']

# 2           1 7.2147e-07     0.434501 13.026012279345801 0.6251501990154984                0.0   v=0-0 J=1-0     0     0     1     0    48    16
# spw13: NaCl 1-0
# KClv=0                       15.378087          2-1
# spw29: KCl 1-0

contspw = [0,2,3,4,6,9,30,31,32]

for robust in (0,2):
    if not os.path.exists(f'KubandDarray.center.robust{robust}.continuum.big-coarse.liteclean.psf.tt0'):
        tclean(vis=vis,
               imagename=f'KubandDarray.center.robust{robust}.continuum.big-coarse.liteclean',
               niter=1000, spw=",".join(map(str,contspw)), field='sgr b2b', imsize=[600],
               cell=['0.5arcsec'], specmode='mfs', weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust, parallel=False,
               mask='clean_mask.crtf')


for spw in (range(32,0,-1)):
    if not os.path.exists(f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'Kuband_Darray.sgrb2.spw{spw}.robust0.5.liteclean',
               #phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[600],
               cell=['0.5arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)

# UVcontsub spw 13 and then clean

# clean continuum based on the cont spws, then selfcal, then apply to spw 13 and clean both with and without uvcontsub (without uvcontsub, it should use the cleaned cont as a startmodel)

# Step 1: Split the data first to create working copy
vis_split = vis[0].replace('.ms', '.split.ms')
if not os.path.exists(vis_split):
    split(vis=vis[0],
          outputvis=vis_split,
          field='sgr b2b',
          datacolumn='corrected')

# Step 2: Non-selfcal imaging of spw 13 BEFORE deep cleaning/selfcal
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
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='0',
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
    contmodel = f'KubandDarray.center.robust{robust}.continuum.big-coarse.liteclean.model.tt0',

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

# Step 3: Deep continuum clean for self-calibration on split data
for robust in (0, 2):
    imagename = f'KubandDarray.center.robust{robust}.continuum.deepclean'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw=",".join(map(str, contspw)),
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='mfs',
               weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust,
               parallel=False,
               savemodel='modelcolumn',
               mask='clean_mask.crtf')

# Step 4: Self-calibration on continuum
# Phase-only self-calibration (only need to do once, not per robust)
caltable = 'KubandDarray.center.pcal1'
if not os.path.exists(caltable):
    gaincal(vis=vis_split,
            caltable=caltable,
            field='sgr b2b',
            solint='inf',
            refant='ea10',
            calmode='p',
            gaintype='G')

# Apply phase calibration and split to create selfcal MS
vis_selfcal = vis[0].replace('.ms', '.selfcal.ms')
if not os.path.exists(vis_selfcal):
    applycal(vis=vis_split,
             field='sgr b2b',
             gaintable=[caltable],
             interp='linear',
             applymode='calonly')
    
    split(vis=vis_split,
          outputvis=vis_selfcal,
          field='sgr b2b',
          datacolumn='corrected')

# Step 5: Selfcal imaging of spw 13 AFTER selfcal
# UV continuum subtraction for spw 13 (selfcal data)
print(f"Creating uvcontsub for selfcal data: vis_selfcal={vis_selfcal}")
uvcontsub_vis_selfcal = vis_selfcal.replace('.ms', '.spw13.contsub')
if not os.path.exists(uvcontsub_vis_selfcal):
    # First check what spws exist in vis_selfcal
    from casatools import msmetadata
    msmd = msmetadata()
    msmd.open(vis_selfcal)
    spws = msmd.spwsforfield('sgr b2b')
    print(f"Available spws in {vis_selfcal}: {spws}")
    msmd.close()
    
    uvcontsub(vis=vis_selfcal,
              outputvis=uvcontsub_vis_selfcal,
              spw='13',
              fitspec='13:250~750',
              fitorder=0,
              )
    print(f"Created uvcontsub output: {uvcontsub_vis_selfcal}")

# Clean spw 13 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'Kuband_Darray.sgrb2.spw13.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        print(f"Cleaning {imagename} from {uvcontsub_vis_selfcal}")
        tclean(vis=uvcontsub_vis_selfcal,
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='0',  # in the split file, spw13 is now spw0
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 13 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'KubandDarray.center.robust{robust}.continuum.deepclean.model.tt0'
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
