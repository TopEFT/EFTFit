import os
import sys
import logging
import datetime
import shutil

import ROOT

import EFTFit.Fitter.consts as CONST

from CombineHarvester.TopEFT.DatacardMaker import DatacardMaker
from EFTFit.Fitter.DatacardReader import DatacardReader
from EFTFit.Fitter.LvlFormatter import LvlFormatter
from EFTFit.Fitter.utils import regex_match
from EFTFit.Fitter.CombineHelper import *

sys.path.append(os.path.join(CONST.EFTFIT_DIR,'scripts'))
from EFTFitter import EFTFit
sys.path.append(os.path.join(CONST.COMBINE_DIR,'TopEFT/scripts'))
from CombineLepFlavors import CombineLepFlavors

# To build the TH1EFT shared library do: root -l TH1EFT.h+

# Note:
#   This code makes heavy use of code defined in the 'cms-govner/TopEFT' git repo and so may break
#   if code there changes

TSTAMP1 = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
TSTAMP2 = datetime.datetime.now().strftime('%Y-%m-%d')

frmt = LvlFormatter()
logging.getLogger().setLevel(logging.DEBUG)

# Configure logging to also output to stdout
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(frmt)
logging.getLogger('').addHandler(console)

# Needs a lot of work
class HelperMode(object):
    SM_FITTING = 'SM_fitting'
    SM_IMPACTS = 'SM_impacts'
    SM_PREFIT  = 'SM_prefitOnly'
    EFT_FITTING = 'EFT_fitting'
    EFT_IMPACTS = 'EFT_impacts'

# Configure logging to an output file
def setup_logger(log_file):
    outlog = logging.FileHandler(filename=log_file,mode='w')
    outlog.setLevel(logging.DEBUG)
    outlog.setFormatter(frmt)
    logging.getLogger('').addHandler(outlog)

    logging.info("Log file: %s",log_file)

def individual_impact_plots(helper,pois,rm_systs):
    orig_card = helper.ops.getOption('original_card')
    helper.setOptions(datacard_file=orig_card)
    helper.loadDatacard(force=True)
    helper.modifyDatacard("mod_datacard.txt",remove_systs=rm_systs)
    helper.make_workspace()

    frz_lst = [x for x in helper.dc_maker.getOperators() if x not in pois]
    helper.runCombine(
        method=CombineMethod.IMPACTS,
        redefine_pois=pois,
        freeze_parameters=frz_lst
    )

def make_impacts_from_tony_inputs():
    tony_dir = '/afs/crc.nd.edu/user/a/alefeld/Public/ForAndrew'
    # No longer exist in the directory
    # a24_private = 'EFT_MultiDim_Datacard_24_Private_FixMerge.txt'
    # a24_central = 'EFT_MultiDim_Datacard_24_Central_FixMerge.txt'
    # a24_histograms = 'anatest24_MergeLepFl.root'
    # a25_private = 'EFT_MultiDim_Datacard_25_Private.txt'
    # a25_central = 'EFT_MultiDim_Datacard_25_Central.txt'
    # a25_histograms = 'anatest25_MergeLepFl.root'

    a28_private = 'EFT_MultiDim_Datacard_28_Private.txt'
    a28_central = 'EFT_MultiDim_Datacard_28_Central.txt'
    a28_private_asimov = 'EFT_MultiDim_Datacard_28_Private_Asimov.txt'
    a28_central_asimov = 'EFT_MultiDim_Datacard_28_Central_Asimov.txt'
    a28_histograms = 'anatest28_MergeLepFl.root'

    datacard = a28_central_asimov

    copy_output = True
    is_asimov = True
    testing = False

    ana_ver = 'ana28'
    sample_source = 'central'
    suffix = 'cminDefaultMinimizerStategy-0'

    dir_ver = 'fromTony'
    out_name = 'SM_impacts_{tstamp}_{ana_ver}_{source}'.format(ana_ver=ana_ver,source=sample_source,tstamp=TSTAMP1)
    if is_asimov:
        out_name += '_Asimov'
    if len(suffix):
        out_name += '_' + suffix

    if testing:
        # Produce the output in the test directory (will be cleaned up over each running)
        copy_output = False
        out_name = 'test'
    out_log = 'out.log'
    out_dir  = os.path.join(dir_ver,out_name)

    helper = CombineHelper(os.getcwd(),out_dir=out_dir)


    ## Configure logging to an output file
    log_file = os.path.join(helper.output_dir,out_log)
    outlog = logging.FileHandler(filename=log_file,mode='w')
    outlog.setLevel(logging.DEBUG)
    outlog.setFormatter(frmt)
    logging.getLogger('').addHandler(outlog)

    if testing:
        helper.cleanDirectory(helper.output_dir,keep=["^out.log$"])

    logging.info("Making impacts from tony inputs...")
    logging.info("Log file: {}".format(log_file))
    logging.info("datacard: {}".format(datacard))

    # Use Tony's class to generate the workspace file
    fitter = EFTFit()
    fitter.makeWorkspaceSM(datacard=os.path.join(tony_dir,datacard))

    ws_file = 'SMWorkspace.root'
    dst = os.path.join(helper.output_dir,ws_file)
    logging.info('Copying {file} to {dst}'.format(file=ws_file,dst=dst))
    shutil.copy(ws_file,dst)

    helper.setOptions(
        ws_file=ws_file,    # Needs to be relative to the output directory
        ws_type=WorkspaceType.SM
    ) 
    helper.setOptions(extend=True,other_options=[
        '--cminDefaultMinimizerStrategy=0',
        # '--autoMaxPOIs=*',
        # '--setRobustFitTolerance=0.5',
        # '--cminDefaultMinimizerTolerance=0.01',
    ])
    # helper.setOptions(extend=True,other_options=['--autoMaxPOIs=*'])
    # helper.setOptions(extend=True,other_options=['--cminPoiOnlyFit'])
    # helper.setOptions(extend=True,other_options=['--floatOtherPOIs=1']) # Can't be used as this is automatically set by combineTools in the '--doFits' stage


    # helper.setOptions(extend=True,other_options=['--setParameterRanges',range_str])
    pois = [
        'mu_ttll',
        'mu_ttH',
        'mu_ttlnu',
        'mu_tllq'
    ]
    helper.dc_maker.setOperators(pois)

    logging.info("Making impacts for all POIs: {}".format(pois))
    helper.runCombine(method=CombineMethod.IMPACTS,robust_fit=False)
    # helper.runCombine(method=CombineMethod.FITDIAGNOSTIC,name='Prefit',minos_arg='all')

    #for poi in pois:
    #    logging.info("Making impacts for poi {poi}".format(poi=poi))
    #    frz_lst = [x for x in pois if x != poi]
    #    helper.runCombine(
    #        method=CombineMethod.IMPACTS,
    #        redefine_pois=[poi],
    #        freeze_parameters=[],#frz_lst,
    #        robust_fit=False
    #    )
    if copy_output:
        copy_dir = os.path.join(CONST.USER_DIR,'www/eft_stuff/misc/impact_plots',out_dir)
        helper.copyOutput(copy_dir,rgx_list=["^impacts_.*pdf$"],clean_directory=False)

    logging.info('Logger shutting down!')
    logging.shutdown()

