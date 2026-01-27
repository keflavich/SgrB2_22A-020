# sbatch --job-name=casa_22A-020_KuD --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KuD_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kuband_Darray.py"


# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854545_1_1.59783.16907671296/pipeline-20220725T214145/html/t2-1.html?sidebar=sidebar_22A_020_sb41854545_1_1_59783_16907671296_ms&subpage=listobs.txt
import os
import shutil
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Darray')
logprint(f"CASA log file: {casalog.logfile()}")
vis = ['../22A-020_sb41854545_1_1.59783.16907671296/22A-020_sb41854545_1_1.59783.16907671296.ms']
listobs(vis[0], listfile='Kuband_Darray.listobs', overwrite=True)

def logprint(string, origin='imaging_Kuband_Darray.py', priority='INFO'):
    print(string)
    casalog.post(string, origin=origin, priority=priority)

# 2           1 7.2147e-07     0.434501 13.026012279345801 0.6251501990154984                0.0   v=0-0 J=1-0     0     0     1     0    48    16
# spw13: NaCl 1-0
# KClv=0                       15.378087          2-1
# spw29: KCl 1-0

contspw = [0,2,3,4,6,9,30,31,32]

for robust in (0,2):
    if not os.path.exists(f'Kuband_Darray.center.robust{robust}.continuum.big-coarse.liteclean.psf.tt0'):
        tclean(vis=vis,
               imagename=f'Kuband_Darray.center.robust{robust}.continuum.big-coarse.liteclean',
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

logprint("Step 1: Split the data first to create working copy")
vis_split = vis[0].replace('.ms', '.split.ms')
if not os.path.exists(vis_split):
    split(vis=vis[0],
          outputvis=vis_split,
          field='sgr b2b',
          datacolumn='corrected')

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

logprint("Step 3a: Split continuum spws separately and average all channels for better SNR")
vis_contavg = vis_split.replace('.ms', '.contavg.ms')
if not os.path.exists(vis_contavg):
    # Use mstransform to split continuum spws and average all channels
    from casatasks import mstransform
    mstransform(vis=vis_split,
                outputvis=vis_contavg,
                field='sgr b2b',
                spw=",".join(map(str, contspw)),
                datacolumn='data',
                chanaverage=True,
                chanbin=999999,  # average all channels in each spw
                combinespws=False)  # keep spws separate for now

logprint("Step 3b: Deep continuum clean for self-calibration on channel-averaged data")

startmodel = ''
for robust in (2, 0):
    imagename = f'Kuband_Darray.center.robust{robust}.continuum.deepclean'
    if os.path.exists(f'{imagename}.model.tt0'):
        imhist = imhistory(f'{imagename}.model.tt0')
        if not any(vis_contavg in x for x in imhist):
            vis_entries = [row for row in imhist if row.startswith('vis')]
            if vis_entries:
                logprint(f"Model was created with: {vis_entries[0]}")
            logprint(f"Removing {imagename} files and reimaging")
            for suffix in ('alpha', 'alpha.error', 'image.tt0', 'image.tt1', 'mask', 'model.tt0', 'model.tt1', 'pb.tt0', 'psf.tt0', 'psf.tt1', 'psf.tt2', 'residual.tt0', 'residual.tt1', 'sumwt.tt0','sumwt.tt1', 'sumwt.tt2'):
                if os.path.exists(f'{imagename}.{suffix}'):
                    shutil.rmtree(f'{imagename}.{suffix}')

    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_contavg],
               imagename=imagename,
               niter=10000,
               threshold='25mJy',
               spw='',  # use all spws in the averaged MS
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
               startmodel=startmodel, # use the other robust's model as the startmodel
               mask='' if os.path.exists(f'{imagename}.mask') else 'clean_mask.crtf')
        startmodel = f'{imagename}.model.tt0'


stats = visstat(vis=vis_contavg, datacolumn='model', useflags=False)
has_model = False
for key in stats:
    # RMS can be scalar or array depending on data shape
    rms = stats[key]['rms']
    if hasattr(rms, '__len__'):
        has_model_ = rms[0] > 0 or rms[1] > 0
    else:
        has_model_ = rms > 0
    logprint(f'MS file {vis_contavg}[{key}] {"has model" if has_model_ else "model is zero"}  (rms={stats[key]["rms"]})', flush=True)
    has_model = (has_model or has_model_)  # ANY spw with model is good enough

