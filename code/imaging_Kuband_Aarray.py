# sbatch --job-name=casa_22A-020_KuA --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KuA_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kuband_Aarray.py"

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

logprint("Step 1: Preliminary imaging")
for robust in (0, 2):
    if not os.path.exists(f'Kuband_Aarray.center.robust{robust}.continuum.big-coarse.liteclean.psf.tt0'):
        tclean(vis=vis,
               imagename=f'Kuband_Aarray.center.robust{robust}.continuum.big-coarse.liteclean',
               niter=10000, spw=",".join(map(str, contspw)), field='sgr b2b', imsize=[2000],
               cell=['0.05arcsec'], specmode='mfs', deconvolver='mtmfs', weighting='briggs',
               nterms=2,
               robust=robust, parallel=False,
               mask='clean_mask.crtf')






logprint("Step 2: Split the data first to create working copy")
vis_split = []
for vv in vis:
    vs = vv.replace('.ms', '.split.ms')
    vis_split.append(vs)
    if not os.path.exists(vs):
        split(vis=vv,
              outputvis=vs,
              field='sgr b2b',
              datacolumn='corrected')


logprint("Step 4a: Split continuum spws separately and average all channels for better SNR")
vis_contavg = []
for vs in vis_split:
    vca = vs.replace('.ms', '.contavg.ms')
    vis_contavg.append(vca)
    if not os.path.exists(vca):
        # Use mstransform to split continuum spws and average all channels
        from casatasks import mstransform
        mstransform(vis=vs,
                    outputvis=vca,
                    field='sgr b2b',
                    spw=",".join(map(str, contspw)),
                    datacolumn='data',
                    chanaverage=True,
                    chanbin=999999,  # average all channels in each spw
                    combinespws=False)  # keep spws separate for now

logprint("Step 4b: Deep continuum clean for self-calibration on channel-averaged data")

startmodel = ''
for robust in (2, 0):
    imagename = f'Kuband_Aarray.center.robust{robust}.continuum.deepclean'
    if os.path.exists(f'{imagename}.model.tt0'):
        imhist = imhistory(f'{imagename}.model.tt0')
        # Check if any of the vis_contavg MS files are in the history
        has_correct_vis = any(any(vca in x for x in imhist) for vca in vis_contavg)
        if not has_correct_vis:
            vis_entries = [row for row in imhist if row.startswith('vis')]
            if vis_entries:
                logprint(f"Model was created with: {vis_entries[0]}")
            logprint(f"Removing {imagename} files and reimaging")
            for suffix in ('alpha', 'alpha.error', 'image.tt0', 'image.tt1', 'mask', 'model.tt0', 'model.tt1', 'pb.tt0', 'psf.tt0', 'psf.tt1', 'psf.tt2', 'residual.tt0', 'residual.tt1', 'sumwt.tt0','sumwt.tt1', 'sumwt.tt2'):
                if os.path.exists(f'{imagename}.{suffix}'):
                    shutil.rmtree(f'{imagename}.{suffix}')

    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=vis_contavg,
               imagename=imagename,
               niter=100000,
               threshold='0.1mJy',
               spw='',  # use all spws in the averaged MS
               field='sgr b2b',
               imsize=[2000],
               cell=['0.05arcsec'],
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


# Check model column for all vis files
has_model = False
for vca in vis_contavg:
    stats = visstat(vis=vca, datacolumn='model', useflags=False)
    for key in stats:
        # RMS can be scalar or array depending on data shape
        rms = stats[key]['rms']
        if hasattr(rms, '__len__'):
            has_model_ = rms[0] > 0 or rms[1] > 0
        else:
            has_model_ = rms > 0
        logprint(f'MS file {vca}[{key}] {"has model" if has_model_ else "model is zero"}  (rms={stats[key]["rms"]})')
        has_model = (has_model or has_model_)  # ANY spw in ANY MS with model is good enough