def runit(group_directory,dir_name,hist_file,mode,testing=False,force=False,copy_output=False):
    # For producing fits with the EFT WCs as the POIs
    EFT_OPS = HelperOptions(
        ws_file      = '16D.root',
        model        = 'EFTFit.Fitter.EFTModel:eft16D',
        ws_type      = WorkspaceType.EFT,
        prefit_value = 0.0,
        algo         = FitAlgo.SINGLES
    )

    # For producing fits with SM signal strength as the POIs
    SM_SIGNAL_OPS = HelperOptions(
        ws_file      = 'SMWorkspace.root',
        model        = 'HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel',
        ws_type      = WorkspaceType.SM,
        sm_signals = [# Overwrites the poi_ranges setting if len(tup[2]) == 3
            # ('ttH',  'mu_ttH',  [1,0,30]),
            # ('tllq', 'mu_tllq', [1,0,30]),
            # ('ttll', 'mu_ttll', [1,0,30]),
            # ('ttlnu','mu_ttlnu',[1,0,30]),
            # ('tHq',  'mu_ttH',  [1,0,30]),  # Ties tHq process to be scaled by ttH signal

            ('ttH',  'mu_ttH',  [1]),
            ('tllq', 'mu_tllq', [1]),
            ('ttll', 'mu_ttll', [1]),
            ('ttlnu','mu_ttlnu',[1]),
            ('tHq',  'mu_ttH',  [1]),  # Ties tHq process to be scaled by ttH signal
        ],
        prefit_value = 1.0,
        algo         = FitAlgo.SINGLES
    )

    out_name = '{mode}_{tstamp}_{name}'.format(mode=mode,tstamp=TSTAMP2,name=dir_name)
    if testing:
        out_name = '{mode}_testing'.format(mode=mode)

    # Should be relative to the CombineHelper 'home' directory
    out_dir = os.path.join(group_directory,out_name)

    if mode == HelperMode.SM_FITTING or mode == HelperMode.SM_IMPACTS or mode == HelperMode.SM_PREFIT:
        helper_ops = HelperOptions(**SM_SIGNAL_OPS.getCopy())
    elif mode == HelperMode.EFT_FITTING or mode == HelperMode.EFT_IMPACTS:
        helper_ops = HelperOptions(**EFT_OPS.getCopy())
    else:
        raise RuntimeError("Unknown run mode: {}".format(mode))
    helper_ops.setOptions(
        verbosity=3,
        fake_data=True,
        save_fitresult=True,
        use_central=False,
        use_poi_ranges=False,
        histogram_file=hist_file
    )
    # Other options
    helper_ops.setOptions(extend=True,other_options=[
        '--cminDefaultMinimizerStrategy=1',
        # '--cminPoiOnlyFit',
        # '--autoMaxPOIs=*'
        '--robustHesse=1',
    ])

    test_dir = os.path.expandvars('${CMSSW_BASE}/src/EFTFit/Fitter/test')

    helper = CombineHelper(home=test_dir,out_dir=out_dir)
    helper.setOptions(preset=helper_ops)

    # Needs to come after the helper is insantiated, b/c of the logger in the helper
    setup_logger(os.path.join(helper.output_dir,'out.log'))

    logging.info('group_directory: {}'.format(group_directory))
    logging.info('dir_name: {}'.format(dir_name))
    logging.info('hist_file: {}'.format(hist_file))
    logging.info('mode: {}'.format(mode))
    logging.info('testing: {}'.format(testing))
    logging.info('force: {}'.format(force))
    logging.info('copy_output: {}'.format(copy_output))

    # helper.make_datacard()
    # return

    to_keep = ["^EFT_MultiDim_Datacard.txt","^16D.root","^SMWorkspace.root","^out.log$"]
    helper.cleanDirectory(helper.output_dir,keep=to_keep)
    if force:
        helper.make_datacard()
        helper.make_workspace()
    else:
        if not helper.hasDatacard():
            helper.make_datacard()
        if not helper.hasWorkspace():
            helper.make_workspace()
    helper.loadDatacard(force=True)

    pois = helper.getPOIs()

    if mode == HelperMode.EFT_FITTING:
        other_ops = []
        # other_ops.extend(['--trackParameters',','.join([poi for poi in pois])])
        helper.setOptions(extend=True,other_options=other_ops)

    # Come from the AN for SM signal fits
    nom_sm_pois = {}
    nom_sm_pois["mu_ttll"]  = 1.06
    nom_sm_pois["mu_ttlnu"] = 0.79
    nom_sm_pois["mu_ttH"]   = 2.50
    nom_sm_pois["mu_tllq"]  = 1.11

    # Come from the AN for SM signal fits
    hi_sm_pois = {}
    hi_sm_pois["mu_ttll"]  = 1.06 + 0.25
    hi_sm_pois["mu_ttlnu"] = 0.79 + 0.37
    hi_sm_pois["mu_ttH"]   = 2.50 + 0.85
    hi_sm_pois["mu_tllq"]  = 1.11 + 0.57

    # Come from the AN for SM signal fits
    lo_sm_pois = {}
    lo_sm_pois["mu_ttll"]  = 1.06 - 0.19
    lo_sm_pois["mu_ttlnu"] = 0.79 - 0.32
    lo_sm_pois["mu_ttH"]   = 2.50 - 0.70
    lo_sm_pois["mu_tllq"]  = 1.11 - 0.54

    # Come from Brent's 1D grid scans (other WCs floating)
    nom_eft_pois = {}
    nom_eft_pois["ctW"]   = -0.62 #-0.860
    nom_eft_pois["ctZ"]   = -0.68 #-0.957
    # nom_eft_pois["ctp"]   = -7.852 # From other scans (i.e. profiled)
    nom_eft_pois["ctp"]   = 25.50 #26.167 # From dedicated 1D scan
    nom_eft_pois["cpQM"]  = -1.07 #0.000
    nom_eft_pois["ctG"]   = -0.85 #-0.750
    nom_eft_pois["cbW"]   =  3.17 #2.633
    nom_eft_pois["cpQ3"]  = -1.60 #-1.280
    nom_eft_pois["cptb"]  =  0.13 #0.133
    nom_eft_pois["cpt"]   = -3.48 #-2.083
    nom_eft_pois["cQl3i"] = -4.20 #-4.200
    nom_eft_pois["cQlMi"] =  0.51 #0.510
    nom_eft_pois["cQei"]  =  0.05 #0.053
    nom_eft_pois["ctli"]  =  0.27 #0.200
    nom_eft_pois["ctei"]  =  0.29 #0.333
    nom_eft_pois["ctlSi"] =  0.00 #-0.073
    nom_eft_pois["ctlTi"] =  0.00 #-0.013

    # Come from the AN (other WCs floating)
    hi_eft_pois = {}
    hi_eft_pois["ctW"]   =  2.79 #2.74;
    hi_eft_pois["ctZ"]   =  3.14 #3.16;
    hi_eft_pois["ctp"]   = 44.51 #44.68;
    hi_eft_pois["cpQM"]  = 21.26 #21.72;
    hi_eft_pois["ctG"]   =  1.18 #1.16;
    hi_eft_pois["cbW"]   =  4.98 #4.78;
    hi_eft_pois["cpQ3"]  =  3.43 #3.54;
    hi_eft_pois["cptb"]  = 12.49 #12.68;
    hi_eft_pois["cpt"]   = 12.37 #12.52;
    hi_eft_pois["cQl3i"] =  9.04 #8.44;
    hi_eft_pois["cQlMi"] =  4.87 #4.90;
    hi_eft_pois["cQei"]  =  4.48 #4.34;
    hi_eft_pois["ctli"]  =  4.71 #4.70;
    hi_eft_pois["ctei"]  =  4.74 #4.72;
    hi_eft_pois["ctlSi"] =  6.31 #6.37;
    hi_eft_pois["ctlTi"] =  0.81 #0.82;

    # Come from the AN (other WCs floating)
    lo_eft_pois = {}
    lo_eft_pois["ctW"]   =  -2.98 #-2.96;
    lo_eft_pois["ctZ"]   =  -3.31 #-3.33;
    lo_eft_pois["ctp"]   = -17.09 #-16.87;
    lo_eft_pois["cpQM"]  =  -7.65 #-7.81;
    lo_eft_pois["ctG"]   =  -1.39 #-1.37;
    lo_eft_pois["cbW"]   =  -4.96 #-4.77;
    lo_eft_pois["cpQ3"]  =  -7.36 #-7.00;
    lo_eft_pois["cptb"]  = -12.58 #-12.77;
    lo_eft_pois["cpt"]   = -18.89 #-18.60;
    lo_eft_pois["cQl3i"] =  -9.66 #-9.16;
    lo_eft_pois["cQlMi"] =  -3.90 #-3.77;
    lo_eft_pois["cQei"]  =  -4.27 #-4.28;
    lo_eft_pois["ctli"]  =  -4.17 #-4.10;
    lo_eft_pois["ctei"]  =  -4.11 #-4.11;
    lo_eft_pois["ctlSi"] =  -6.31 #-6.37;
    lo_eft_pois["ctlTi"] =  -0.81 #-0.82;



    ## To make fitresult objects for pre/postfit yields
    if mode == HelperMode.SM_FITTING or mode == HelperMode.EFT_FITTING:
        frz_nom_pois  = []
        frz_up_pois   = []
        frz_down_pois = []
        frz_sm_pois   = []
        if mode == HelperMode.EFT_FITTING:
            frz_nom_pois  = ["{poi}={val}".format(poi=k,val=v) for k,v in nom_eft_pois.iteritems()]
            frz_up_pois   = ["{poi}={val}".format(poi=k,val=v) for k,v in hi_eft_pois.iteritems()]
            frz_down_pois = ["{poi}={val}".format(poi=k,val=v) for k,v in lo_eft_pois.iteritems()]
            frz_sm_pois   = ["{poi}=0.0".format(poi=k) for k in pois]
        elif mode == HelperMode.SM_FITTING:
            frz_nom_pois  = ["{poi}={val}".format(poi=k,val=v) for k,v in nom_sm_pois.iteritems()]
            frz_up_pois   = ["{poi}={val}".format(poi=k,val=v) for k,v in hi_sm_pois.iteritems()]
            frz_down_pois = ["{poi}={val}".format(poi=k,val=v) for k,v in lo_sm_pois.iteritems()]
            frz_sm_pois   = ["{poi}=1.0".format(poi=k) for k in pois]
        helper.runCombine(method=CombineMethod.FITDIAGNOSTIC,name='Prefit',minos_arg='all')
        helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Postfit')
        helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Bestfit',  # Start from Brent's best fit point
            parameter_values=frz_nom_pois,
            algo=FitAlgo.NONE
        )
        helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='FreezeNom',
            parameter_values=frz_nom_pois,
            freeze_parameters=pois
        )
        helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='FreezeUp',
            parameter_values=frz_up_pois,
            freeze_parameters=pois
        )
        helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='FreezeDown',
            parameter_values=frz_down_pois,
            freeze_parameters=pois
        )
        helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='NuisOnly',
            parameter_values=frz_sm_pois,
            freeze_parameters=pois
        )
        # Just to make workspace_testing.C happy, not needed for overlay_operator_variations.C
        # helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Stats',freeze_parameters=[])
    # if mode == HelperMode.SM_FITTING:
    #     bestfit_SM_pois  = ["{poi}={val}".format(poi=k,val=v) for k,v in nom_SM_pois.iteritems()]
    #     helper.runCombine(method=CombineMethod.FITDIAGNOSTIC,name='Prefit',minos_arg='all')
    #     helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Postfit',parameter_values=bestfit_SM_pois)

    # Skips finding the impacts for these nuisances
    to_exclude = []
    to_exclude.extend(helper.getSysts(['FR_stats_.*','^QCDscale_VVV$','[lh]fstats[12]']))

    if mode == HelperMode.SM_IMPACTS:
        # Note: Not sure this is correct thing to do here...
        # to_remove = [
        #     CombineSystematic(syst_name='pdf_ggttH',procs=['ttH'] ,bins=['.*']),
        #     CombineSystematic(syst_name='pdf_gg'   ,procs=['ttll'],bins=['.*']),
        #     CombineSystematic(syst_name='pdf_qgtHq',procs=['tHq'] ,bins=['.*']),
        #     CombineSystematic(syst_name='pdf_qq',procs=['ttlnu','tllq'],bins=['.*']),
        #     CombineSystematic(syst_name='QCDscale_ttH',procs=['ttH'] ,bins=['.*']),
        #     CombineSystematic(syst_name='QCDscale_V'  ,procs=['tllq'],bins=['.*']),
        #     CombineSystematic(syst_name='QCDscale_tHq',procs=['tHq'] ,bins=['.*']),
        #     CombineSystematic(syst_name='QCDscale_ttbar',procs=['ttll','ttlnu'],bins=['.*'])
        # ]
        # helper.modifyDatacard("mod_datacard.txt",remove_systs=to_remove)
        # helper.make_workspace()
        # helper.loadDatacard(force=True)
        # Note: If we don't set a POI range the '--doInitialFit' portion freaks out
        #       when trying to perform the robust fit
        for poi in pois: helper.setPOIRange(poi,0,30)
        param_values = []
        if not helper.ops.getOption('fake_data'):
            param_values = bestfit_SM_pois
        helper.runCombine(method=CombineMethod.IMPACTS,
            robust_fit=True,
            use_poi_ranges=True,
            parameter_values=param_values,
            exclude_nuisances=to_exclude,
        )
    if mode == HelperMode.EFT_IMPACTS:
        frz_nom_pois  = ["{poi}={val}".format(poi=k,val=v) for k,v in nom_eft_pois.iteritems()]
        for poi in pois:
            lo = 1.5*lo_eft_pois[poi]
            hi = 1.5*hi_eft_pois[poi]
            helper.setPOIRange(poi,lo,hi)
        param_values = []
        if not helper.ops.getOption('fake_data'):
            param_values = frz_nom_pois
        helper.runCombine(method=CombineMethod.IMPACTS,
            robust_fit=True,        # Note: Setting this to True makes the impacts take a VERY VERY long time to run
            use_poi_ranges=False,
            parameter_values=param_values,
            exclude_nuisances=to_exclude,
        )

    helper.chdir(helper.home_dir)

    if copy_output:
        if mode == HelperMode.SM_IMPACTS or mode == HelperMode.EFT_IMPACTS:
            dst_dir = os.path.join(CONST.WEB_DIR,'eft_stuff/misc/impact_plots',out_dir)
            helper.copyOutput(dst_dir,rgx_list=["^impacts_.*pdf$"],clean_directory=False)

    logging.info('Logger shutting down!')
    logging.shutdown()

