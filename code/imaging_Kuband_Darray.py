# sbatch --job-name=casa_22A-020_KuD --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KuD_%j.log --wrap "xvfb-run -a /orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --nologger --nogui --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kuband_Darray.py"


# https://data.rc.ufl.edu/secure/adamginsburg/SgrB2/22A-020/22A-020_sb41854545_1_1.59783.16907671296/pipeline-20220725T214145/html/t2-1.html?sidebar=sidebar_22A_020_sb41854545_1_1_59783_16907671296_ms&subpage=listobs.txt
import os
import shutil
from casatasks import mstransform
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Darray')
vis = ['../22A-020_sb41854545_1_1.59783.16907671296/22A-020_sb41854545_1_1.59783.16907671296.ms']
listobs(vis[0], listfile='Kuband_Darray.listobs', overwrite=True)

def logprint(string, origin='imaging_Kuband_Darray.py', priority='INFO', flush=True):
    print(string, flush=flush)
    casalog.post(string, origin=origin, priority=priority)
logprint(f"CASA log file: {casalog.logfile()}")

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


# clean continuum based on the cont spws, then selfcal, then apply to spw 13 and clean both with and without uvcontsub (without uvcontsub, it should use the cleaned cont as a startmodel)

logprint("Step 1: Split the data first to create working copy")
vis_split = vis[0].replace('.ms', '.split.ms')
if not os.path.exists(vis_split):
    split(vis=vis[0],
          outputvis=vis_split,
          field='sgr b2b',
          datacolumn='corrected')

logprint("Step 3a: Split continuum spws separately and average all channels for better SNR")
vis_contavg = vis_split.replace('.ms', '.contavg.ms')
if not os.path.exists(vis_contavg):
    # Use mstransform to split continuum spws and average all channels
    mstransform(vis=vis_split,
                outputvis=vis_contavg,
                field='sgr b2b',
                spw=",".join(map(str, contspw)),
                datacolumn='data',
                chanaverage=True,
                chanbin=12,  # average 12 channels in each spw - should have 10 left
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
                datacolumn='data', # important b/c we're going to populate 'corrected' below
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
caltable_nocombine = 'Kuband_Darray.center.pcal.nocombine'
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
logprint("Model column verified - proceeding with gaincal", flush=True)
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
gaincal(vis=vis_contavg,
        caltable=caltable_nocombine,
        field='sgr b2b',
        solint='inf',
        refant='ea10',
        refantmode='flex',
        minsnr=3.0,
        #combine='spw',
        calmode='p',
        gaintype='G')

# Diagnostic plots for gaincal solutions
logprint("Creating diagnostic plots for calibration table...")
#listcal(caltable=caltable) < --- doesn't work?  says 'vis must exist' ?
#plotcal(caltable=caltable, xaxis='time', yaxis='phase', figfile=f'{caltable}_phase_vs_time_plotcal.png', showgui=False)

for caltable_to_plot in (caltable, caltable_nocombine):
    plotms(vis=caltable_to_plot,
           xaxis='time',
           yaxis='phase',
           coloraxis='antenna1',
           plotfile=f'{caltable_to_plot}_phase_vs_time.png',
           showgui=False,
           overwrite=True,
           plotrange=[-1,-1,-180,180])
    plotms(vis=caltable_to_plot,
           xaxis='time',
           yaxis='amp',
           coloraxis='antenna1',
           plotfile=f'{caltable_to_plot}_amp_vs_time.png',
           showgui=False,
           overwrite=True)
    plotms(vis=caltable_to_plot,
           xaxis='antenna1',
           yaxis='phase',
           coloraxis='corr',
           plotfile=f'{caltable_to_plot}_phase_vs_antenna.png',
           showgui=False,
           overwrite=True,
           plotrange=[-1,-1,-180,180])
    plotms(vis=caltable_to_plot,
           xaxis='antenna1',
           yaxis='snr',
           coloraxis='corr',
           plotfile=f'{caltable_to_plot}_snr_vs_antenna.png',
           showgui=False,
           overwrite=True)
    logprint(f"Diagnostic plots saved: {caltable_to_plot}_*.png")

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

# this version fails and I don't know why.
applycal(vis=vis_split,
         field='sgr b2b',
         gaintable=[caltable],
         interp='linear',
         spwmap=[spwmap],
         applymode='calonly',
         calwt=False
         )

# no spwmap because it's the same file
applycal(vis=vis_contavg,
         field='sgr b2b',
         gaintable=[caltable],
         interp='linear',
         applymode='calonly',
         calwt=False
         )

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
               threshold='10mJy',
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
    imagename = f'Kuband_Darray.center.robust{robust}.continuum.deepclean.selfcal.preaveraged'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_contavg],
               datacolumn='corrected',
               imagename=imagename,
               niter=100000,
               threshold='10mJy',
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
               savemodel='none')