if not has_model:
    # populate all model columns for all spws
    logprint(f"Model column not properly populated, using ft to populate from {imagename}.model.tt0/tt1", flush=True)
    delmod(vis_contavg)
    ft(
        vis=vis_contavg,
        field='sgr b2b',
        spw='',  # populate all spws
        model=[imagename+'.model.tt0', imagename+'.model.tt1'],
        nterms=2,
        reffreq='',
        usescratch=True,
        incremental=False
    )
    # Verify it worked
    stats_after = visstat(vis=vis_contavg, datacolumn='model', useflags=False)
    has_model_after = False
    for key in stats_after:
        rms = stats_after[key]['rms']
        has_rms = (rms[0] > 0 or rms[1] > 0) if hasattr(rms, '__len__') else (rms > 0)
        if has_rms:
            has_model_after = True
            break
    if not has_model_after:
        raise RuntimeError("FATAL: Model column still not populated after ft! Cannot proceed with gaincal.")


# Convolve model with synthesized beam to create realistic model image
for robust in (0, 2):
    imagename = f'Kuband_Darray.center.robust{robust}.continuum.deepclean'
    model_conv = f'{imagename}.model.conv.tt0'
    if not os.path.exists(model_conv):
        # Get beam from restored image
        beam = imhead(imagename=f'{imagename}.image.tt0', mode='get', hdkey='beammajor')
        bmaj = beam['value']
        bmin = imhead(imagename=f'{imagename}.image.tt0', mode='get', hdkey='beamminor')['value']
        bpa = imhead(imagename=f'{imagename}.image.tt0', mode='get', hdkey='beampa')['value']
        imsmooth(imagename=f'{imagename}.model.tt0',
                 kernel='gauss',
                 major=str(bmaj)+beam['unit'],
                 minor=str(bmin)+beam['unit'],
                 pa=str(bpa)+'deg',
                 outfile=model_conv,
                 overwrite=True)

logprint("Step 4: Self-calibration on channel-averaged continuum")
# Phase-only self-calibration (only need to do once, not per robust)
caltable = 'Kuband_Darray.center.pcal1'
# CRITICAL: Verify model column is populated before running gaincal
# If model is empty, gaincal will corrupt the data!
stats = visstat(vis=vis_contavg, datacolumn='model', useflags=False)
has_any_model = False
for key in stats:
    rms = stats[key]['rms']
    has_rms = (rms[0] > 0 or rms[1] > 0) if hasattr(rms, '__len__') else (rms > 0)
    if has_rms:
        has_any_model = True
        logprint(f'{key} has model with rms={stats[key]["rms"]}', flush=True)
if not has_any_model:
    raise RuntimeError("FATAL ERROR: Model column is empty! Cannot run gaincal - this would corrupt the data!")
logprint("\u2713 Model column verified - proceeding with gaincal", flush=True)
if os.path.exists(caltable):
    rmtables(caltable)
gaincal(vis=vis_contavg,
        caltable=caltable,
        field='sgr b2b',
        solint='inf',
        refant='ea10',
        refantmode='flex',
        minsnr=3.0,
        combine='spw',
        calmode='p',
        gaintype='G')

# Diagnostic plots for gaincal solutions
logprint("Creating diagnostic plots for calibration table...")
plotms(vis=caltable,
       xaxis='time',
       yaxis='phase',
       coloraxis='antenna1',
       plotfile=f'{caltable}_phase_vs_time.png',
       showgui=False,
       overwrite=True,
       plotrange=[-1,-1,-180,180])
plotms(vis=caltable,
       xaxis='time',
       yaxis='amp',
       coloraxis='antenna1',
       plotfile=f'{caltable}_amp_vs_time.png',
       showgui=False,
       overwrite=True)
plotms(vis=caltable,
       xaxis='antenna1',
       yaxis='phase',
       coloraxis='corr',
       plotfile=f'{caltable}_phase_vs_antenna.png',
       showgui=False,
       overwrite=True,
       plotrange=[-1,-1,-180,180])