# Kept around for posterity and reference, despite being called 'main' this code shouldn't ever get run
def main():
    EFT_OPS = HelperOptions(
        ws_file      = '16D.root',
        model        = 'EFTFit.Fitter.EFTModel:eft16D',
        ws_type      = WorkspaceType.EFT,
        prefit_value = 0.0
    )

    # NOTE: Tony changed the HistogramProcessor to replace tZq --> tllq, ttW --> ttlnu, and ttZ --> ttll
    sm_central = [
        ('ttH',  'mu_ttH',  [1,0,30]),
        ('tllq', 'mu_tllq', [1,0,30]),
        ('ttll', 'mu_ttll', [1,0,30]),
        ('ttlnu','mu_ttlnu',[1,0,30]),
        ('tHq',  'mu_ttH',  [1,0,30]),  # Ties tHq process to be scaled by ttH signal
    ]

    SM_SIGNAL_OPS = HelperOptions(
        ws_file      = 'SMWorkspace.root',
        model        = 'HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel',
        ws_type      = WorkspaceType.SM,
        # sm_signals   = [x for x in sm_central],
        sm_signals = [
            ('ttH',  'mu_ttH',  [1,0,30]),
            ('tllq', 'mu_tllq', [1,0,30]),
            ('ttll', 'mu_ttll', [1,0,30]),
            ('ttlnu','mu_ttlnu',[1,0,30]),
            ('tHq',  'mu_ttH',  [1,0,30]),  # Ties tHq process to be scaled by ttH signal
        ],
        prefit_value = 1.0,
        algo         = FitAlgo.SINGLES
    )

    use_fake_data   = False
    modify_datacard = True
    copy_output     = False

    # Remove certain bin categories from the datacard
    keep_bins = []
    # keep_bins = ['^C_2lss_.*']
    # keep_bins = ['^C_3l_.*','^C_4l_.*']

    # NOTE: The ws_type controls whether we make a SM workspace or an EFT one, this is specified
    #       in the template options above
    helper_ops = HelperOptions(**SM_SIGNAL_OPS.getCopy())
    helper_ops.setOptions(verbosity=2,fake_data=use_fake_data,save_fitresult=True)
    helper_ops.setOptions(use_central=False)

    if helper_ops.getOption('ws_type') == WorkspaceType.EFT and not use_fake_data:
        print "ERROR: Not allowed to look at real data for the EFT fit yet!"
        raise RuntimeError

    sample_source = 'private' if helper_ops.getOption('use_central') else 'central'

    out_log = 'out.log'
    if not use_fake_data:
        # dir_ver,hist_file = ('data2017v1','TOP-19-001_unblinded_v1.root')   # Needs to have PSISR systematics added in 'by hand' in DatacardMaker
        # dir_ver,hist_file = ('data2017v1','anatest16.root')                 # These are the central samples (don't need to add in PSISR)
        # dir_ver,hist_file = ('data2017v1','anatest17.root')                 # Private samples with first attempt at including ad-hoc jet systematics (probably never use)
        # dir_ver,hist_file = ('data2017v1','anatest18.root')                 # Updated version of anatest17 with fixed SFs for the ad-hoc jet systematics
        # dir_ver,hist_file = ('data2017v1','anatest19.root')                 # Private samples with noSFs, but rougher njet binning (the changes to DatacardMaker are not backwards compatible)
        # dir_ver,hist_file = ('data2017v1','anatest20.root')                 # Private samples with new SFs/Normalizations, uses full njet bins (not compatible with anatest19)
        # dir_ver,hist_file = ('data2017v1','anatest22.root')                 # Both Private and Central samples which include multiple fixes since first unblinding (e.g. remove higgs from tllq, code bugs, etc.)
        dir_ver,hist_file = ('data2017v1','anatest23_v3.root')              # post-Geoff histograms, replaced the private tllq4f matched sample with tllq4f-tch+jets
        # dir_ver,hist_file = ('data2017v1','anatest24.root')                 # tllq4f no longer has intermediate higgs and fixes JEC AK4PFchs issue
        # dir_ver,hist_file = ('data2017v1','anatest25.root')                 # Fixed muR/muF and PDF systematics
        # out_name = 'SM_impacts_testing'
        # out_name = 'SM_fitting_{tstamp}_ana23v3_private_cminDefaultMinimizerStrategy-0'.format(tstamp=TSTAMP1)
        out_name = 'SM_fitting_{tstamp}_ana23v3_private_test'.format(tstamp=TSTAMP1)
        out_dir  = os.path.join(dir_ver,out_name)       # This path is relative to EFTFIT_TEST_DIR
    else:
        # out_dir = 'ana12_Jan18btagReqs/1DctZ_AllSysts_impacts_SMdata'
        # out_dir = 'ana12_Jan18btagReqs/16D_AllSysts_SMdata'
        # out_dir = 'ana12_Jan18btagReqs/3D_tonyfit_SMdata'
        # out_dir = 'ana12_Jan18btagReqs/16D_tonyfit_SMdata'
        # out_dir = 'ana14/16D_tonyfit_SMdata'
        # out_dir = 'ana14/SM_impacts_RemovedSignalNorm'
        # out_dir = 'ana14/SM_impacts_RemovedSignalNorm_FreezeOthers'
        # out_dir = 'ana14/SM_impacts_AsimovSMdata'
        # out_dir = 'ana14/SM_testing_AsimovSMdata'
        # out_dir = 'ana14/3D_tonyfit_NonSMdata'
        dir_ver,hist_file  = ('ana22','anatest22.root')
        # out_name = 'SM_fitting_testing'
        # out_name = 'SM_fitting_%s' % (TSTAMP1)
        out_name = 'SM_impacts_test-{tstamp}'.format(tstamp=TSTAMP1)
        out_dir  = os.path.join(dir_ver,out_name)       # This path is relative to EFTFIT_TEST_DIR
    copy_dir = os.path.join(CONST.USER_DIR,'www/eft_stuff/misc/impact_plots',out_dir)
    helper = CombineHelper(os.getcwd(),out_dir=out_dir,preset=helper_ops)
    helper.setOptions(histogram_file=hist_file)
    # helper.setOptions(robust_fit=True)
    # helper.setOptions(auto_bounds_pois=["*"])
    helper.setOptions(extend=True,other_options=['--cminDefaultMinimizerStrategy=0'])
    # helper.setOptions(freeze_parameters=['mu_tllq'])
    # helper.setOptions(redefine_pois=['mu_ttH','mu_ttlnu','mu_ttll'])

    ## This is when using the Central Samples, as the histograms are named differently --> Shouldn't be needed anymore since Tony's update to HistogramProcessor
    # helper.dc_maker.hp.sgnl_known     = [ x[0] for x in sm_central]
    # helper.dc_maker.hp.sgnl_histnames = [ x[0] for x in sm_central]

    ## This is now needed after Tony's update to HistogramProcessor for the 'TOP-19-001_unblind' histograms
    # helper.dc_maker.hp.sgnl_histnames = [x[0] + '_16D' for x in sm_signals]

    ## For central samples in anatest16
    # helper.dc_maker.hp.sgnl_histnames = ['ttH','tllq','ttll','ttlnu','tHq']
    # helper.dc_maker.hp.sgnl_histnames = ['ttH','tllq','ttll','ttlnu']

    # Note: starting with anatest22, both private and central samples are in the same anatest file

    log_file = os.path.join(helper.output_dir,out_log)

    ## Configure logging to an output file
    outlog = logging.FileHandler(filename=log_file,mode='w')
    outlog.setLevel(logging.DEBUG)
    outlog.setFormatter(frmt)
    logging.getLogger('').addHandler(outlog)

    logging.info("Log file: %s",log_file)

    if helper.ops.getOption('ws_type') == WorkspaceType.EFT:
        wc_lst = []
        # wc_lst += ['cbW','ctW','cpQ3']
        # wc_lst += ['ctp','cpQM','ctW','ctZ','ctG','cbW','cpQ3','cptb','cpt']   # 2-Heavy Operators
        # wc_lst += ['cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']       # 4-Fermi Operators
        if use_fake_data:
            rwgt_pt = {}
            for wc in wc_lst: rwgt_pt[wc] = 0
            helper.dc_maker.setOperators(wc_lst)
            helper.dc_maker.setReweightPoint(rwgt_pt)
        for wc in wc_lst: helper.setPOIRange(wc,-20.0,20.0)

    rm_systs = {}
    rm_systs['pdf_ggttH'] = CombineSystematic(syst_name='pdf_ggttH',procs=['ttH'] ,bins=['.*'])
    rm_systs['pdf_gg']    = CombineSystematic(syst_name='pdf_gg'   ,procs=['ttll'],bins=['.*'])
    rm_systs['pdf_qgtHq'] = CombineSystematic(syst_name='pdf_qgtHq',procs=['tHq'] ,bins=['.*'])
    rm_systs['pdf_qq']    = CombineSystematic(syst_name='pdf_qq',procs=['ttlnu','tllq'],bins=['.*'])

    rm_systs['QCDscale_ttH']   = CombineSystematic(syst_name='QCDscale_ttH',procs=['ttH'] ,bins=['.*'])
    rm_systs['QCDscale_V']     = CombineSystematic(syst_name='QCDscale_V'  ,procs=['tllq'],bins=['.*'])
    rm_systs['QCDscale_tHq']   = CombineSystematic(syst_name='QCDscale_tHq',procs=['tHq'] ,bins=['.*'])
    rm_systs['QCDscale_ttbar'] = CombineSystematic(syst_name='QCDscale_ttbar',procs=['ttll','ttlnu'],bins=['.*'])

    # rm_systs['PSISR'] = CombineSystematic(syst_name='PSISR',procs=['.*'],bins=['.*'])   # This is b/c starting with anatest16 the PSISR are properly
                                                                                          # included in the histograms, so we get a duplicate nuisance parameter

    ## Just add/remove them all for now
    to_add    = [] # Don't add any systematics 
    to_remove = []#[v for k,v in rm_systs.iteritems()]

    helper.cleanDirectory(helper.output_dir,keep=["^EFT_MultiDim_Datacard.txt","^16D.root","^SMWorkspace.root","^out.log$"])

    helper.make_datacard()
    if modify_datacard:
        helper.modifyDatacard("mod_datacard.txt",
            remove_systs=to_remove,
            add_systs=to_add,
            filter_bins=keep_bins
        )
    helper.make_workspace()
    helper.loadDatacard(force=True)

    ## We use list comprehensions here to ensure we don't accidentally modify a helper option 
    frz_lst   = [x for x in helper.ops.getOption('freeze_parameters')]
    redef_lst = [x for x in helper.ops.getOption('redefine_pois')]
    pois = helper.dc_maker.getOperators()

    ## To make impact plots with a simultaneous fit of all signals
    poi_lst = [x for x in pois if x not in frz_lst] # This is to ensure we don't try to make an impact plot for a frozen parameter

    ## Not needed for CombineMethod.MULTIDIMFIT
    # range_str = helper.getPOIRangeStr(pois)
    # helper.setOptions(extend=True,other_options=['--setParameterRanges',range_str])

    # for poi in poi_lst: helper.runCombine(method=CombineMethod.IMPACTS,redefine_pois=[poi])

    ## We don't redefine the POIs, so the other POIs don't become unconstrained nuisance parameters and will not appear in the impact plots...
    ## This seems to have no change on the limits of the POIs, other then the other POIs don't appear in the impact plots
    # helper.runCombine(method=CombineMethod.IMPACTS)

    ## To make fitresult objects for pre/postfit yields
    # helper.runCombine(method=CombineMethod.FITDIAGNOSTIC,name='Prefit',minos_arg='all')
    # helper.setOptions(other_options=['--cminDefaultMinimizerStrategy=2','--cminPoiOnlyFit'])
    # helper.setOptions(other_options=['--cminDefaultMinimizerStrategy=2'])
    # helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Postfit')
    # helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Freeze',freeze_parameters=pois)   # Note: We should really add back in the removed systematics for this fit
    # helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Stats',freeze_parameters=[])      # Just to make workspace_testing.C happy, not needed for overlay_operator_variations.C

    helper.runCombine(method=CombineMethod.IMPACTS,robust_fit=False)

    ## To scan a nuisance parameter
    ## -- Work in progress --

    ## To make impact plots with other signals frozen
    # rm_systs['pdf_gg'].setOptions(procs=['ttll']); rm_systs['QCDscale_ttbar'].setOptions(procs=['ttll'])
    # to_remove = [rm_systs['pdf_gg'],rm_systs['QCDscale_ttbar']]
    # individual_impact_plots(helper,['mu_ttll'],to_remove)
    
    # to_remove = [rm_systs['pdf_ggttH'],rm_systs['QCDscale_ttH'],rm_systs['pdf_qgtHq'],rm_systs['QCDscale_tHq']]
    # individual_impact_plots(helper,['mu_ttH'],to_remove)
    
    # rm_systs['pdf_qq'].setOptions(procs=['ttlnu']); rm_systs['QCDscale_ttbar'].setOptions(procs=['ttlnu'])
    # to_remove = [rm_systs['pdf_qq'],rm_systs['QCDscale_ttbar']]
    # individual_impact_plots(helper,['mu_ttlnu'],to_remove)
    
    # rm_systs['pdf_qq'].setOptions(procs=['tllq']); rm_systs['QCDscale_V'].setOptions(procs=['tllq'])
    # to_remove = [rm_systs['pdf_qq'],rm_systs['QCDscale_V']]
    # individual_impact_plots(helper,['mu_tllq'],to_remove)

    if copy_output:
        search_strs = ["^impacts_.*pdf$"]
        helper.copyOutput(copy_dir,rgx_list=search_strs,clean_directory=False)

    helper.chdir(helper.home_dir)

    logging.info('Logger shutting down!')
    logging.shutdown()

    ### OLD UNUSED/DEPRECATED SHIT ###

    # add_systs = {}
    # add_systs['tHq_1j'] = CombineSystematic(syst_name='tHq_1j',val_u=1.1,procs=['tHq'],bins=['^C_2lss_.*_4j$'  ,'^C_3l_.*_2j$'],syst_type='lnN')
    # add_systs['tHq_2j'] = CombineSystematic(syst_name='tHq_2j',val_u=1.2,procs=['tHq'],bins=['^C_2lss_.*_5j$'  ,'^C_3l_.*_3j$'],syst_type='lnN')
    # add_systs['tHq_3j'] = CombineSystematic(syst_name='tHq_3j',val_u=1.3,procs=['tHq'],bins=['^C_2lss_.*_6j$'  ,'^C_3l_.*_4j$'],syst_type='lnN')
    # add_systs['tHq_4j'] = CombineSystematic(syst_name='tHq_4j',val_u=1.4,procs=['tHq'],bins=['^C_2lss_.*_ge7j$','^C_3l_.*_ge5j$'],syst_type='lnN')
    # add_systs['tllq_1j'] = CombineSystematic(syst_name='tllq_1j',val_u=1.1,procs=['tllq'],bins=['^C_3l_.*_2j$'],syst_type='lnN')
    # add_systs['tllq_2j'] = CombineSystematic(syst_name='tllq_2j',val_u=1.2,procs=['tllq'],bins=['^C_3l_.*_3j$'],syst_type='lnN')
    # add_systs['tllq_3j'] = CombineSystematic(syst_name='tllq_3j',val_u=1.3,procs=['tllq'],bins=['^C_3l_.*_4j$'],syst_type='lnN')
    # add_systs['tllq_4j'] = CombineSystematic(syst_name='tllq_4j',val_u=1.4,procs=['tllq'],bins=['^C_3l_.*_ge5j$'],syst_type='lnN')
    # add_systs['ttH_1j'] = CombineSystematic(syst_name='ttH_1j',val_u=1.1,procs=['ttH'],bins=['^C_2lss_.*_ge7j$','^C_3l_.*_ge5j$','^C_4l_.*_3j$'],syst_type='lnN')
    # add_systs['ttH_2j'] = CombineSystematic(syst_name='ttH_2j',val_u=1.2,procs=['ttH'],bins=['^C_4l_.*_ge4j$'],syst_type='lnN')
    # add_systs['ttll_1j'] = CombineSystematic(syst_name='ttll_1j',val_u=1.1,procs=['ttll'],bins=['^C_3l_.*_4j$','^C_4l_.*_3j$'],syst_type='lnN')
    # add_systs['ttll_2j'] = CombineSystematic(syst_name='ttll_2j',val_u=1.2,procs=['ttll'],bins=['^C_4l_.*_ge4j$'],syst_type='lnN')
    # add_systs['ttlnu_1j'] = CombineSystematic(syst_name='ttlnu_1j',val_u=1.1,procs=['ttlnu'],bins=['^C_2lss_.*_5j$'  ,'^C_3l_.*_3j$'],syst_type='lnN')
    # add_systs['ttlnu_2j'] = CombineSystematic(syst_name='ttlnu_2j',val_u=1.2,procs=['ttlnu'],bins=['^C_2lss_.*_6j$'  ,'^C_3l_.*_4j$'],syst_type='lnN')
    # add_systs['ttlnu_3j'] = CombineSystematic(syst_name='ttlnu_3j',val_u=1.3,procs=['ttlnu'],bins=['^C_2lss_.*_ge7j$','^C_3l_.*_ge5j$'],syst_type='lnN')

    # helper.make_fitdiagnostics(name='Prefit')
    # helper.make_multidimfit(name='Postfit',freeze_lst=[])
    # helper.make_multidimfit(name='Stats',freeze_lst=list(keep_systs),saved_workspace='Postfit')
    # helper.make_grid_scan(grid_pois=['ctZ'])

    # To make fitresult objects for pre/postfit yields
    # helper.make_fitdiagnostics(name='Prefit')
    # helper.make_tonyfit(name='Postfit')
    # helper.make_tonyfit(name='Freeze',freeze_lst=pois)  # Note: We should really add back in the removed systematics for this fit
    # helper.make_tonyfit(name='Stats')   # Just to make workspace_testing.C happy
    # for p in pois:
    #    name = "Bestfit%s" % (p)
    #    helper.make_tonyfit(name=name,redefine_pois=[p])

    # To make impact plots with a simultaneous fit of all signals
    # helper.make_impact_plots(tar_pois=['mu_ttll'] ,freeze_others=False)
    # helper.make_impact_plots(tar_pois=['mu_ttH']  ,freeze_others=False)
    # helper.make_impact_plots(tar_pois=['mu_ttlnu'],freeze_others=False)
    # helper.make_impact_plots(tar_pois=['mu_tllq'] ,freeze_others=False)

    # To make impact plots with other signals frozen
    # rm_systs = [{'bin': '.*','process': 'ttll', 'systs': ['^pdf_gg$','^QCDscale_ttbar$']}]
    # individual_impact_plots(helper,['mu_ttll'],rm_systs)
    # rm_systs  = [{'bin': '.*','process': 'ttH', 'systs': ['^pdf_ggttH$','^QCDscale_ttH$']}]
    # rm_systs += [{'bin': '.*','process': 'tHq', 'systs': ['^pdf_qgtHq$','^QCDscale_tHq$']}]
    # individual_impact_plots(helper,['mu_ttH'],rm_systs)
    # rm_systs = [{'bin': '.*','process': 'ttlnu', 'systs': ['^pdf_qq$','^QCDscale_ttbar$']}]
    # individual_impact_plots(helper,['mu_ttlnu'],rm_systs)
    # rm_systs = [{'bin': '.*','process': 'tllq', 'systs': ['^pdf_qq$','^QCDscale_V$']}]
    # individual_impact_plots(helper,['mu_tllq'],rm_systs)

    # helper.make_SMfit(tar_pois=['mu_tHq','mu_tllq'],freeze_others=True)

    # helper.test_running()

    # helper.make_fitdistribution()
    # helper.make_uncertainties()