if not has_model:
    # populate all model columns for all spws in all MS files
    logprint(f"Model column not properly populated, using ft to populate from {imagename}.model.tt0/tt1")
    for vca in vis_contavg:
        delmod(vca)
        ft(
            vis=vca,
            field='sgr b2b',
            spw='',  # populate all spws
            model=[imagename+'.model.tt0', imagename+'.model.tt1'],
            nterms=2,
            reffreq='',
            usescratch=True,
            incremental=False
        )
    # Verify it worked
    has_model_after = False
    for vca in vis_contavg:
        stats_after = visstat(vis=vca, datacolumn='model', useflags=False)
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
    imagename = f'Kuband_Aarray.center.robust{robust}.continuum.deepclean'
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
# Combine both EBs for better SNR in gaincal
caltable = 'Kuband_Aarray.center.pcal1'
# CRITICAL: Verify model column is populated before running gaincal
# If model is empty, gaincal will corrupt the data!
has_any_model = False
for vca in vis_contavg:
    stats = visstat(vis=vca, datacolumn='model', useflags=False)
    for key in stats:
        rms = stats[key]['rms']
        has_rms = (rms[0] > 0 or rms[1] > 0) if hasattr(rms, '__len__') else (rms > 0)
        if has_rms:
            has_any_model = True
            logprint(f'{vca}[{key}] has model with rms={stats[key]["rms"]}')
if not has_any_model:
    raise RuntimeError("FATAL ERROR: Model column is empty in all MS files! Cannot run gaincal - this would corrupt the data!")
logprint("Model column verified - proceeding with gaincal"
if not os.path.exists(caltable):
    gaincal(vis=vis_contavg,
            caltable=caltable,
            field='sgr b2b',
            solint='inf',
            refant='ea10',
            refantmode='flex',
            minsnr=3.0,
            combine='spw,scan',  # combine across spws and scans for multiple EBs
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

# Apply phase calibration and split to create selfcal MS
vis_selfcal = []
for vv, vs in zip(vis, vis_split):
    vsc = vv.replace('.ms', '.selfcal.ms')
    vis_selfcal.append(vsc)
    if os.path.exists(vsc):
        shutil.rmtree(vsc)
    
    # Map all spws to the combined solution
    # Determine number of SPWs from the MS
    from casatools import msmetadata
    msmd = msmetadata()
    msmd.open(vs)
    nspws = msmd.nspw()
    msmd.close()
    spwmap = [0] * nspws  # map all spws to solution 0
    
    applycal(vis=vs,
             field='sgr b2b',
             gaintable=[caltable],
             interp='linear',
             spwmap=[spwmap],
             applymode='calonly')
    
    split(vis=vs,
          outputvis=vsc,
          field='sgr b2b',
          datacolumn='corrected')

logprint("Step 5: Create channel-averaged continuum MS from selfcal data")
vis_selfcal_contavg = []
for vsc in vis_selfcal:
    vsca = vsc.replace('.ms', '.contavg.ms')
    vis_selfcal_contavg.append(vsca)
    if os.path.exists(vsca):
        shutil.rmtree(vsca)
    
    from casatasks import mstransform
    mstransform(vis=vsc,
                outputvis=vsca,
                field='sgr b2b',
                spw=",".join(map(str, contspw)),
                datacolumn='data',
                chanaverage=True,
                chanbin=999999,  # average all channels in each spw
                combinespws=False)

logprint("Step 6: Reimage continuum with selfcal")
for robust in (0, 2):
    imagename = f'Kuband_Aarray.center.robust{robust}.continuum.deepclean.selfcal'
    if not os.path.exists(f'{imagename}.psf.tt0'):
        tclean(vis=vis_selfcal_contavg,
               imagename=imagename,
               niter=100000,
               threshold='0.1mJy',
               spw='',  # use all spws in the averaged MS
               field='sgr b2b',
               imsize=[2000],
               cell=['0.05arcsec'],
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
    imagename = f'Kuband__Aarray.center.robust{robust}.continuum.deepclean.selfcal'
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

# Convolve model with synthesized beam to create realistic model image
for robust in (0, 2):
    imagename = f'Kuband_Aarray.center.robust{robust}.continuum.deepclean.selfcal'
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