logprint("Step 7: Second round of phase-only self-calibration with 30s solution interval")
# Use the model from the selfcal imaging to do shorter timescale calibration
caltable2 = 'Kuband_Darray.center.pcal2_30s'
if os.path.exists(caltable2):
    rmtables(caltable2)
gaincal(vis=vis_selfcal_contavg,
        caltable=caltable2,
        field='sgr b2b',
        solint='30s',
        refant='ea10',
        refantmode='flex',
        minsnr=2.0,
        combine='spw',
        calmode='p',
        gaintype='G')

# Diagnostic plots for second round gaincal solutions
logprint("Creating diagnostic plots for second calibration table...")
plotms(vis=caltable2,
       xaxis='time',
       yaxis='phase',
       coloraxis='antenna1',
       plotfile=f'{caltable2}_phase_vs_time.png',
       showgui=False,
       overwrite=True,
       plotrange=[-1,-1,-180,180])
plotms(vis=caltable2,
       xaxis='time',
       yaxis='amp',
       coloraxis='antenna1',
       plotfile=f'{caltable2}_amp_vs_time.png',
       showgui=False,
       overwrite=True)
plotms(vis=caltable2,
       xaxis='antenna1',
       yaxis='phase',
       coloraxis='corr',
       plotfile=f'{caltable2}_phase_vs_antenna.png',
       showgui=False,
       overwrite=True,
       plotrange=[-1,-1,-180,180])
plotms(vis=caltable2,
       xaxis='antenna1',
       yaxis='snr',
       coloraxis='corr',
       plotfile=f'{caltable2}_snr_vs_antenna.png',
       showgui=False,
       overwrite=True)
logprint(f"Diagnostic plots saved: {caltable2}_*.png")

# Apply second calibration
applycal(vis=vis_selfcal_contavg,
         field='sgr b2b',
         gaintable=[caltable2],
         interp='linear',
         applymode='calonly',
         calwt=False)

# Create second selfcal MS
vis_selfcal2 = vis[0].replace('.ms', '.selfcal2.ms')
if os.path.exists(vis_selfcal2):
    shutil.rmtree(vis_selfcal2)

# Apply second calibration to full resolution data
msmd.open(vis_selfcal)
nspws_selfcal = msmd.nspw()
msmd.close()
spwmap2 = [0] * nspws_selfcal

applycal(vis=vis_selfcal,
         field='sgr b2b',
         gaintable=[caltable2],
         interp='linear',
         spwmap=[spwmap2],
         applymode='calonly',
         calwt=False)

split(vis=vis_selfcal,
      outputvis=vis_selfcal2,
      field='sgr b2b',
      datacolumn='corrected')

logprint("Step 8: Create channel-averaged continuum MS from second selfcal")
vis_selfcal2_contavg = vis_selfcal2.replace('.ms', '.contavg.ms')
if not os.path.exists(vis_selfcal2_contavg):
    mstransform(vis=vis_selfcal2,
                outputvis=vis_selfcal2_contavg,
                field='sgr b2b',
                spw=",".join(map(str, contspw)),
                datacolumn='data',
                chanaverage=True,
                chanbin=999999,
                combinespws=False)

logprint("Step 9: Final imaging with second selfcal")
for robust in (0, 2):
    imagename = f'Kuband_Darray.center.robust{robust}.continuum.deepclean.selfcal2'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_selfcal2_contavg],
               imagename=imagename,
               niter=100000,
               threshold='5mJy',
               spw='',
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


logprint("Imaging complete!")
