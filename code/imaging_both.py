# sbatch --job-name=casa_22A-020_KuA --account=astronomy-dept --qos=astronomy-dept-b --nodes=1 --ntasks=16 --mem=256gb --time=96:00:00 --output=/blue/adamginsburg/adamginsburg/logs/VLA-22A-020_sgrb2_KuA_%j.log --wrap "/orange/adamginsburg/casa/casa-6.6.6-17-pipeline-2025.1.0.35-py3.10.el8/bin/casa --pipeline -c /orange/adamginsburg/sgrb2/22A-020/code/imaging_Kuband_Aarray.py"


print(f"CASA log file: {casalog.logfile()}")

# imaging Ku-band A-array (both EBs combined)
import os
import shutil
os.chdir('/orange/adamginsburg/sgrb2/22A-020/imaging_Aarray')
vis = ['../22A-020.sb41257746.eb41788351.59700.31502699074/22A-020.sb41257746.eb41788351.59700.31502699074.ms',
       '../22A-020.sb41257746.eb41789929.59703.295863067135/22A-020.sb41257746.eb41789929.59703.295863067135.ms']

contspw = [8, 9, 10, 11, 12, 13, 14, 15, 31, 32, 33, 34, 35, 36, 37, 38]

# Step 1: Preliminary imaging
for robust in (0, 2):
    if not os.path.exists(f'KubandAarray.center.robust{robust}.continuum.big-coarse.liteclean.psf.tt0'):
        tclean(vis=vis,
               imagename=f'KubandAarray.center.robust{robust}.continuum.big-coarse.liteclean',
               niter=10000, spw=",".join(map(str, contspw)), field='sgr b2b', imsize=[2000],
               cell=['0.05arcsec'], specmode='mfs', deconvolver='mtmfs', weighting='briggs',
               nterms=2,
               robust=robust, parallel=False,
               mask='clean_mask.crtf')

for spw in (range(42,0,-1)):
    if not os.path.exists(f'KubandAarray.sgrb2n.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KubandAarray.sgrb2n.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m19.87 -28d22m18.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)
    if not os.path.exists(f'KubandAarray.sgrb2m.spw{spw}.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KubandAarray.sgrb2m.spw{spw}.liteclean',
               phasecenter='ICRS 17h47m20.16 -28d23m04.5',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[1000],
               cell=['0.02arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)


for spw in (16, 30, 39):
    if not os.path.exists(f'KubandAarray.center.spw{spw}.big-coarse.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KubandAarray.center.spw{spw}.big-coarse.liteclean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)

for spw in (30,31):
    if not os.path.exists(f'KubandAarray.center.robust2.spw{spw}.big-coarse.liteclean.psf'):
        tclean(vis=vis,
               imagename=f'KubandAarray.center.robust2.spw{spw}.big-coarse.liteclean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=False)


for spw in (16, 30, 39):
    if not os.path.exists(f'KubandAarray.center.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=vis,
               imagename=f'KubandAarray.center.spw{spw}.big-coarse.clean',
               niter=1000, spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=0.5, parallel=False)

for spw in (30,31):
    if not os.path.exists(f'KubandAarray.center.robust2.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=vis,
               imagename=f'KubandAarray.center.robust2.spw{spw}.big-coarse.clean',
               niter=1000000, threshold='10mJy', spw=str(spw), field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=False)

for vv in vis:
    if not os.path.exists(vv.replace(".ms", "_spw30_NaCl.split")):
        split(vis=vv, outputvis=vv.replace(".ms", "_spw30_NaCl.split"),
              width=8, field='sgr b2b', spw='30')
for spw in (30,):
    if not os.path.exists(f'KubandAarray.center.robust2.downsample.spw{spw}.big-coarse.clean.psf'):
        tclean(vis=[vv.replace(".ms", "_spw30_NaCl.split") for vv in vis],
               imagename=f'KubandAarray.center.robust2.downsample.spw{spw}.big-coarse.clean',
               niter=2000000, threshold='10mJy', field='sgr b2b', imsize=[2000],
               cell=['0.1arcsec'], specmode='cube', weighting='briggs',
               robust=2, parallel=False)

# Step 2: Split the data first to create working copy
vis_split = []
for vv in vis:
    vs = vv.replace('.ms', '.split.ms')
    vis_split.append(vs)
    if not os.path.exists(vs):
        split(vis=vv,
              outputvis=vs,
              field='sgr b2b',
              datacolumn='corrected')

# Step 3: Non-selfcal imaging of NaCl line spws BEFORE deep cleaning/selfcal
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
    imagename = f'KubandAarray.center.spw30.robust{robust}.contsub.noselfcal.clean'
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
    contmodel = f'KubandAarray.center.robust{robust}.continuum.big-coarse.liteclean.model.tt0',
    imagename = f'KubandAarray.center.spw30.robust{robust}.withcont.noselfcal.clean'
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

# Step 4a: Split continuum spws separately and average all channels for better SNR
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

# Step 4b: Deep continuum clean for self-calibration on channel-averaged data

startmodel = ''
for robust in (2, 0):
    imagename = f'KubandAarray.center.robust{robust}.continuum.deepclean'
    if os.path.exists(f'{imagename}.model.tt0'):
        imhist = imhistory(f'{imagename}.model.tt0')
        # Check if any of the vis_contavg MS files are in the history
        has_correct_vis = any(any(vca in x for x in imhist) for vca in vis_contavg)
        if not has_correct_vis:
            vis_entries = [row for row in imhist if row.startswith('vis')]
            if vis_entries:
                print(f"Model was created with: {vis_entries[0]}")
            print(f"Removing {imagename} files and reimaging")
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
        print(f'MS file {vca}[{key}] {"has model" if has_model_ else "model is zero"}  (rms={stats[key]["rms"]})', flush=True)
        has_model = (has_model or has_model_)  # ANY spw in ANY MS with model is good enough

if not has_model:
    # populate all model columns for all spws in all MS files
    print(f"Model column not properly populated, using ft to populate from {imagename}.model.tt0/tt1", flush=True)
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
    imagename = f'KubandAarray.center.robust{robust}.continuum.deepclean'
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

# Step 5: Self-calibration on channel-averaged continuum
# Combine both EBs for better SNR in gaincal
caltable = 'KubandAarray.center.pcal1'
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
            print(f'{vca}[{key}] has model with rms={stats[key]["rms"]}', flush=True)
if not has_any_model:
    raise RuntimeError("FATAL ERROR: Model column is empty in all MS files! Cannot run gaincal - this would corrupt the data!")
print("\u2713 Model column verified - proceeding with gaincal", flush=True)
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

# Step 6: Selfcal imaging of NaCl line spws AFTER selfcal
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
    imagename = f'KubandAarray.center.spw30.robust{robust}.contsub.selfcal.clean'
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
    contmodel = f'KubandAarray.center.robust{robust}.continuum.deepclean.model.tt0'
    imagename = f'KubandAarray.center.spw30.robust{robust}.withcont.selfcal.clean'
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

# Step 7a: Create channel-averaged continuum MS from selfcal data
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

# Step 7b: Reimage continuum with selfcal
for robust in (0, 2):
    imagename = f'KubandAarray.center.robust{robust}.continuum.deepclean.selfcal'
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
    imagename = f'KubandAarray.center.robust{robust}.continuum.deepclean.selfcal'
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