def test_read(fpath,wc_leaf,tracked_params,skip_header=False):
    def add_row(tree,entry,leaves,rows,target_wc=None):
        tree.GetEntry(entry)
        row = []
        if target_wc:
            row = [target_wc]
        else:
            row = [entry]
        for leaf in leaves:
            row.append(tree.GetLeaf(leaf).GetValue(0))
        rows.append(row)
    # print "fpath: {}".format(fpath)
    root_file = ROOT.TFile.Open(fpath)
    limit_tree = root_file.Get("limit")

    col_names = ['entry','deltaNLL']
    for s in tracked_params:
        col_names.append(s)

    leaves = ['deltaNLL']
    for s in tracked_params:
        if s == wc_leaf:
            leaves.append(s)
        else:
            leaves.append("trackedParam_{wc}".format(wc=s))

    rows = []
    if not skip_header:
        rows.append(col_names)
    min_entry = 0
    min_dll = limit_tree.GetLeaf("deltaNLL").GetValue(0)
    for entry in range(limit_tree.GetEntries()):
        limit_tree.GetEntry(entry)
        dll = limit_tree.GetLeaf("deltaNLL").GetValue(0)
        if min_dll > dll:
            min_entry = entry
            min_dll = dll
    add_row(limit_tree,min_entry,leaves,rows,target_wc=wc_leaf)
    
    width = 8
    for r in rows:
        str_lst = []
        for x in r:
            if isinstance(x,float):
                tmp_str = "{:+.4f}".format(x)
                str_lst.append("{:<{w}}".format(tmp_str,w=width))
            else:
                str_lst.append("{:<{w}}".format(x,w=width))
        print " ".join(str_lst)

    root_file.Close()

