# sbatch --job-name=casa_22A-020_KD --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KD_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kband_Darray.py"

import os
import shutil
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Darray')

def logprint(string, origin='imaging_Kband_Darray.py', priority='INFO'):
    print(string)
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

logprint("Step 1: Preliminary imaging")
for robust in (0,2):
    if not os.path.exists(f'Kband_Darray.center.robust{robust}.continuum.big-coarse.liteclean.psf.tt0'):
        tclean(vis=vis,
               imagename=f'Kband_Darray.center.robust{robust}.continuum.big-coarse.liteclean',
               niter=1000, spw=",".join(map(str,contspw)), field='sgr b2b', imsize=[700],
               cell=['0.25arcsec'], specmode='mfs', weighting='briggs',
               deconvolver='mtmfs',
               nterms=2,
               robust=robust, parallel=False,
               mask='clean_mask.crtf')



logprint("Step 2: Split the data first to create working copy")
vis_split = vis[0].replace('.ms', '.split.ms')
if not os.path.exists(vis_split):
    split(vis=vis[0],
          outputvis=vis_split,
          field='sgr b2b',
          datacolumn='corrected')

logprint("Step 4a: Split continuum spws separately and average all channels for better SNR")
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

logprint("Step 4b: Deep continuum clean for self-calibration on channel-averaged data")

startmodel = ''
for robust in (2, 0):
    imagename = f'Kband_Darray.center.robust{robust}.continuum.deepclean'
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
               niter=100000,
               threshold='0.5mJy',
               spw='',  # use all spws in the averaged MS
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
               startmodel=startmodel, # use the other robust's model as the startmodel
               mask='' if os.path.exists(f'{imagename}.mask') else 'clean_mask.crtf')
        startmodel = f'{imagename}.model.tt0'


stats = visstat(vis=vis_contavg, datacolumn='model')
has_model = False
for key in stats:
    # RMS can be scalar or array depending on data shape
    rms = stats[key]['rms']
    if hasattr(rms, '__len__'):
        has_model_ = rms[0] > 0 or rms[1] > 0
    else:
        has_model_ = rms > 0
    logprint(f'MS file {vis_contavg}[{key}] {"has model" if has_model_ else "model is zero"}  (rms={stats[key]["rms"]})')
    has_model = (has_model or has_model_)  # ANY spw with model is good enough

if not has_model:
    # populate all model columns for all spws
    logprint(f"Model column not properly populated, using ft to populate from {imagename}.model.tt0/tt1")
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
    imagename = f'Kband_Darray.center.robust{robust}.continuum.deepclean'
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

logprint("Step 5: Self-calibration on channel-averaged continuum")
caltable = 'Kband_Darray.center.pcal1'
# CRITICAL: Verify model column is populated before running gaincal
# If model is empty, gaincal will corrupt the data!
stats = visstat(vis=vis_contavg, datacolumn='model', useflags=False)
has_any_model = False
for key in stats:
    rms = stats[key]['rms']
    has_rms = (rms[0] > 0 or rms[1] > 0) if hasattr(rms, '__len__') else (rms > 0)
    if has_rms:
        has_any_model = True
        logprint(f'{key} has model with rms={stats[key]["rms"]}')
if not has_any_model:
    raise RuntimeError("FATAL ERROR: Model column is empty! Cannot run gaincal - this would corrupt the data!")
logprint("\u2713 Model column verified - proceeding with gaincal")
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
    #logprint("Creating diagnostic plots for calibration table...")
    #plotms(vis=caltable,
    #       xaxis='time',
    #       yaxis='phase',
    #       coloraxis='antenna1',
    #       plotfile=f'{caltable}_phase_vs_time.png',
    #       showgui=False,
    #       overwrite=True,
    #       plotrange=[-1,-1,-180,180])
    #plotms(vis=caltable,
    #       xaxis='time',
    #       yaxis='amp',
    #       coloraxis='antenna1',
    #       plotfile=f'{caltable}_amp_vs_time.png',
    #       showgui=False,
    #       overwrite=True)
    #plotms(vis=caltable,
    #       xaxis='antenna1',
    #       yaxis='phase',
    #       coloraxis='corr',
    #       plotfile=f'{caltable}_phase_vs_antenna.png',
    #       showgui=False,
    #       overwrite=True,
    #       plotrange=[-1,-1,-180,180])
    #plotms(vis=caltable,
    #       xaxis='antenna1',
    #       yaxis='snr',
    #       coloraxis='corr',
    #       plotfile=f'{caltable}_snr_vs_antenna.png',
    #       showgui=False,
    #       overwrite=True)
    #logprint(f"Diagnostic plots saved: {caltable}_*.png")

# Apply phase calibration to the full split MS (with proper spwmap)
vis_selfcal = vis[0].replace('.ms', '.selfcal.ms')
if os.path.exists(vis_selfcal):
    shutil.rmtree(vis_selfcal)

# Map all spws to the combined solution
# The caltable has solutions for the continuum spws only
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
if os.path.exists(vis_selfcal_contavg):
    shutil.rmtree(vis_selfcal_contavg)

from casatasks import mstransform
mstransform(vis=vis_selfcal,
            outputvis=vis_selfcal_contavg,
            field='sgr b2b',
            spw=",".join(map(str, contspw)),
            datacolumn='data',
            chanaverage=True,
            chanbin=999999,  # average all channels in each spw
            combinespws=False)

logprint("Step 6: Reimage continuum with selfcal")
for robust in (0, 2):
    imagename = f'Kband_Darray.center.robust{robust}.continuum.deepclean.selfcal'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=[vis_selfcal_contavg],
               imagename=imagename,
               niter=100000,
               threshold='0.5mJy',
               spw='',  # use all spws in the averaged MS
               field='sgr b2b',
               imsize=[700],
               cell=['0.25arcsec'],
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
    imagename = f'Kband_Darray.center.robust{robust}.continuum.deepclean.selfcal'
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

