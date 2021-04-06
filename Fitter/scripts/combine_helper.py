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
from EFTFit.Fitter.options import CombineSystematic
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
    EFT_FITTING  = 'EFT_fitting'
    EFT_IMPACTS  = 'EFT_impacts'
    EFT_GRIDSCAN = 'EFT_gridscan'
    EFT_GOF      = 'EFT_gof'

    @classmethod
    def isSM(cls,mode):
        return (mode in [cls.SM_FITTING,cls.SM_IMPACTS,cls.SM_PREFIT])

    @classmethod
    def isEFT(cls,mode):
        return (mode in [cls.EFT_FITTING,cls.EFT_IMPACTS,cls.EFT_GRIDSCAN,cls.EFT_GOF])

# For producing fits with the EFT WCs as the POIs
EFT_OPS = HelperOptions(
    ws_file      = '16D.root',
    model        = 'EFTFit.Fitter.EFTModel:eftmodel',
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
        # ('tHq',  'mu_tHq',  [1]),  # Lets tHq be a free parameter in the fit
    ],
    prefit_value = 1.0,
    algo         = FitAlgo.SINGLES
)

# Configure logging to an output file
def setup_logger(log_file):
    outlog = logging.FileHandler(filename=log_file,mode='w')
    outlog.setLevel(logging.DEBUG)
    outlog.setFormatter(frmt)
    logging.getLogger('').addHandler(outlog)

    logging.info("Log file: %s",log_file)

def runit(group_directory,dir_name,mode,helper_ops,testing=False,force=False,copy_output=False,modify_datacard=False):
    out_name = '{mode}_{tstamp}_{name}'.format(mode=mode,tstamp=TSTAMP2,name=dir_name)
    if testing:
        out_name = '{mode}_testing'.format(mode=mode)

    # Should be relative to the CombineHelper 'home' directory
    out_dir = os.path.join(group_directory,out_name)

    helper = CombineHelper(out_dir=out_dir)
    helper.setOptions(preset=helper_ops)

    # Needs to come after the helper is insantiated, b/c of the logger in the helper
    setup_logger(os.path.join(helper.output_dir,'out.log'))

    logging.info('group_directory: {}'.format(group_directory))
    logging.info('dir_name: {}'.format(dir_name))
    logging.info('out_dir: {}'.format(out_name))
    logging.info('hist_file: {}'.format(helper_ops.getOption('histogram_file')))
    logging.info('mode: {}'.format(mode))
    logging.info('testing: {}'.format(testing))
    logging.info('force: {}'.format(force))
    logging.info('copy_output: {}'.format(copy_output))

    # TODO: Should make these configurable from outside of the runit() function
    keep_bins = []
    # keep_bins = ['^C_2lss_.*','^C_3l_mix_sfz_.*','^C_4l_.*']
    keep_bins = ['^C_2lss_.*','^C_3l_.*']

    systs_to_remove = []
    # systs_to_remove = [ CombineSystematic(syst_name='FR_stats_.*',procs=['.*'],bins=['.*']) ]

    to_keep = ["^EFT_MultiDim_Datacard.txt","^16D.root","^SMWorkspace.root","^out.log$"]
    helper.cleanDirectory(helper.output_dir,keep=to_keep)
    if force:
        helper.make_datacard()
        if modify_datacard:
            helper.modifyDatacard("mod_datacard.txt",filter_bins=keep_bins,remove_systs=systs_to_remove)
        helper.make_workspace()
    else:
        if not helper.hasDatacard():
            helper.make_datacard()
        if modify_datacard:
            helper.loadDatacard()
            helper.modifyDatacard("mod_datacard.txt",filter_bins=keep_bins,remove_systs=systs_to_remove)
            helper.make_workspace()
        if not helper.hasWorkspace():
            helper.make_workspace()
    helper.loadDatacard(force=True)

    # for b in helper.dc_reader.getBins(keep=['C_3l_mix_sfz_.*']):
    #     tmp = helper.dc_reader.cb.cp()
    #     tmp.bin([b])
    #     tmp.process(["Diboson","Triboson"])
    #     # tmp.PrintProcs()
    #     tmp.PrintSysts()
    # return

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

    # NOTE1: For the batch submission methods, the main thread won't be locked!
    # NOTE2: When using batch submission, the non-scanned PoIs are automatically added to tracked list
    if mode == HelperMode.EFT_GRIDSCAN:
        helper.poi_ranges = {
            'ctW':(-6,6),    'ctZ':(-7,7),
            'cpt':(-40,30),  'ctp':(-35,65),
            'ctli':(-20,20), 'ctlSi':(-22,22),
            'cQl3i':(-20,20),'cptb':(-40,40),
            'ctG':(-3,3),    'cpQM':(-30,50),  
            'ctlTi':(-4,4),  'ctei':(-20,20),
            'cQei':(-16,16), 'cQlMi':(-17,17),
            'cpQ3':(-20,12), 'cbW':(-10,10)
        }
        to_scan = helper.ops.getOption('set_parameters')
        helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='GridScan',
            algo=FitAlgo.GRID,
            save_fitresult=False
        )

    # Skips finding the impacts for these nuisances
    to_exclude = []
    to_exclude.extend(helper.getSysts(['FR_stats_.*','^QCDscale_VVV$','[lh]fstats[12]']))

    if mode == HelperMode.SM_IMPACTS:
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

    if mode == HelperMode.EFT_GOF:
        to_track = pois + helper.getSysts()
        poi_values = ["{poi}=0.0".format(poi=k) for k in pois]
        all_values = ["{param}=0.0".format(param=k) for k in to_track]
        helper.runCombine(method=CombineMethod.GOF,name='GOF',
            parameter_values=poi_values,
            parameters_for_eval=poi_values,
            # parameter_values=all_values,
            # parameters_for_eval=all_values,
            track_parameters=to_track,

            freeze_parameters=pois
        )

    print os.getcwd()

    if copy_output:
        if mode == HelperMode.SM_IMPACTS or mode == HelperMode.EFT_IMPACTS:
            dst_dir = os.path.join(CONST.WEB_DIR,'eft_stuff/misc/impact_plots',out_dir)
            helper.copyOutput(dst_dir,rgx_list=["^impacts_.*pdf$"],clean_directory=False)

    logging.info('Logger shutting down!')
    logging.shutdown()