if __name__ == "__main__":
    # main()
    # make_impacts_from_tony_inputs()

    anatest_dir = os.path.expanduser('~awightma/Public/anatest_files')
    hist_dir = os.path.expandvars('${CMSSW_BASE}/src/CombineHarvester/TopEFT/hist_files')

    # Requires old TH1EFT library
    a28 = 'anatest28.root'
    a28_redo = 'anatest28_redoFullWF-NoStreaming.root'
    a28_mixin_tHq   = 'anatest28_mixin-a31-tHq.root'
    a28_mixin_ttH   = 'anatest28_mixin-a31-ttH.root'
    a28_mixin_tllq  = 'anatest28_mixin-a31-tllq.root'
    a28_mixin_ttll  = 'anatest28_mixin-a31-ttll.root'
    a28_mixin_ttlnu = 'anatest28_mixin-a31-ttlnu.root'
    a28_mixin_ttH_ttlnu = 'anatest28_mixin-a31-ttH-ttlnu.root'
    a28_mixin_ttll_tllq = 'anatest28_mixin-a31-ttll-tllq.root'
    a28_mixin_ttH_ttll = 'anatest28_mixin-a31-ttH-ttll.root'
    a29_noDupes = 'anatest29_NoDuplicatesV2.root'
    a29 = 'anatest29.root'
    a31 = 'anatest31.root'
    # Requires updated TH1EFT library
    a28_fixed = 'anatest28_fixedErrors.root'
    a31_fixed = 'anatest31_fixedErrors.root'
    a32 = 'anatest32.root'

    hanV4_SMCheck = 'private_sgnl_HanV4_SMCheck.root'
    hanOrig_SMCheck = 'private_sgnl_HanOriginal_SMCheck.root'   # Currently doesn't make sense since it
                                                                # doesn't have the tllq and tHq samples

    # dir_name = 'ana32_private'
    # dir_name = 'ana32_central'
    #dir_name = 'ana32_private_sgnl_Default-PSWeights-Symmetrized_moreStats'
    # dir_name = 'ana32_private_sgnl_Default-PSWeights-Symmetrized_adHoc-MissingPartonSyst_moreStats'
    # dir_name = 'ana32_private_sgnl_Default-PSWeights-Symmetrized_MatchingSyst_moreStats_with-NuisOnly'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_with-NuisOnly_cmin2'

    dir_name = 'ana32_private_sgnl_Asimov_Decorrelated-PS-PDF-Q2RF-QCUT_cmin1-robustHesse1'
    # dir_name = 'ana32_private_sgnl_Asimov_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0-poiRanges'
    hist_file = a32
    hist_file_merged = "{}_MergeLepFl.root".format(hist_file.strip('.root'))

    src_hist_loc = os.path.join(anatest_dir,hist_file)
    dst_hist_loc = os.path.join(hist_dir,hist_file)

    if not os.path.exists(src_hist_loc):
        print "Unknown anatest file: {}".format(hist_file)
        sys.exit()

    merged_hist_loc = os.path.join(hist_dir,hist_file_merged)

    # base_path = os.path.join(CONSTS.CMSSW_SRC,'EFTFit/Fitter/test/fromBrent/EFT-Private-Float_2019-12-11')
    # wc_lst = [
    #     "ctW","ctZ","ctp","cpQM",
    #     "ctG","cbW","cpQ3","cptb",
    #     "cpt","cQl3i","cQlMi","cQei",
    #     "ctli","ctei","ctlSi","ctlTi"
    # ]
    # for idx,wc in enumerate(wc_lst):
    #     fname = "higgsCombine.EFT.Private.Float.12112019.{wc}.MultiDimFit.root".format(wc=wc)
    #     fpath = os.path.join(base_path,fname)
    #     skip_header = idx != 0
    #     test_read(fpath,wc,wc_lst,skip_header)
    # sys.exit()

    if not os.path.exists(merged_hist_loc):
        print "Copying {src} to {dst}".format(srd=src_hist_loc,dst=dst_hist_loc)
        shutil.copy(src_hist_loc,dst_hist_loc)  # This is needed b/c we can't specify rel. dirs. in CLF
        CLF = CombineLepFlavors()
        CLF.Filename = hist_file
        print "Making merged anatest file: {fname}".format(fname=hist_file_merged)
        CLF.execute()

    runit(
        group_directory='data2017v1',
        dir_name=dir_name,
        hist_file=hist_file_merged,
        mode=HelperMode.EFT_IMPACTS,
        # mode=HelperMode.EFT_FITTING,
        testing=False,
        force=False,
        copy_output=True
    )