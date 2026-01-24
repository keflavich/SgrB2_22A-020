# sbatch --job-name=casa_22A-020_KD --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KD_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kband_Darray.py"

import os
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Darray')
print(f"CASA log file: {casalog.logfile()}")
# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854998_1_1.59785.110016307866/pipeline-20220726T015648/html/t2-1.html?sidebar=sidebar_22A_020_sb41854998_1_1_59785_110016307866_ms&subpage=listobs.txt

# NaCl v=0 2-1; 26.0518979GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# NaCl v=1 2-1; 25.8582961GHz; Lsr Kinematic; Radio; 60.0km/s; 200.0km/s; 1.0km/s; DUAL; USE_RECIRCULATION=true
# spw13: v=0 2-1
# spw14: v=1 2-1
# spw36: water

vis = ['../22A-020_sb41854998_1_1.59785.110016307866/22A-020_sb41854998_1_1.59785.110016307866.ms']

contspw = [4,5,6,7,8,9,10,11, 27,28,29,30,31,32,33,34]
# 4-11, 27-34

# Step 1: Preliminary imaging
for robust in (0,2):
    if not os.path.exists(f'KbandDarray.center.robust{robust}.continuum.big-coarse.liteclean.psf.tt0'):
        tclean(vis=vis,
               imagename=f'KbandDarray.center.robust{robust}.continuum.big-coarse.liteclean',
               niter=1000, spw=",".join(map(str,contspw)), field='sgr b2b', imsize=[700],
               cell=['0.25arcsec'], specmode='mfs', weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust, parallel=False,
               mask='clean_mask.crtf')

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

# Step 2: Split the data first to create working copy
vis_split = vis[0].replace('.ms', '.split.ms')
if not os.path.exists(vis_split):
    split(vis=vis[0],
          outputvis=vis_split,
          field='sgr b2b',
          datacolumn='corrected')

# Step 3: Non-selfcal imaging of NaCl line spws BEFORE deep cleaning/selfcal
# UV continuum subtraction for spw 13 (NaCl v=0 2-1)
uvcontsub_vis_spw13_noselfcal = vis_split.replace('.ms', '.spw13.contsub')
if not os.path.exists(uvcontsub_vis_spw13_noselfcal):
    uvcontsub(vis=vis_split,
              outputvis=uvcontsub_vis_spw13_noselfcal,
              spw='13',
              fitspec='13:100~800',
              fitorder=0)

# Clean spw 13 WITH uvcontsub (non-selfcal only)
for robust in (0, 2):
    imagename = f'KbandDarray.center.spw13.robust{robust}.contsub.noselfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw13_noselfcal,
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='0',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 13 WITHOUT uvcontsub using lite continuum model as startmodel (non-selfcal only)
for robust in (0, 2):
    contmodel = f'KbandDarray.center.robust{robust}.continuum.big-coarse.liteclean.model.tt0',
    imagename = f'KbandDarray.center.spw13.robust{robust}.withcont.noselfcal.clean'
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

# Step 4: Deep continuum clean for self-calibration on split data
for robust in (0, 2):
    imagename = f'KbandDarray.center.robust{robust}.continuum.deepclean'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_split],
               imagename=imagename,
               niter=100000,
               threshold='0.5mJy',
               spw=",".join(map(str, contspw)),
               field='sgr b2b',
               imsize=[700],
               cell=['0.25arcsec'],
               specmode='mfs',
               weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust,
               parallel=False,
               savemodel='modelcolumn',
               mask='clean_mask.crtf')

# Step 5: Self-calibration on continuum
caltable = 'KbandDarray.center.pcal1'
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

# Step 6: Selfcal imaging of NaCl line spws AFTER selfcal
# UV continuum subtraction for spw 13 (selfcal data)
uvcontsub_vis_spw13_selfcal = vis_selfcal.replace('.ms', '.spw13.contsub')
if not os.path.exists(uvcontsub_vis_spw13_selfcal):
    uvcontsub(vis=vis_selfcal,
              outputvis=uvcontsub_vis_spw13_selfcal,
              spw='13',
              fitspec='13:100~800',
              fitorder=0)

# Clean spw 13 WITH uvcontsub (selfcal only)
for robust in (0, 2):
    imagename = f'KbandDarray.center.spw13.robust{robust}.contsub.selfcal.clean'
    if not os.path.exists(f'{imagename}.psf'):
        tclean(vis=uvcontsub_vis_spw13_selfcal,
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='0',
               field='sgr b2b',
               imsize=[500],
               cell=['0.5arcsec'],
               specmode='cube',
               weighting='briggs',
               robust=robust,
               parallel=False)

# Clean spw 13 WITHOUT uvcontsub using deep continuum model as startmodel (selfcal only)
for robust in (0, 2):
    contmodel = f'KbandDarray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'KbandDarray.center.spw13.robust{robust}.withcont.selfcal.clean'
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

# Step 7: Reimage continuum with selfcal
for robust in (0, 2):
    imagename = f'KbandDarray.center.robust{robust}.continuum.deepclean.selfcal'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_selfcal],
               imagename=imagename,
               niter=100000,
               threshold='0.5mJy',
               spw=",".join(map(str, contspw)),
               field='sgr b2b',
               imsize=[700],
               cell=['0.25arcsec'],
               specmode='mfs',
               weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust,
               parallel=False,
               mask='clean_mask.crtf')