plotms(vis=caltable,
       xaxis='antenna1',
       yaxis='snr',
       coloraxis='corr',
       plotfile=f'{caltable}_snr_vs_antenna.png',
       showgui=False,
       overwrite=True)
logprint(f"Diagnostic plots saved: {caltable}_*.png")

# Apply phase calibration to the full split MS (with proper spwmap)
# Create spwmap: all continuum spws map to spw 0 in the caltable
vis_selfcal = vis[0].replace('.ms', '.selfcal.ms')
if os.path.exists(vis_selfcal):
    shutil.rmtree(vis_selfcal)

# Map all spws to the combined solution
# The caltable has solutions for the continuum spws only
# We need to map each spw in vis_split to the appropriate solution
# Since we used combine='spw', there's one solution for all
# Determine number of SPWs from the MS
from casatools import msmetadata
msmd = msmetadata()
msmd.open(vis_split)
nspws = msmd.nspw()
msmd.close()
spwmap = [0] * nspws  # map all spws to solution 0

applycal(vis=vis_split,
         field='sgr b2b',
         gaintable=[caltable],
         interp='linear',
         spwmap=[spwmap],
         applymode='calonly')

split(vis=vis_split,
        outputvis=vis_selfcal,
        field='sgr b2b',
        datacolumn='corrected')

logprint("Step 5: Create channel-averaged continuum MS from selfcal data")
vis_selfcal_contavg = vis_selfcal.replace('.ms', '.contavg.ms')
if not os.path.exists(vis_selfcal_contavg):
    from casatasks import mstransform
    mstransform(vis=vis_selfcal,
                outputvis=vis_selfcal_contavg,
                field='sgr b2b',
                spw=",".join(map(str, contspw)),
                datacolumn='data',
                chanaverage=True,
                chanbin=999999,  # average all channels in each spw
                combinespws=False)

logprint("Step 6: Reimage continuum with selfcal using deep clean parameters")
for robust in (0, 2):
    imagename = f'Kuband_Darray.center.robust{robust}.continuum.deepclean.selfcal'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_selfcal_contavg],
               imagename=imagename,
               niter=100000,
               threshold='0.5mJy',
               spw='',  # use all spws in the averaged MS
               field='sgr b2b',
               imsize=[600],
               cell=['0.5arcsec'],
               specmode='mfs',
               weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust,
               parallel=False,
               mask='clean_mask.crtf',
               savemodel='modelcolumn')

# Convolve model with synthesized beam to create realistic model image
for robust in (0, 2):
    imagename = f'Kuband_Darray.center.robust{robust}.continuum.deepclean.selfcal'
    model_conv = f'{imagename}.model.conv.tt0'
    if not os.path.exists(model_conv):
        # Get beam from restored image
        beam = imhead(imagename=f'{imagename}.image.tt0', mode='get', hdkey='beammajor')
        bmaj = beam['value']
        bmin = imhead(imagename=f'{imagename}.image.tt0', mode='get', hdkey='beamminor')['value']
        bpa = imhead(imagename=f'{imagename}.image.tt0', mode='get', hdkey='beampa')['value']
        imsmooth(imagename=f'{imagename}.model.tt0',
                 kernel='gauss',
                 major=str(bmaj)+beam['unit'],
                 minor=str(bmin)+beam['unit'],
                 pa=str(bpa)+'deg',
                 outfile=model_conv,
                 overwrite=True)

logprint("Step 7: Selfcal imaging of spw 13 AFTER selfcal")
# UV continuum subtraction for spw 13 (selfcal data)
logprint(f"Creating uvcontsub for selfcal data: vis_selfcal={vis_selfcal}")
uvcontsub_vis_selfcal = vis_selfcal.replace('.ms', '.spw13.contsub')
if os.path.exists(uvcontsub_vis_selfcal):
    shutil.rmtree(uvcontsub_vis_selfcal)

# First check what spws exist in vis_selfcal
from casatools import msmetadata
msmd = msmetadata()
msmd.open(vis_selfcal)
spws = msmd.spwsforfield('sgr b2b')
logprint(f"Available spws in {vis_selfcal}: {spws}")
msmd.close()

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

logprint("Imaging complete!")