if __name__ == "__main__":
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
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_with-NuisOnly_cmin0'

    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_with-NuisOnly_no-SFZ-bin-mask_cmin0'

    # dir_name = 'ana32_private_sgnl_Asimov_Decorrelated-PS-PDF-Q2RF-QCUT_cmin1-robustHesse1'
    # dir_name = 'ana32_private_sgnl_Asimov_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0-poiRanges'

    # Name for GOF tests
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_5k-toys'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_bypassFrequentistFit_5k-toys'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin2_bypassFrequentistFit_5k-toys'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin2_5k-toys'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_freezePOIs_5k-toys'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_freezePOIs_50k-toys'

    # Name for gridscan tests
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_2D-ctG-ctW-ctZ-90k-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_setAllRanges_2D-ctp-90k-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_2D-cpt-cptb-ctli-ctlSi-90k-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_2D-ctlTi-cpQM-cQl3i-ctei-cQei-cQlMi-cpQ3-cbW-90k-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_3D-ctGctWctp-ctWctZctp-cpQMcpQ3ctp-1M-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_3D-cpQMcpQ3ctp-10M-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_3D-ctGcpQMctp-1M-pts'
    dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_floatPOIs_3D-ctGcpQMctp-10M-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_freezePOIs_3D-cpQMcpQ3ctp-10M-pts'
    # dir_name = 'ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_cmin0_freezePOIs_2D-AllCombos-90k-pts'

    hist_file = a32
    hist_file_merged = "{}_MergeLepFl.root".format(hist_file.strip('.root'))

    src_hist_loc = os.path.join(anatest_dir,hist_file)
    dst_hist_loc = os.path.join(hist_dir,hist_file)

    if not os.path.exists(src_hist_loc):
        print "Unknown anatest file: {}".format(hist_file)
        sys.exit()

    merged_hist_loc = os.path.join(hist_dir,hist_file_merged)

    if not os.path.exists(merged_hist_loc):
        print "Copying {src} to {dst}".format(src=src_hist_loc,dst=dst_hist_loc)
        shutil.copy(src_hist_loc,dst_hist_loc)  # This is needed b/c we can't specify rel. dirs. in CLF
        CLF = CombineLepFlavors()
        CLF.Filename = hist_file
        print "Making merged anatest file: {fname}".format(fname=hist_file_merged)
        CLF.execute()

    # What type of combine action to take
    # mode = HelperMode.EFT_GOF
    mode = HelperMode.EFT_GRIDSCAN

    if HelperMode.isSM(mode):
        ops = HelperOptions(**SM_SIGNAL_OPS.getCopy())
    elif HelperMode.isEFT(mode):
        ops = HelperOptions(**EFT_OPS.getCopy())
    else:
        raise RuntimeError("Unknown run mode: {}".format(mode))

    ops.setOptions(
        verbosity=2,
        fake_data=False,
        save_fitresult=True,
        use_central=False,
        use_poi_ranges=False,
        histogram_file=hist_file_merged
        # histogram_file=hist_file
    )

    already_done = [
        ('ctG','ctW'),
        ('ctG','ctZ'),
        ('ctG','ctp'),
        ('ctG','cpt'),
        ('ctG','cptb'),
        ('ctG','ctli'),
        ('ctG','ctlSi'),
        ('ctG','ctlTi'),
        ('ctG','cpQM'),
        ('ctG','cQl3i'),
        ('ctG','ctei'),
        ('ctG','cQei'),
        ('ctG','cQlMi'),
        ('ctG','cpQ3'),
        ('ctG','cbW'),

        ('ctW','ctZ'),
        ('ctW','ctp'),
        ('ctW','cpt'),
        ('ctW','cptb'),
        ('ctW','ctli'),
        ('ctW','ctlSi'),
        ('ctW','ctlTi'),
        ('ctW','cpQM'),
        ('ctW','cQl3i'),
        ('ctW','ctei'),
        ('ctW','cQei'),
        ('ctW','cQlMi'),
        ('ctW','cpQ3'),
        ('ctW','cbW'),

        ('ctZ','ctp'),
        ('ctZ','cpt'),
        ('ctZ','cptb'),
        ('ctZ','ctli'),
        ('ctZ','ctlSi'),
        ('ctZ','ctlTi'),
        ('ctZ','cpQM'),
        ('ctZ','cQl3i'),
        ('ctZ','ctei'),
        ('ctZ','cQei'),
        ('ctZ','cQlMi'),
        ('ctZ','cpQ3'),
        ('ctZ','cbW'),

        ('ctp','cpt'),
        ('ctp','cptb'),
        ('ctp','ctli'),
        ('ctp','ctlSi'),
        ('ctp','ctlTi'),
        ('ctp','cpQM'),
        ('ctp','cQl3i'),
        ('ctp','ctei'),
        ('ctp','cQei'),
        ('ctp','cQlMi'),
        ('ctp','cpQ3'),
        ('ctp','cbW'),

        ('cpt','cptb'),
        ('cpt','ctli'),
        ('cpt','ctlSi'),
        ('cpt','ctlTi'),
        ('cpt','cpQM'),
        ('cpt','cQl3i'),
        ('cpt','ctei'),
        ('cpt','cQei'),
        ('cpt','cQlMi'),
        ('cpt','cpQ3'),
        ('cpt','cbW'),

        ('cptb','ctli'),
        ('cptb','ctlSi'),
        ('cptb','ctlTi'),
        ('cptb','cpQM'),
        ('cptb','cQl3i'),
        ('cptb','ctei'),
        ('cptb','cQei'),
        ('cptb','cQlMi'),
        ('cptb','cpQ3'),
        ('cptb','cbW'),

        ('ctli','ctlSi'),
        ('ctli','ctlTi'),
        ('ctli','cpQM'),
        ('ctli','cQl3i'),
        ('ctli','ctei'),
        ('ctli','cQei'),
        ('ctli','cQlMi'),
        ('ctli','cpQ3'),
        ('ctli','cbW'),

        ('ctlSi','ctlTi'),
        ('ctlSi','cpQM'),
        ('ctlSi','cQl3i'),
        ('ctlSi','ctei'),
        ('ctlSi','cQei'),
        ('ctlSi','cQlMi'),
        ('ctlSi','cpQ3'),
        ('ctlSi','cbW'),

        ('ctlTi','cpQM'),
        ('ctlTi','cQl3i'),
        ('ctlTi','ctei'),
        ('ctlTi','cQei'),
        ('ctlTi','cQlMi'),
        ('ctlTi','cpQ3'),
        ('ctlTi','cbW'),

        ('cpQM','cQl3i'),
        ('cpQM','ctei'),
        ('cpQM','cQei'),
        ('cpQM','cQlMi'),
        ('cpQM','cpQ3'),
        ('cpQM','cbW'),

        ('cQl3i','ctei'),
        ('cQl3i','cQei'),
        ('cQl3i','cQlMi'),
        ('cQl3i','cpQ3'),
        ('cQl3i','cbW'),

        ('ctei','cQei'),
        ('ctei','cQlMi'),
        ('ctei','cpQ3'),
        ('ctei','cbW'),

        ('cQei','cQlMi'),
        ('cQei','cpQ3'),
        ('cQei','cbW'),

        ('cQlMi','cpQ3'),
        ('cQlMi','cbW'),

        ('cpQ3','cbW'),
    ]

    # Some grid scan options
    batch_list = [
        ('ctG','cpQM','ctp')
        # ('ctG','ctW','ctp'),
        # ('ctZ','ctW','ctp'),
        # ('cpQM','cpQ3','ctp'),
    ]
    ops.setOptions(
        # set_parameters=['ctZ','ctW'],
        batch_list=batch_list,
        # scan_points=300**2,
        scan_points=220**3,
        split_points=30000,
        float_other_pois=True,
        use_poi_ranges=True,
        batch_type=BatchType.CONDOR
    )
    ops.setOptions(extend=True,other_options=[
        '--cminDefaultMinimizerStrategy=0',
        '--cminPreScan'
    ])
    # Some options for doing the GoodnessOfFit test
    # ops.setOptions(extend=True,
    #     algo=FitAlgo.SATURATED,
    #     batch_type=BatchType.CONDOR,
    #     toys=50000,
    #     seed=5264981,
    #     other_options=[
    #         # '--cminDefaultMinimizerStrategy=2',
    #         # '--bypassFrequentistFit',
    #         # '--saveToys',
    # ])
    # Other options
    # ops.setOptions(extend=True,other_options=[
    #     '--cminDefaultMinimizerStrategy=0',
    #     # '--cminPoiOnlyFit',
    #     # '--autoMaxPOIs=*'
    #     # '--robustHesse=1',
    # ])

    runit(
        group_directory='data2017v1',
        dir_name=dir_name,
        helper_ops=ops,
        mode=mode,
        testing=True,
        force=False,
        copy_output=False,
        modify_datacard=False
    )
