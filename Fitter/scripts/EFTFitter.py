import os
import stat
import sys
import logging
import subprocess as sp
import ROOT
import itertools
import glob
import getpass
import array
import random
import json
import uproot
import numpy as np
from collections import defaultdict
from EFTFit.Fitter.findMask import findMask
from itertools import chain
from scipy.stats import chi2

# Batch modes supported are: CRAB3 ('crab') and Condor ('condor')

class EFTFit(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # WCs lists for easy use
        # Full list of opeators
        self.wcs = ["cQd1", "ctj1", "cQj31", "ctj8", "ctd1", "ctd8", "ctGRe", "ctGIm", "cQj11", "cQj18", "ctu8", "cQd8", "ctu1", "cQu1", "cQj38", "cQu8"]

        # Used for batch1DScanEFT, defines the physics boundaries passed to Combine for the scan
        self.wc_ranges = {
            "cQd1": (-10.0, 10.0),
            "ctj1": (-10.0, 10.0),
            "cQj31":(-10.0, 10.0),
            "ctj8": (-10.0, 10.0),
            "ctd1": (-10.0, 10.0),
            "ctd8": (-10.0, 10.0),
            "ctGRe":(-1.0, 1.0),
            "ctGIm":(-1.0, 1.0),
            "cQj11":(-10.0, 10.0),
            "cQj18":(-10.0, 10.0),
            "ctu8": (-10.0, 10.0),
            "cQd8": (-10.0, 10.0),
            "ctu1": (-10.0, 10.0),
            "cQu1": (-10.0, 10.0),
            "cQj38":(-10.0, 10.0),
            "cQu8": (-10.0, 10.0)
        }

        self.wc_ranges_differential = {
            "cQd1": (-4.0, 4.0),
            "ctj1": (-4.0, 4.0),
            "cQj31":(-4.0, 4.0),
            "ctj8": (-4.0, 4.0),
            "ctd1": (-4.0, 4.0),
            "ctd8": (-4.0, 4.0),
            "ctGRe":(-1.5, 1.5),
            "ctGIm":(-1.5, 1.5),
            "cQj11":(-4.0, 4.0),
            "cQj18":(-4.0, 4.0),
            "ctu8": (-4.0, 4.0),
            "cQd8": (-4.0, 4.0),
            "ctu1": (-4.0, 4.0),
            "cQu1": (-4.0, 4.0),
            "cQj38":(-4.0, 4.0),
            "cQu8": (-4.0, 4.0)
        }

        # self.systematics = [
        #     'L1prefire', 'PU', 'lumi', 
        #     'FSR', 'ISR', 'hdamp', 'PDF',
        #     'smxsec_tt', 'smxsec_tW', 'smxsec_DY', 'smxsec_Others',
        #     # 'fact_DY', 'fact_Diboson', 'fact_TTll', 'fact_Triboson', 'fact_WWZ', 'fact_tW', 'fact_tt',
        #     # 'renorm_DY', 'renorm_Diboson', 'renorm_TTll', 'renorm_Triboson', 'renorm_WWZ', 'renorm_tW', 'renorm_tt',
        #     'fact_tt', 'fact_tW', 'fact_DY', 'fact_Others',
        #     'renorm_tt', 'renorm_tW', 'renorm_DY', 'renorm_Others',
        #     # 'factrenorm',
        #     # 'elecID',  
        #     "elecHEEP", "elecRECO",
        #     'muonID', 'muonISO',  'trigSF',
        #     'jetPuID', 'METunclust',
        #     'btagSFbc_2016','btagSFbc_2016APV', 'btagSFbc_2017', 'btagSFbc_2018', 'btagSFbc_correlated', 
        #     'btagSFlight_2016','btagSFlight_2016APV', 'btagSFlight_2017', 'btagSFlight_2018', 'btagSFlight_correlated', 
        #     'JER_2016','JER_2016APV','JER_2017','JER_2018',
        #     'JES_AbsoluteMPFBias','JES_AbsoluteScale','JES_AbsoluteStat','JES_FlavorPureBottom','JES_FlavorPureCharm','JES_FlavorPureGluon','JES_FlavorQCD','JES_Fragmentation','JES_PileUpDataMC','JES_PileUpPtBB','JES_PileUpPtEC1','JES_PileUpPtEC2','JES_PileUpPtHF','JES_PileUpPtRef','JES_RelativeBal','JES_RelativeFSR','JES_RelativeJEREC1','JES_RelativeJEREC2','JES_RelativeJERHF','JES_RelativePtBB', 'JES_RelativePtEC1','JES_RelativePtEC2','JES_RelativePtHF','JES_RelativeSample','JES_RelativeStatEC','JES_RelativeStatFSR','JES_RelativeStatHF','JES_SinglePionECAL','JES_SinglePionHCAL','JES_TimePtEta',
        #     "prop_binch1_bin0_tt_sm","prop_binch1_bin0_tW_sm","prop_binch1_bin0_Others_sm","prop_binch1_bin1_tt_sm","prop_binch1_bin1_tW_sm","prop_binch1_bin1_DY_sm","prop_binch1_bin1_Others_sm","prop_binch1_bin2","prop_binch1_bin3","prop_binch1_bin4","prop_binch1_bin5","prop_binch1_bin6","prop_binch1_bin7","prop_binch1_bin8","prop_binch1_bin9","prop_binch1_bin10","prop_binch1_bin11","prop_binch1_bin12","prop_binch1_bin13","prop_binch1_bin14","prop_binch1_bin15","prop_binch2_bin0","prop_binch2_bin1_tt_sm","prop_binch2_bin1_tW_sm","prop_binch2_bin1_DY_sm","prop_binch2_bin1_Others_sm","prop_binch2_bin2","prop_binch2_bin3","prop_binch2_bin4","prop_binch2_bin5","prop_binch2_bin6","prop_binch2_bin7","prop_binch2_bin8","prop_binch2_bin9","prop_binch2_bin10","prop_binch2_bin11","prop_binch2_bin12","prop_binch2_bin13","prop_binch2_bin14","prop_binch2_bin15_tt_sm","prop_binch2_bin15_tW_sm","prop_binch2_bin15_DY_sm","prop_binch2_bin15_Others_sm","prop_binch3_bin0_tt_sm","prop_binch3_bin0_tW_sm","prop_binch3_bin0_Others_sm","prop_binch3_bin1","prop_binch3_bin2","prop_binch3_bin3","prop_binch3_bin4","prop_binch3_bin5","prop_binch3_bin6","prop_binch3_bin7","prop_binch3_bin8","prop_binch3_bin9","prop_binch3_bin10","prop_binch3_bin11","prop_binch3_bin12","prop_binch3_bin13","prop_binch3_bin14","prop_binch3_bin15","prop_binch4_bin0","prop_binch4_bin1","prop_binch4_bin2","prop_binch4_bin3","prop_binch4_bin4","prop_binch4_bin5","prop_binch4_bin6","prop_binch4_bin7","prop_binch4_bin8","prop_binch4_bin9","prop_binch4_bin10","prop_binch4_bin11","prop_binch4_bin12","prop_binch4_bin13","prop_binch4_bin14","prop_binch4_bin15","prop_binch5_bin0","prop_binch5_bin1","prop_binch5_bin2","prop_binch5_bin3","prop_binch5_bin4","prop_binch5_bin5","prop_binch5_bin6","prop_binch5_bin7","prop_binch5_bin8","prop_binch5_bin9","prop_binch5_bin10","prop_binch5_bin11","prop_binch5_bin12","prop_binch5_bin13","prop_binch5_bin14","prop_binch5_bin15","prop_binch6_bin0_tt_sm","prop_binch6_bin0_tW_sm","prop_binch6_bin0_Others_sm","prop_binch6_bin1","prop_binch6_bin2","prop_binch6_bin3","prop_binch6_bin4","prop_binch6_bin5","prop_binch6_bin6","prop_binch6_bin7","prop_binch6_bin8","prop_binch6_bin9","prop_binch6_bin10","prop_binch6_bin11","prop_binch6_bin12","prop_binch6_bin13","prop_binch6_bin14","prop_binch6_bin15","prop_binch7_bin0_tt_sm","prop_binch7_bin0_tW_sm","prop_binch7_bin0_Others_sm","prop_binch7_bin1","prop_binch7_bin2_tt_sm","prop_binch7_bin2_tW_sm","prop_binch7_bin2_DY_sm","prop_binch7_bin2_Others_sm","prop_binch7_bin3","prop_binch7_bin4","prop_binch7_bin5","prop_binch7_bin6","prop_binch7_bin7","prop_binch7_bin8","prop_binch7_bin9","prop_binch7_bin10","prop_binch7_bin11","prop_binch7_bin12","prop_binch7_bin13","prop_binch7_bin14","prop_binch7_bin15","prop_binch8_bin0_tt_sm","prop_binch8_bin0_tW_sm","prop_binch8_bin0_Others_sm","prop_binch8_bin1","prop_binch8_bin2","prop_binch8_bin3","prop_binch8_bin4","prop_binch8_bin5","prop_binch8_bin6","prop_binch8_bin7","prop_binch8_bin8","prop_binch8_bin9","prop_binch8_bin10","prop_binch8_bin11","prop_binch8_bin12","prop_binch8_bin13","prop_binch8_bin14","prop_binch8_bin15_tt_sm","prop_binch8_bin15_tW_sm","prop_binch8_bin15_DY_sm","prop_binch8_bin15_Others_sm","prop_binch9_bin0_tt_sm","prop_binch9_bin0_Others_sm","prop_binch9_bin1","prop_binch9_bin2","prop_binch9_bin3_tt_sm","prop_binch9_bin3_tW_sm","prop_binch9_bin3_DY_sm","prop_binch9_bin3_Others_sm","prop_binch9_bin4","prop_binch9_bin5","prop_binch9_bin6","prop_binch9_bin7","prop_binch9_bin8","prop_binch9_bin9","prop_binch9_bin10","prop_binch9_bin11","prop_binch9_bin12","prop_binch9_bin13","prop_binch9_bin14","prop_binch9_bin15"
        # ]

        self.systematics = self.get_nuisances_from_workspace()


    def get_nuisances_from_workspace(self, workspace='workspace.root',):
            """Extracts nuisance parameter names directly from the ROOT workspace."""
            if not os.path.exists(workspace):
                self.logger.warning(f"Workspace {ws_path} not found. Using default systematics.")
                return self.systematics

            f = ROOT.TFile.Open(workspace)
            w = f.Get("w")
            mc = w.obj("ModelConfig")
            nuisances = mc.GetNuisanceParameters().contentsString()
            f.Close()
            
            # Convert comma-separated string to a cleaned list
            return [n for n in nuisances.split(',') if n]

    def log_subprocess_output(self, pipe, level):
        ### Pipes Popen streams to logging class ###
        for line in iter(pipe.readline, b''):  # Use b'' to indicate the end condition for a bytes object
            line = line.decode('utf-8')  # Decode the bytes object to a string
            if level == 'info':
                logging.info(line.rstrip('\n'))
            elif level == 'err':
                logging.error(line.rstrip('\n'))
                
    #def log_subprocess_output(self,pipe,level):
    #    ### Pipes Popen streams to logging class ###
    #    for line in iter(pipe.readline, ''):
    #        if level=='info': logging.info(line.rstrip('\n'))
    #        if level=='err': logging.error(line.rstrip('\n'))

    def makeWorkspaceSM(self, datacard='EFT_MultiDim_Datacard.txt'):
        ### Generates a workspace from a datacard ###
        logging.info("Creating workspace")
        if not os.path.isfile(datacard):
            logging.error("Datacard does not exist!")
            return
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['text2workspace.py',datacard,'-P','HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel',
                '--channel-masks',
                #'--PO','map=.*/ttll:mu_ttll[1]','--PO','map=.*/tHq:mu_ttH[1,0,3]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,3]','--PO','map=.*/ttH:mu_ttH[1,0,3]','--PO','map=.*/tllq:mu_tllq[1,0,3]',
                #'--PO','map=.*/ttll:mu_ttll[1,0,3]','--PO','map=.*/tHq:mu_ttH[1]','--PO','map=.*/ttlnu:mu_ttlnu[1]','--PO','map=.*/ttH:mu_ttH[1]','--PO','map=.*/tllq:mu_tllq[1,0,3]',
                #'--PO','map=.*/ttll:mu_ttll[1]','--PO','map=.*/tHq:mu_ttH[1]','--PO','map=.*/ttlnu:mu_ttlnu[1]','--PO','map=.*/ttH:mu_ttH[1]','--PO','map=.*/tllq:mu_tllq[1,0,3]',
                #'--PO','map=.*/ttll:mu_ttll[1,0,30]','--PO','map=.*/tHq:mu_ttH[1,0,30]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,30]','--PO','map=.*/ttH:mu_ttH[1,0,30]','--PO','map=.*/tllq:mu_tllq[1,0,3]',

                #'--PO','map=.*/ttll:mu_ttll[1,0,100]','--PO','map=.*/tHq:mu_ttH[1,0,100]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,100]','--PO','map=.*/ttH:mu_ttH[1,0,100]','--PO','map=.*/tllq:mu_tllq[1,0,100]',
                #'--PO','map=.*/ttll:mu_ttll[1,0,30]','--PO','map=.*/tHq:mu_ttH[1,0,30]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,30]','--PO','map=.*/ttH:mu_ttH[1,0,30]','--PO','map=.*/tllq:mu_tllq[1,0,30]',
                #'--PO','map=.*/ttll:mu_ttll[1,0,15]','--PO','map=.*/tHq:mu_ttH[1,0,15]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,15]','--PO','map=.*/ttH:mu_ttH[1,0,15]','--PO','map=.*/tllq:mu_tllq[1,0,15]',
                #'--PO','map=.*/ttll:mu_ttll[1,0,5]','--PO','map=.*/tHq:mu_ttH[1,0,5]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,5]','--PO','map=.*/ttH:mu_ttH[1,0,5]','--PO','map=.*/tllq:mu_tllq[1,0,5]',
                '--PO','map=.*/ttll:mu_ttll[1]','--PO','map=.*/tHq:mu_ttH[1]','--PO','map=.*/ttlnu:mu_ttlnu[1]','--PO','map=.*/ttH:mu_ttH[1]','--PO','map=.*/tllq:mu_tllq[1]',
                '-o','SMWorkspace.root']

        logging.info(" ".join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()

    def bestFitSM(self, name='.test', freeze=[], autoMaxPOIs=True, other=[], mask=[], mask_syst=[]):
        ### Multidimensional fit ###
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args=['combine','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/SMWorkspace.root','-v','2','--saveFitResult','-M','MultiDimFit','--cminPoiOnlyFit','--cminDefaultMinimizerStrategy=2']
        if freeze:
            params_all=['mu_ttll','mu_ttlnu','mu_ttH','mu_tllq']
            fit=list(set(params_all) - set(freeze))
            name += '.'
            name += '.'.join(fit)
        if name:        args.extend(['-n','{}'.format(name)])
        if mask_syst:
            freeze.append(','.join(mask_syst))
        if freeze:      args.extend(['--freezeParameters',','.join(freeze)])
        if other:       args.extend(other)
        if mask:
            masks = []
            for m in mask:
                msk = findMask(m)
                if not msk:
                    print('No bins found containig ' + m + '! Please check the spelling, and try again.')
                    return
                if 'sfz' not in m:
                    msk = [x for x in msk if 'sfz' not in x]
                masks.append(msk)
            masks = [item for sub in masks for item in sub]
            args.extend(['--setParameters',','.join(masks)])

        logging.info(" ".join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()
        logging.info("Done with SMFit.")
        sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
        sp.call(['mv','multidimfit'+name+'.root','../fit_files/'])
        self.printBestFitsSM(name)

    def gridScanSM(self, name='.test', batch='', scan_params=['mu_ttll'], params_tracked=['mu_ttlnu','mu_ttH','mu_tllq'], points=300, freeze=False, other=[]):
        ### Runs deltaNLL Scan in a parameter using CRAB ###
        ### Can be used to do 2D scans as well ###
        logging.info("Doing grid scan...")

        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['combineTool.py','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/SMWorkspace.root','-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=0']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if scan_params:     args.extend(['-P',' -P '.join(scan_params)]) # Preserves constraints
        if params_tracked: args.extend(['--trackParameters',','.join(params_tracked)])
        if not freeze:        args.extend(['--floatOtherPOIs','1'])
        if other:             args.extend(other)
        # Common 'other' uses: --setParameterRanges param=min,max
        if batch=='crab':      args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points','2000'])
        if batch=='condor':    args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','2000'])
        logging.info(' '.join(args))

        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()
        logging.info("Done with gridScan batch submission.")

        if not batch:
            sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
            logging.info("Done with gridScan.")

    def batch1DScanSM(self, basename='.test', batch='', scan_params=[], points=300, freeze=False, other=[]):
        ### For each SM signal strength, run a 1D deltaNLL Scan.
        if not scan_params:
            scan_params = ['mu_ttll','mu_ttlnu','mu_ttH','mu_tllq']

        for param in scan_params:
            scanmax = 3
            if param=='mu_ttH': scanmax = 6
            if param=='mu_tllq': scanmax = 4            
            self.gridScanSM('{}.{}'.format(basename,param), batch, [param], self.systematics+[params for params in scan_params if params != param], points, freeze, ['--setParameterRanges','{}=0,{}'.format(param,scanmax)]+other)
            
    def batchRetrieve1DScansSM(self, basename='.test', batch='crab'):
        ### For each wc, retrieves finished 1D deltaNLL crab jobs, extracts, and hadd's into a single file ###
        for param in ['mu_ttll','mu_ttlnu','mu_ttH','mu_tllq']:
            self.retrieveGridScan('{}.{}'.format(basename,param),batch)
            
            
            

    def makeWorkspaceEFT(self, datacard='EFT_MultiDim_Datacard.txt'):
        ### Generates a workspace from a datacard and fit parameterization file ###
        logging.info("Creating workspace")
        if not os.path.isfile(datacard):
            logging.error("Datacard does not exist!")
            sys.exit()
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['text2workspace.py',datacard,'-P','EFTFit.Fitter.EFTModel:eftmodel','--PO','fits='+CMSSW_BASE+'/src/EFTFit/Fitter/hist_files/EFT_Parameterization.npy','-o','EFTWorkspace.root','--channel-masks']

        logging.info(' '.join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()
        
    def bestFit(self, name='.test', params_POI=[], startValuesString='', freeze=False, autoBounds=True, other=[]):
        ### Multidimensional fit ###
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        if params_POI == []:
            params_POI = self.wcs
        args=['combine','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/EFTWorkspace.root','-v','2','--saveFitResult','-M','MultiDimFit','-H','AsymptoticLimits','--cminPoiOnlyFit','--cminDefaultMinimizerStrategy=2']
        if name:              args.extend(['-n','{}'.format(name)])
        if params_POI:     args.extend(['-P',' -P '.join(params_POI)]) # Preserves constraints
        args.extend(['--trackParameters',','.join([wc for wc in self.wcs if wc not in params_POI])])
        if startValuesString: args.extend(['--setParameters',startValuesString])
        if not freeze:        args.extend(['--floatOtherPOIs','1'])
        if autoBounds:        args.extend(['--autoBoundsPOIs=*'])
        if other:             args.extend(other)

        logging.info(" ".join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()
        logging.info("Done with bestFit.")
        sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
        if os.path.isfile('multidimfit'+name+'.root'):
            sp.call(['mv','multidimfit'+name+'.root','../fit_files/'])
        self.printBestFitsEFT(name)

    def batchDNNScan(self, name='.test', batch='crab', points=1000000, workspace='ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root', other=[]):
        '''
        This function is designed to submit large scale jobs to CRAB.
        It is confirmed to run on LXPLUS, but has not been tested on Earth (issues with CRAB on slc7) or PSI (should work in principle).
        Submitting jobs relies on the `crab_random` branch on the TopEFT CombineHarvester fork (https://github.com/TopEFT/EFTFit/blob/master/Fitter/test/README.md), 
        or you can make the following changes to the master branch: 
        https://github.com/cms-analysis/CombineHarvester/compare/master...TopEFT:CombineHarvester:crab_random?expand=1#diff-b73f13966085e4d83dee1cae08cd0b9c0e422a257113dbc33ab15b851292fdf7

        Example submission:
        `fitter.batchDNNScan(name='.11302022.EFT.Float.DNN.1M', workspace='ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root', points=1000000)`
        '''
        ### Runs deltaNLL Scan in for a single parameter using CRAB or Condor ###
        logging.info("Doing grid scan...")

        CMSSW_BASE = os.getenv('CMSSW_BASE')

        nsplit = 100 # jobs per task
        jobs = points // nsplit # points per job

        # Generate nsplit jobs, since each needs its own random seed
        logging.info(' '.join(['Generating', str(jobs), 'jobs each with', str(nsplit), 'points for a total of', str(points)]))
        args = ['combineTool.py','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/'+workspace,'-M','MultiDimFit','--algo','random','--skipInitialFit','--cminDefaultMinimizerStrategy=0', '-s -1']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if other:             args.extend(other)

        if batch=='crab':
            args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points',str(nsplit)])
            args.extend(['--setParameterRanges',':'.join(['='.join(wc) for wc in list({k:','.join([str(l) for l in v]) for k,v in list(self.at23v01_2sig_prof.items())}.items())])])
            args.extend(['-P',' -P '.join(self.wcs)])
            args.extend(['--saveToys'])
            # Implement condor later
            #if batch=='condor' and freeze==False and points>3000: args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','3000','--dry-run'])
            #elif batch=='condor' and freeze==False: args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','10','--dry-run'])
            #elif batch=='condor':          args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','10','--dry-run'])
            logging.info(' '.join(args))

            # Run the combineTool.py command
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()
        os.system('find -type d crab_* -size +1M -delete') # Remove input tgz files to save space

    def retrieveDNNScan(self, name='.test', batch='crab'):
        taskname = name.replace('.','')
        logging.info("Retrieving gridScan files. Task name: "+taskname)
        logging.info(' '.join(['Collecting', name]))
        # Find crab output files (defaults to user's hadoop directory)
        host = os.uname()[1]
        if 'lxplus' in host: hadooppath = '/eos/user/{}/{}/EFT/Combine/{}/*/*'.format(os.getlogin()[0], os.getlogin(), taskname)
        #if 'lxplus' in host: hadooppath = '/eos/cms/store/user/{}/EFT/Combine/{}/*/*'.format(os.getlogin(), taskname)
        elif 'earth' in host: hadooppath = '/hadoop/store/user/{}/EFT/Combine/{}/*/*'.format(os.getlogin(), taskname)
        else: raise NotImplementedError('The machine ' + host + ' is not configured! Please add its path to `retrieveGridScan`')
        paths = glob.glob(hadooppath)
        paths = [p for p in (chain.from_iterable(os.walk(path) for path in paths)) if 'log' not in p]
        if not paths[0][2]:
            logging.error("No files found in store!")
            sys.exit()

        # Make a temporary folder to hold the extracted root files
        if not os.path.isdir(taskname+'tmp'):
            sp.call(['mkdir',taskname+'tmp'])
        else:
            logging.error("Directory {}tmp/ already exists! Please rename this directory.".format(taskname))
            return

        def divide_chunks(farray, dfile=1000):
            for i in range(0, len(farray), dfile):
                yield farray[i:i+dfile]
        # Extract the root files
        print('Extracting root files, this will take a few minutes')
        tars = [tarfiles[0]+'/'+tarfile for tarfiles in paths for tarfile in tarfiles[2] if 'log' not in tarfile]
        for tar in divide_chunks(tars, dfile=100):
            process = [sp.Popen(['tar', '-xf', tarfile,'-C', taskname+'tmp'], stdout=sp.PIPE, stderr=sp.PIPE) for tarfile in tar]
            for p in process:
                p.wait()
        '''
        for tarfiles in paths:
            for tarfile in tarfiles[2]:
                if tarfile.endswith('.tar'):
                    #print(tarfiles[0]+'/'+tarfile)
                    sp.call(['tar', '-xf', tarfiles[0]+'/'+tarfile,'-C', taskname+'tmp'])
        '''
        haddargs = ['hadd', '-f', chunk[0].split('.POINT')[0], '.MultiDimFit_', str(ichunk), '.root', ' '.join(chunk)]
        #haddargs = ['hadd','-f','../fit_files/higgsCombine'+name+'.MultiDimFit.root']+['{}tmp/{}'.format(taskname,rootfile) for rootfile in os.listdir(taskname+'tmp') if rootfile.endswith('.root')]
        print(haddargs)
        return
        process = sp.Popen(haddargs, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()

        # Remove the temporary directory and split root files
        sp.call(['rm','-r',taskname+'tmp'])

    def gridScan(self, name='.test', batch='', freeze=False, scan_params=['ctW'], params_tracked=[], points=90000, other=[], mask=[], mask_syst=[], workspace='EFTWorkspace.root', track_error=False):
        ### Runs deltaNLL Scan in two parameters using CRAB or Condor ###
        logging.info("Doing grid scan...")

        CMSSW_BASE = os.getenv('CMSSW_BASE')
        if not "/afs/" in workspace:
            wsname = CMSSW_BASE+'/src/EFTFit/Fitter/test/'+workspace
            if not os.path.exists(wsname):
                print('WARNING! I was not able to find the workspace in afs, I will try finding it by assuming you passed me an absolute path')
                wsname = workspace
        if not os.path.exists(wsname):
            raise RuntimeError('Failed to find the workspace, either considering it as a local afs path or an absolute path. Please, fix it!')
        print('Workspace found! I am gonna use it for running fits...')
        args = ['combineTool.py','-d',wsname,'-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=0']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if scan_params:     args.extend(['-P',' -P '.join(scan_params)]) # Preserves constraints
        track = []
        if any('trackParameters' in s for s in other):
            index = other.index('--trackParameters')
            other.pop(index)
            track.append(other.pop(index))

        if params_tracked: args.extend(['--trackParameters',','.join(params_tracked+track)])
        if track_error: args.extend('--trackErrors rgx{.*}')

        if not freeze:        args.extend(['--floatOtherPOIs','1'])
        params = ['{}=0'.format(wc) for wc in scan_params+params_tracked]
        if '--setParameters' not in other: # Set all starting points to 0 unless the user specifies otherwise
            other.append('--setParameters')
            other.append(','.join(['{}=0'.format(wc) for wc in scan_params+params_tracked]))
        if other:             args.extend(other)
        if mask_syst:
            freeze.append(','.join(mask_syst))
        if mask:
            masks = []
            for m in mask:
                msk = findMask(m)
                if not msk:
                    print('No bins found containig ' + m + '! Please check the spelling, and try again.')
                    return
                if 'sfz' not in m:
                    msk = [x for x in msk if 'sfz' not in x]
                masks.append(msk)
            masks = [item for sub in masks for item in sub]
            params += mask
            args.extend(['--setParameters',','.join(masks)])

        point_scale = 8#hrs
        wall_time  = 8#hrs
        if not freeze: wall_time /= 2 # profiled scans take longer, so submit less points per job
        if batch=='crab':      args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points',str(int(round(wall_time*point_scale)))])
        if batch=='condor' and freeze==False and points>3000: args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','3000','--dry-run'])
        elif batch=='condor' and freeze==False: args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','10','--dry-run'])
        elif batch=='condor':          args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','10','--dry-run'])
        logging.info(' '.join(args))

        # Run the combineTool.py command
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)

        with process.stdout, process.stderr:
            self.log_subprocess_output(process.stdout, 'info')
            self.log_subprocess_output(process.stderr, 'err')
        process.wait()

        # Condor needs executable permissions on the .sh file, so we used --dry-run
        # Add the permission and complete the submission.
        if batch == 'condor':
            if os.path.exists('condor{}'.format(name)):
                logging.error("Directory condor{} already exists!".format(name))
                logging.error("Aborting submission.")

            sp.call(['mkdir', 'condor{}'.format(name)])
            sp.call(['chmod', 'a+x', 'condor_{}.sh'.format(name.replace('.', ''))])
            sp.call(['sed', '-i', 's/ulimit.*/&\\nunset PERL5LIB/', 'condor_{}.sh'.format(name.replace('.', ''))])
            sp.call(['sed', '-i', 's/queue/\\n\\nrequestMemory=10000\\n+JobFlavour = "workday"\\n\\nqueue/', 'condor_{}.sub'.format(name.replace('.', ''))])  # Ask for at least 10GB of RAM

            # Replace hardcoded paths with $CMSSW_BASE and dynamic paths
            cmssw_base = os.getenv('CMSSW_BASE')
            test_dir = os.path.join(cmssw_base, 'src', 'EFTFit', 'Fitter', 'test')

            sp.call(['sed', '-i',
                     's|executable = \(.*\)|executable = {}/src/EFTFit/Fitter/test/condor_{}.sh\\narguments = $(ProcId)|'.format(cmssw_base, name.replace('.', '')),
                     'condor_{}.sub'.format(name.replace('.', ''))
            ])
            
            logging.info('Now submitting condor jobs.')
            condorsub = sp.Popen(['condor_submit', '-append', 'initialdir=condor{}'.format(name), 'condor_{}.sub'.format(name.replace('.', ''))], 
                                 stdout=sp.PIPE, stderr=sp.PIPE)
            #Maybe can be commented out
            with condorsub.stdout, condorsub.stderr:
                self.log_subprocess_output(condorsub.stdout, 'info')
                self.log_subprocess_output(condorsub.stderr, 'err')

            condorsub.wait()

        if batch:
            logging.info("Done with gridScan batch submission.")

        if not batch:
            sp.call(['mv', 'higgsCombine'+name+'.MultiDimFit.mH120.root', '../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
            logging.info("Done with gridScan.")


    def getBestValues2D(self, name, scan_params=[], params_tracked=[]):
        ### Gets values of parameters for grid scan point with best deltaNLL ###
  
        bestDeltaNLL=1000000;
        bestEntry=-1;

        fitFile = '../fit_files/higgsCombine'+name+'.MultiDimFit.root'
        print(fitFile)

        if not os.path.isfile(fitFile):
            logging.error("fitFile does not exist!")
            sys.exit()
        rootFile = ROOT.TFile.Open(fitFile);
        limitTree = rootFile.Get("limit");

        for entry in range(limitTree.GetEntries()):
            limitTree.GetEntry(entry)
            if(bestDeltaNLL > limitTree.GetLeaf("deltaNLL").GetValue(0)):
              bestDeltaNLL = limitTree.GetLeaf("deltaNLL").GetValue(0)
              bestEntry=entry
              #cout << Form("Entry %i deltaNLL=%f, ctW=%f ctZ=%f",bestEntry,bestDeltaNLL,limitTree.GetLeaf("ctW").GetValue(0),limitTree.GetLeaf("ctZ").GetValue(0)) << endl;

        limitTree.GetEntry(bestEntry)
        startValues = []
        for param in scan_params:
            value = limitTree.GetLeaf(param).GetValue(0)
            startValues.append('{}={}'.format(param,value))
        for param in params_tracked:
            value = limitTree.GetLeaf('trackedParam_'+param).GetValue(0)
            startValues.append('{}={}'.format(param,value))
        return ','.join(startValues)

    def getBestValues1DEFT(self, basename, wcs=[]):
        ### Gets values of WCs for grid scan point with best deltaNLL ###
        if not wcs:
            wcs = self.wcs

        startValues = []

        for wc in wcs:
  
            bestDeltaNLL=1000000;
            bestEntry=-1;

            fitFile = '../fit_files/higgsCombine{}.{}.MultiDimFit.root'.format(basename,wc)
            logging.info("Obtaining best value from {}".format(fitFile))

            if not os.path.isfile(fitFile):
                logging.error("fitFile does not exist!")
                sys.exit()
            rootFile = ROOT.TFile.Open(fitFile);
            limitTree = rootFile.Get("limit");

            for entry in range(limitTree.GetEntries()):
                limitTree.GetEntry(entry)
                if(bestDeltaNLL > limitTree.GetLeaf("deltaNLL").GetValue(0)):
                  bestDeltaNLL = limitTree.GetLeaf("deltaNLL").GetValue(0)
                  bestEntry=entry
                  #cout << Form("Entry %i deltaNLL=%f, ctW=%f ctZ=%f",bestEntry,bestDeltaNLL,limitTree.GetLeaf("ctW").GetValue(0),limitTree.GetLeaf("ctZ").GetValue(0)) << endl;

            limitTree.GetEntry(bestEntry)

            value = limitTree.GetLeaf(wc).GetValue(0)
            startValues.append('{}={}'.format(wc,value))

        return ','.join(startValues)


    def retrieveGridScan(self, name='.test', batch='crab', user='apiccine'):#getpass.getuser()):
        ### Retrieves finished grid jobs, extracts, and hadd's into a single file ###
        taskname = name.replace('.','')
        logging.info("Retrieving gridScan files. Task name: "+taskname)

        if batch=='crab':
            # Find crab output files (defaults to user's hadoop directory)
            host = os.uname()[1]
            #if 'lxplus' in host: hadooppath = '/eos/user/{}/{}/EFT/Combine/{}/*/*'.format(os.getlogin()[0], os.getlogin(), taskname)
            if 'lxplus' in host: hadooppath = '/eos/cms/store/user/{}/EFT/Combine/{}/*/*'.format(user, taskname)
            elif 'earth' in host: hadooppath = '/hadoop/store/user/{}/EFT/Combine/{}/*/*'.format(user, taskname)
            else: raise NotImplementedError('The machine ' + host + ' is not configured! Please add its path to `retrieveGridScan`')
            paths = glob.glob(hadooppath)
            paths = [p for p in (chain.from_iterable(os.walk(path) for path in paths))]
            if not paths[0][2]:
                logging.error("No files found in store!")
                sys.exit()

            # Make a temporary folder to hold the extracted root files
            if not os.path.isdir(taskname+'tmp'):
                sp.call(['mkdir',taskname+'tmp'])
            else:
                logging.error("Directory {}tmp/ already exists! Please rename this directory.".format(taskname))
                return

            # Extract the root files
            for tarfiles in paths:
                for tarfile in tarfiles[2]:
                    if tarfile.endswith('.tar'):
                        print(tarfiles[0]+'/'+tarfile)
                        sp.call(['tar', '-xf', tarfiles[0]+'/'+tarfile,'-C', taskname+'tmp'])
            haddargs = ['hadd','-f','../fit_files/higgsCombine'+name+'.MultiDimFit.root']+['{}tmp/{}'.format(taskname,rootfile) for rootfile in os.listdir(taskname+'tmp') if rootfile.endswith('.root')]
            process = sp.Popen(haddargs, stdout=sp.PIPE, stderr=sp.PIPE)
            with process.stdout,process.stderr:
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')
            process.wait()

            # Remove the temporary directory and split root files
            sp.call(['rm','-r',taskname+'tmp'])
            
        elif batch=='condor':
            if not glob.glob('higgsCombine{}.POINTS*.root'.format(name)):
                logging.info("No files to hadd. Returning.")
                return
            #haddargs = ['hadd','-f','higgsCombine'+name+'.MultiDimFit.root']+sorted(glob.glob('higgsCombine{}.POINTS*.root'.format(name)))
            haddargs = ['hadd','-f','-k','../fit_files/higgsCombine'+name+'.MultiDimFit.root']+sorted(glob.glob('higgsCombine{}.POINTS*.root'.format(name)))
            print((['hadd','-f','../../fit_files/higgsCombine'+name+'.MultiDimFit.root']+sorted(glob.glob('higgsCombine{}.POINTS*.root'.format(name)))))
            process = sp.Popen(haddargs, stdout=sp.PIPE, stderr=sp.PIPE)

            with process.stdout,process.stderr:
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')
            process.wait()

            if process.returncode == 0:
                logging.info("hadd successful. Removing POINT files.")
                
                for rootfile in glob.glob('higgsCombine{}.POINTS*.root'.format(name)):
                    os.remove(rootfile)
                if os.path.isfile('condor_{}.sh'.format(name.replace('.',''))):
                    os.rename('condor_{}.sh'.format(name.replace('.','')),'condor{0}/condor_{0}.sh'.format(name))
                if os.path.isfile('condor_{}.sub'.format(name.replace('.',''))):
                    os.rename('condor_{}.sub'.format(name.replace('.','')),'condor{0}/condor_{0}.sub'.format(name))
            else: 
                logging.error("hadd FAILED with code {}. POINT files preserved for manual merging.".format(process.returncode))
                logging.error("Check if '../fit_files/' exists!")

    def submitEFTWilks(self, name='.test', limits='/afs/crc.nd.edu/user/b/byates2/Public/wc_top22006_a24_prof_2sigma.json', workspace='ptz-lj0pt_fullR2_anatest24v01_withAutostats_withSys.root', doBest=False, asimov=False, fixed=False, wc=None, sig=0, batch='condor'):
        '''
        Submit jobs for GoodnessOfFit:
            doBest = False - Fix all NPs to 0, run toys with seed(s) speicfied below
            doBest = True  - Fix all WCs to their best fit values and all NPs to 0
            fixed = True - Compare fixed point (e.g., 2sigma) to best fit point
            sig = -2, 0, 2 - -2 for -2sigma, 0 for best fit, 2 for +2sigma
        '''
        # Update `sig` to access list: `[best, [-2sigma, +2sigma]]`
        if sig not in [-2, 0, 2]:
            raise Exception('Please specifiy 0 for best fit, or +/-2 for +/-2 sigma!')
        if sig == -2:
            sig == 1
        if sig == 2:
            sig == 2
        '''
        with open(limits) as jf:
            limits = json.load(jf)
        best = ','.join(['{}={}'.format(key,val[sig]) for key,val in limits.items()])
        '''
        '''
        if not doBest:
            best = ','.join(['{}={}'.format(key,val[sig]) for key,val in limits.items() if key in self.wcs])
        '''
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['combineTool.py','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/'+workspace,'-M','GoodnessOfFit','--algo','saturated','--cminPreScan','--cminDefaultMinimizerStrategy=0', '--noMCbonly=1']
        if not doBest:
            args = ['combineTool.py','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/'+workspace,'-M','MultiDimFit','--algo', 'none', '--skipInitialFit', '--cminPreScan','--cminDefaultMinimizerStrategy=0']
        if fixed:
            args = ['combineTool.py','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/'+workspace,'-M','MultiDimFit','--algo', 'fixed', '--cminPreScan','--cminDefaultMinimizerStrategy=0']
            args.extend(['-P', wc]) # Preserves constraints
        #args = ['combineTool.py','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/'+workspace,'-M','MultiDimFit','--algo','none','--cminPreScan','--cminDefaultMinimizerStrategy=0']
        '''
        if wc is not None:
            # If a WC is specified, set it to it's requested value, and start all others at 0
            best = ','.join(['{}=0'.format(key) if key != wc else '{}={}'.format(key,limits[wc][sig]) for key,value in limits.items()])
        '''
        if fixed:
            args.extend(['--setParameters', ','.join(['{}=0'.format(key) for key in self.wcs])]) # Set all WCs to their best fit values
            args.extend(['--floatOtherPOIs', '1'])
            if wc is not None:
                wc_ranges = self.wc_ranges_njets
                args.extend(['--setParameterRanges {}={},{}'.format(wc,wc_ranges[wc][0],wc_ranges[wc][1])])
        else:
            args.extend(['--setParameters', best]) # Set all WCs to their best fit values
        args.extend(['-n',name])
        if doBest:
            if wc is not None:
                args.extend(['--freezeParameters', 'rgx{.*}']) # Float all WCs except `wc`
                #args.extend(['--freezeParameters', 'rgx{.*},' + ','.join(['{}={}'.format(key,val) for key,val in limits.items() if key != wc])]) # Float all WCs except `wc`
                #args.extend(['--freezeParameters', 'rgx{.*},' + '{}'.format(wc)]) # Float all WCs except `wc`
                #args.extend(['--freezeParameters', 'rgx{.*},' + ','.join(['{}'.format(w) for w in self.wcs if w != wc]), '--fixedSignalStrength=1']) # Freeze all WCs except `wc` #FIXME
            else:
                args.extend(['--freezeParameters', 'rgx{.*}']) # Freeze all parameters
            #args.extend(['--fixedSignalStrength=1']) # Freeze all parameters
            if asimov:
                args.extend(['-t', '-1']) # 1 toys, default seed `123456`
        else:
            if wc is not None and not fixed:
                args.extend(['--freezeParameters', 'rgx{.*},' + ','.join(['{}'.format(w) for w in self.wcs if w != wc])]) # Freeze all WCs except `wc`
            elif 'noSyst' not in workspace:
                args.extend(['--freezeParameters', 'rgx{.*}']) # Freeze all NPs
            #args.extend(['--freezeParameters', 'rgx{.*}', '--fixedSignalStrength=1']) # Freeze all NPs
            #args.extend(['-t', '1', '-s', '123456', '--saveToys']) # 1 toys, default seed `123456`
            #args.extend(['-t', '1', '-s', '1:100:1', '--saveToys', '--toysNoSystematics']) # 5 toys, vary seed between 1-100
            args.extend(['-t', '100', '-s', '123456:133455:1', '--toysNoSystematics']) # 5 toys, vary seed between 1-100
            #args.extend(['-t', '5', '-s', '1:100:1', '--saveToys', '--toysNoSystematics']) # 5 toys, vary seed between 1-100 FIXME
        if not fixed:
            args.extend(['--fixedSignalStrength=1'])
        args.extend(['--trackParameters',','.join(self.wcs)])

        if batch=='crab':
            args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py'])
            logging.info(' '.join(args))
            # Run the combineTool.py command
            process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
            with process.stdout,process.stderr:
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')
            process.wait()
        elif batch=='condor':
            args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--dry-run'])
            logging.info(' '.join(args))
            if os.path.exists('condor{}'.format(name)):
                logging.error("Directory condor{} already exists!".format(name))
                logging.error("Aborting submission.")
                #return
            sp.call(['mkdir','condor{}'.format(name)])
            sp.call(['chmod','a+x','condor_{}.sh'.format(name.replace('.',''))])
            sp.call(['sed','-i','s/queue/\\n\\nrequestMemory=7000\\n\\nqueue/','condor_{}.sub'.format(name.replace('.',''))]) # Ask for at least 3GB of RAM
            sp.call(['sed','-i','s/cd .*EFTFit.*test/cd \/scratch365\/{}\//'.format(getpass.getuser()),'condor_{}.sh'.format(name.replace('.',''))]) # Run in /scratch365/{user}
            logging.info('Now submitting condor jobs.')
            condorsub = sp.Popen(['condor_submit','-append','initialdir=condor{}'.format(name),'condor_{}.sub'.format(name.replace('.',''))], stdout=sp.PIPE, stderr=sp.PIPE)
            with condorsub.stdout,condorsub.stderr:
                self.log_subprocess_output(condorsub.stdout,'info')
                self.log_subprocess_output(condorsub.stderr,'err')
            condorsub.wait()

    def submitEFTWilksWC(self, name='.012023.Wilks.NP', wc='ctp', batch='condor', workspace='EFTWorkspace.root'):
        wcs=['cQq81', 'ctq8', 'ctG', 'ctp', 'cpQM', 'cpt'] #TOP-22-00 linear dominant terms
        for wc in wcs:
            self.submitEFTWilks(name+'.'+wc, wc=wc, sig=0, doBest=False, fixed=True, workspace=workspace, batch=batch)
        #print('Submitting +/-2 sigma s:seaturated tests for {}'.format(wc))
        #self.submitEFTWilks(name+'.'+wc+'-2sigma', wc=wc, sig=-2, doBest=True)
        #self.submitEFTWilks(name+'.'+wc+'+2sigma', wc=wc, sig=+2, doBest=True)

    def getEFTBestFit(self, name, asimov=False):
        best_fit = 170
        fin = 'higgsCombine{}.GoodnessOfFit.mH120.root'.format(name)
        if asimov:
            fin = 'higgsCombine{}.Asimov.BestFit.GoodnessOfFit.mH120.root'.format(name)
        print(('Opening {}'.format(fin)))
        fit_file = ROOT.TFile.Open(fin)
        limit_tree = fit_file.Get('limit')
        best_fit = limit_tree.GetMinimum('limit')
        fit_file.Close()
        return best_fit

    def getEFTNLL(self, name, asimov=False):
        fin = 'higgsCombine{}.BestFit.MultiDimFit.mH120.root'.format(name)
        if asimov:
            fin = 'higgsCombine{}.Asimov.BestFit.MultiDimFit.mH120.root'.format(name)
        print(('Opening {}'.format(fin)))
        with uproot.open(fin) as limit_tree:
            limits = limit_tree['limit']['deltaNLL'].array()
            mask = limit_tree['limit']['quantileExpected'].array() >= 0
            limits = limits[mask]
            nll_fit = 2 * np.min(limits[limits>1])
        return nll_fit

    def computeEFTWilks(self, name='.122022.Wilks', asimov=False):
        best_fit = self.getEFTBestFit(name=name, asimov=asimov)
        self.drawEFTWilks(name, best_fit, best_fit, dof=178, asimov=asimov)
        #self.drawEFTWilks(name, best_fit, best_fit, nll_fit, dof=178, asimov=asimov)

    def drawEFTWilks(self, name, best_fit, alt_fit, nll_fit=0, dof=1, asimov=False):
        if not glob.glob('higgsCombine{}.GoodnessOfFit.mH120*.root'.format(name)):
            logging.info("No files to hadd. Returning.")
        elif not os.path.exists('../fit_files/higgsCombine'+name+'.GoodnessOfFit.root'):
            haddargs = ['hadd','-f','-k','../fit_files/higgsCombine'+name+'.GoodnessOfFit.root']+sorted(glob.glob('higgsCombine{}.GoodnessOfFit.mH120*.root'.format(name)))
            process = sp.Popen(haddargs, stdout=sp.PIPE, stderr=sp.PIPE)
            with process.stdout,process.stderr:
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')
            process.wait()
        fin = '../fit_files/higgsCombine{}.GoodnessOfFit.root'.format(name)
        with uproot.open(fin) as limit_tree:
            print(('Opening {}'.format(fin)))
            limits = limit_tree['limit']['limit'].array()
            mask = limit_tree['limit']['quantileExpected'].array() > -2
            limits = limits[mask]
            alt_limits = np.min(limits[limits>1])
            alt_limits = np.min(limits)
            print('\n\n', 'AlternativeFit =', alt_fit, 'BestFit =', best_fit)
            print('\n\nP({}>test statistic)='.format(alt_fit) + str(limits[limits > alt_fit].size/float(limits.size)) + '\n')
            '''
            >>> scipy.stats.chi2.ppf(.68, 1)
            0.988946481478023
            >>> scipy.stats.chi2.cdf(4, 1)
            0.9544997361036415
            '''
            prob = chi2.cdf(alt_fit - best_fit, 1)
            target = 4
            print('P({}-{}={}, {})={}'.format(alt_fit, best_fit, alt_fit - best_fit, dof, prob))
            if prob < target:
                print('\tPossible UNDER coverage!')
            else:
                print('\tPossible OVER coverage!')
            print('\tTarget is P({}, {})={}'.format(target, dof, chi2.cdf(target, dof)))
            #print('P({}-{}={}, 26)={}'.format(alt_limits, best_fit, alt_limits - best_fit, chi2.cdf(alt_limits - best_fit, 26)))

        ROOT.gROOT.SetBatch(True)
        ROOT.gStyle.SetOptStat(0)
        hname = '{}.GoodnessOfFit'.format(name)
        if asimov:
            hname = hname.replace('Goodness','Asimov.Goodness')
        fit_file = ROOT.TFile.Open('../fit_files/higgsCombine{}.GoodnessOfFit.root'.format(name))
        limit_tree = fit_file.Get('limit')
        canvas = ROOT.TCanvas('c','c',800,800)
        canvas.cd()
        limit_tree.Draw('limit>>hist', 'quantileExpected>-2')
        h = canvas.GetPrimitive("hist")
        line = ROOT.TLine(best_fit, 0, best_fit, 10)
        line.SetLineStyle(9)
        line.Draw("same")
        arrow = ROOT.TArrow(best_fit, 5, best_fit+5, 5, 5, '>')
        #arrow.Draw("same")
        h.SetName(hname)
        h.SetTitle("")
        canvas.Print(hname+'.png','png')
        canvas.Print(hname+'.eps','eps')
        os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop c{}.eps c{}.pdf'.format(hname,hname))
        fit_file.Close()

    def computeEFTWilksWC(self, name='.012023.Wilks.NP', wc='ctp', asimov=False):
        best_fit = self.getEFTBestFit(name=name, asimov=asimov)
        sigma_fit = self.getEFTBestFit(name='{}.{}-2sigma'.format(name, wc), asimov=asimov)
        self.drawEFTWilks(name, best_fit, sigma_fit, dof=1, asimov=asimov)

    def getInterval(fin='', wc=[]):
        rootFile = ROOT.TFile.Open(fin)
        limitTree = rootFile.Get('limit')
        graphwcs = []
        graphnlls = []

        # Get coordinates for TGraph
        for entry in range(limitTree.GetEntries()):
            limitTree.GetEntry(entry)
            graphwcs.append(limitTree.GetLeaf(wc).GetValue(0))
            graphnlls.append(2*limitTree.GetLeaf('deltaNLL').GetValue(0))

        rootFile.Close()

        return (graphwcs, graphnlls)

    def batch1DScanEFT(self, basename='.test', batch='crab', freeze=False, scan_wcs=[], points=300, other=[], mask=[], mask_syst=[], workspace='workspace.root', ignore=[], wc_ranges=None, wc_val=None):
        ### For each wc, run a 1D deltaNLL Scan.
        if not scan_wcs:
            scan_wcs = self.wcs

        # Set the WC ranges if not specified
        if wc_ranges is None: wc_ranges = self.wc_ranges

        zero_ignore = []
        freeze_ignore = []
        if len(ignore)>0:
            zero_ignore = ['--setParameters ' + ','.join(['{}=0'.format(wc) for wc in ignore])]
            freeze_ignore = ['--freezeParameters ' + ','.join(['{}'.format(wc) for wc in ignore])]
            for iwc in ignore:
                if iwc in scan_wcs: scan_wcs.remove(iwc)
                
        if wc_val is None:
            params = ','.join(['{}=0'.format(wc) for wc in self.wcs])
        else:
            params = ','.join(['{}=0'.format(wc) if wc not in wc_val.keys() else '{}={}'.format(wc, wc_val[wc]) for wc in self.wcs])
        for wc in scan_wcs:
            if isinstance(mask, list) and len(mask)==1:
                masks = mask[0]
            else:
                masks = ','.join(mask)
            mask = []
            self.gridScan('{}.{}'.format(basename,wc), batch, freeze, [wc], [wcs for wcs in self.wcs if wcs != wc], points, ['--setParameterRanges {}={},{}'.format(wc,wc_ranges[wc][0],wc_ranges[wc][1])]+zero_ignore+freeze_ignore+other+['--setParameters', params+','+masks], mask, mask_syst, workspace)

    '''
    example: `fitter.batch2DScanEFT('.test.ctZ', batch='crab', wcs=['ctZ'], workspace='wps_njet_runII.root')`
    example: `fitter.batch2DScanEFT('.test.ctZ', batch='crab', wcs='ctZ', workspace='wps_njet_runII.root')`
    '''

    def batch2DScanEFT(self, basename='.EFT.2DgridScan', batch='condor', freeze=False, points=90000, allPairs=False, other=[], mask=[], mask_syst=[], wcs=[], workspace='workspace.root', differential=None):
        ### For pairs of wcs, runs deltaNLL Scan in two wcs using CRAB or Condor ###
        if differential is None:
            differential = 'njets' not in workspace
            print('Assuming')
            print('njets' if not differential else 'differential')
            print('based on the workspace.\nTo force differential or njets set `differential=True/False` respectively.')
        wc_ranges = self.wc_ranges_differential if differential else self.wc_ranges_njets

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs

            params = ','.join(['{}=0'.format(wc) for wc in scan_wcs])
            for wcs in itertools.combinations(scan_wcs,2):
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print(pois, wcs_tracked)
                self.gridScan(name='{}.{}{}'.format(basename,wcs[0],wcs[1]), batch=batch, freeze=freeze, scan_params=list(wcs), params_tracked=wcs_tracked, points=points, other=['--setParameterRanges {}={},{}:{}={},{}'.format(wcs[0],wc_ranges[wcs[0]][0],wc_ranges[wcs[0]][1],wcs[1],wc_ranges[wcs[1]][0],wc_ranges[wcs[1]][1])]+other+['--setParameters', params], mask=mask, mask_syst=mask_syst, workspace=workspace)

        # Use each wc only once
        if not allPairs:
            #pairs from AN
            # scan_wcs = [('ctp', 'cpt'), ('ctZ', 'ctW'), ('ctG', 'cpQM'), ('cptb', 'cQl3i'), ('cpQ3', 'cbW'), ('cQlMi', 'cQei')] # From TOP-19-001
            # Pairs from `ptz-lj0pt_fullR2_anatest10v01_withSys.root` where abs(correlation) > 0.4
            # scan_wcs = [('cQQ1', 'cQt8'), ('cQQ1', 'cQt1'), ('cQt1', 'ctt1'), ('cQt1', 'cQt8'), ('cpQM', 'cpt'), ('ctG', 'ctp'), ('ctW', 'ctZ')]
            scan_wcs = [('ctj1', 'ctj8')]
            if len(wcs) > 0:
                scan_wcs = []
                if isinstance(wcs, str): wcs = [wcs]
                for wc in wcs:
                    if isinstance(wc, tuple): scan_wcs.append(wc)
                    else: scan_wcs = scan_wcs + [(wc, other_wc) for other_wc in self.wcs if wc != other_wc]

            params = ','.join(['{}=0'.format(wc) for wc in self.wcs])
            # params = ','.join(['{}=0'.format(w) for wc in scan_wcs for w in wc])
            for wcs in scan_wcs:
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print(scan_wcs, wcs_tracked)
                self.gridScan(name='{}.{}{}'.format(basename,wcs[0],wcs[1]), batch=batch, freeze=freeze, scan_params=list(wcs), params_tracked=wcs_tracked, points=points, other=['--setParameterRanges {}={},{}:{}={},{}'.format(wcs[0],wc_ranges[wcs[0]][0],wc_ranges[wcs[0]][1],wcs[1],wc_ranges[wcs[1]][0],wc_ranges[wcs[1]][1])]+other+['--setParameters', params], mask=mask, mask_syst=mask_syst, workspace=workspace)

    def batch3DScanEFT(self, basename='.EFT.gridScan', batch='crab', freeze=False, points=27000000, allPairs=False, other=[], wc_triplet=[], mask=[], mask_syst=[]):
        ### For pairs of wcs, runs deltaNLL Scan in two wcs using CRAB or Condor ###

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs

            for wcs in itertools.combinations(scan_wcs,2):
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print(pois, wcs_tracked)
                self.gridScan(name='{}.{}{}{}'.format(basename,wcs[0],wcs[1],wcs[2]), batch=batch, freeze=freeze, scan_params=list(wcs), params_tracked=wcs_tracked, points=points, other=other, mask=mask, mask_syst=mask_syst, workspace=workspace)

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('ctZ','ctp','cpt')]
            if len(wc_triplet)>0: scan_wcs = wc_triplet

            for wcs in scan_wcs:
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print(pois, wcs_tracked)
                self.gridScan(name='{}.{}{}{}'.format(basename,wcs[0],wcs[1],wcs[2]), batch=batch, freeze=freeze, scan_params=list(wcs), params_tracked=wcs_tracked, points=points, other=other, mask=mask, mask_syst=mask_syst, workspace=workspace)

    def batchResubmit1DScansEFT(self, basename='.EFT.gridScan', scan_wcs=[]):
        ### For each wc, attempt to resubmit failed CRAB jobs ###
        if not scan_wcs:
            scan_wcs = self.wcs

        for wc in scan_wcs:
            process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+wc], stdout=sp.PIPE, stderr=sp.PIPE)
            with process.stdout,process.stderr:
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')
            process.wait()

    def batchResubmit2DScansEFT(self, basename='.EFT.gridScan', allPairs=False):
        ### For pairs of wcs, attempt to resubmit failed CRAB jobs ###

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs

            for wcs in itertools.combinations(scan_wcs,2):
                process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+wcs[0]+wcs[1]], stdout=sp.PIPE, stderr=sp.PIPE)
                with process.stdout,process.stderr:
                    self.log_subprocess_output(process.stdout,'info')
                    self.log_subprocess_output(process.stderr,'err')
                process.wait()

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('cQlMi','cQei'),('cpQ3','cbW'),('cptb','cQl3i'),('ctG','cpQM'),('ctZ','ctW'),('ctei','ctlTi'),('ctlSi','ctli'),('ctp','cpt')]

            for wcs in scan_wcs:
                process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+wcs[0]+wcs[1]], stdout=sp.PIPE, stderr=sp.PIPE)
                with process.stdout,process.stderr:
                    self.log_subprocess_output(process.stdout,'info')
                    self.log_subprocess_output(process.stderr,'err')
                process.wait()

    def batchRetrieve1DScansEFT(self, basename='.test', batch='crab', scan_wcs=[]):
        ### For each wc, retrieves finished 1D deltaNLL grid jobs, extracts, and hadd's into a single file ###
        if not scan_wcs:
            scan_wcs = self.wcs

        for wc in scan_wcs:
            self.retrieveGridScan('{}.{}'.format(basename,wc),batch)

    def batchRetrieve2DScansEFT(self, basename='.EFT.gridScan', batch='crab', allPairs=False, wcs=[]):
        ### For pairs of wcs, retrieves finished grid jobs, extracts, and hadd's into a single file ###
        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs
            for wcs in itertools.combinations(scan_wcs,2):
                self.retrieveGridScan('{}.{}{}'.format(basename,wcs[0],wcs[1]),batch)

        # Use each wc only once
        if not allPairs:
            #pairs from AN
            # scan_wcs = [('ctp', 'cpt'), ('ctZ', 'ctW'), ('ctG', 'cpQM'), ('cptb', 'cQl3i'), ('cpQ3', 'cbW'), ('cQlMi', 'cQei')] # From TOP-19-001
            # Pairs from `ptz-lj0pt_fullR2_anatest10v01_withSys.root` where abs(correlation) > 0.4
            # scan_wcs = [('cpt', 'cpQM'), ('ctlSi', 'ctlTi'), ('cQlMi', 'ctei'), ('cbW', 'cpQ3'), ('cQq81', 'cbW'), ('cbW', 'cptb'), ('cptb', 'cpQ3'), ('cQt1', 'ctt1'), ('ctp', 'ctG'), ('cQq81', 'cpQ3')]
            # scan_wcs = [('cQQ1', 'ctt1'), ('cQt8', 'ctt1'), ('cQQ1', 'ctp'), ('cQt8', 'ctp'), ('cpQM', 'cpQ3')]
            scan_wcs = [('ctj1', 'ctj8')]
            if len(wcs) > 0:
                scan_wcs = []
                if isinstance(wcs, str): wcs = [wcs]
                for wc in wcs:
                    if isinstance(wc, tuple): scan_wcs.append(wc)
                    else: scan_wcs = scan_wcs + [(wc, other_wc) for other_wc in self.wcs if wc != other_wc]
            for wcs in scan_wcs:
                print(wcs)
                print('{}.{}{}'.format(basename,wcs[0],wcs[1]), batch)
                self.retrieveGridScan('{}.{}{}'.format(basename,wcs[0],wcs[1]),batch)
                
    def reductionFitEFT(self, name='.EFT.Private.Unblinded.Nov16.28redo.Float.cptcpQM', wc='cpt', final=True, from_wcs=[], alreadyRun=True):
        ### Extract a 1D scan from a higher-dimension scan to avoid discontinuities ###
        if not wc:
            logging.error("No WC specified!")
            return
        if final and not alreadyRun:
            os.system('hadd -f higgsCombine{}.MultiDimFit.mH120.root higgsCombine{}.POINTS*.{}reduced.MultiDimFit.root '.format(name,name,''.join(from_wcs)))
        if alreadyRun and not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
            return
        elif not alreadyRun and not os.path.exists('higgsCombine{}.MultiDimFit.mH120.root'.format(name)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
            return

        rootFile = []
        if alreadyRun:
            rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        else: rootFile = ROOT.TFile.Open('higgsCombine{}.MultiDimFit.mH120.root'.format(name))
        limitTree = rootFile.Get('limit')

        # First loop through entries and get deltaNLL list for each value of the WC
        wc_dict = defaultdict(list)
        for entry in range(limitTree.GetEntries()):
            limitTree.GetEntry(entry)
            wc_dict[limitTree.GetLeaf(wc).GetValue(0)].append(limitTree.GetLeaf('deltaNLL').GetValue(0))
        rootFile.Close()
        
        # Next pick the best deltaNLL for each WC value
        wc_dict_reduced = {}
        for key in wc_dict:
            wc_dict_reduced[key] = min(wc_dict[key])
            
        # Now make a new .root file with the new TTree
        # Only the WC and deltaNLL will be branches
        # These can be directly used by EFTPlotter
        outFile = []
        if final:
            outFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.{}reduced.MultiDimFit.root'.format(name,wc),'RECREATE')
        else:
            outFile = ROOT.TFile.Open('higgsCombine{}.{}reduced.MultiDimFit.root'.format(name,wc),'RECREATE')
        outTree = ROOT.TTree('limit','limit')
        
        wc_branch = array.array('f',[0.])
        deltaNLL_branch = array.array('f',[0.])
        outTree.Branch(wc,wc_branch,wc+'/F')
        outTree.Branch('deltaNLL',deltaNLL_branch,'deltaNLL/F')
        
        # Fill the branches
        for event in range(len(list(wc_dict_reduced.keys()))):
            wc_branch[0] = list(wc_dict_reduced.keys())[event]
            deltaNLL_branch[0] = list(wc_dict_reduced.values())[event]
            outTree.Fill()
            
        # Write the file
        outFile.Write()

    def reduction2DFitEFT(self, name='.EFT.Private.Unblinded.Nov16.28redo.Float.cptcpQM', wcs=['cpt','ctp'], final=True):
        ### Extract a 2D scan from a higher-dimension scan to avoid discontinuities ###
        if not wcs:
            logging.error("No WC specified!")
            return
        if final:
            os.system('hadd -f higgsCombine{}.MultiDimFit.mH120.root higgsCombine{}.POINTS*.{}reduced.MultiDimFit.root '.format(name,name,''.join(wcs)))
        if not os.path.exists('higgsCombine{}.MultiDimFit.mH120.root'.format(name)):
        #if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
            return

        rootFile = []
        rootFile = ROOT.TFile.Open('higgsCombine{}.MultiDimFit.mH120.root'.format(name))
        #rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        limitTree = rootFile.Get('limit')

        # First loop through entries and get deltaNLL list for each value of the WC
        wc_dict = defaultdict(list)
        for entry in range(limitTree.GetEntries()):
            limitTree.GetEntry(entry)
            wc_dict[limitTree.GetLeaf(wcs[0]).GetValue(0),limitTree.GetLeaf(wcs[1]).GetValue(0)].append(limitTree.GetLeaf('deltaNLL').GetValue(0))
        rootFile.Close()
        
        # Next pick the best deltaNLL for each WC value
        wc_dict_reduced = {}
        for key in wc_dict:
            wc_dict_reduced[key] = min(wc_dict[key])
            
        # Now make a new .root file with the new TTree
        # Only the WC and deltaNLL will be branches
        # These can be directly used by EFTPlotter
        outFile = []
        if final:
            outFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.{}reduced.MultiDimFit.root'.format(name,''.join(wcs)),'RECREATE')
        else:
            outFile = ROOT.TFile.Open('higgsCombine{}.{}{}reduced.MultiDimFit.root'.format(name,wcs[0],wcs[1]),'RECREATE')
        outTree = ROOT.TTree('limit','limit')
        
        wc_branch1 = array.array('f',[0.])
        wc_branch2 = array.array('f',[0.])
        deltaNLL_branch = array.array('f',[0.])
        outTree.Branch(wcs[0],wc_branch1,wcs[0]+'/F')
        outTree.Branch(wcs[1],wc_branch2,wcs[1]+'/F')
        outTree.Branch('deltaNLL',deltaNLL_branch,'deltaNLL/F')
        
        # Fill the branches
        for wc1,wc2 in wc_dict_reduced:
            wc_branch1[0] = wc1
            wc_branch2[0] = wc2
            deltaNLL_branch[0] = wc_dict_reduced[(wc1,wc2)]
            outTree.Fill()
            
        # Write the file
        outFile.Write()

    def batchReductionFitEFT(self, name='.EFT.Private.Unblinded.Nov16.28redo.Float.cptcpQM', wc=['cpt'], points=27000000, split=30000):
        JOB_PREFIX = """#!/bin/sh
        ulimit -s unlimited
        set -e
        cd %(CMSSW_BASE)s/src
        export SCRAM_ARCH=%(SCRAM_ARCH)s
        eval `scramv1 runtime -sh`
        cd %(PWD)s
        """ % ({
            'CMSSW_BASE': os.environ['CMSSW_BASE'],
            'SCRAM_ARCH': os.environ['SCRAM_ARCH'],
            'PWD': os.environ['PWD']
        })
        
        CONDOR_TEMPLATE = """executable = %(EXE)s
        arguments = $(ProcId)
        output                = condor_%(TASK)s/%(TASK)s.$(ClusterId).$(ProcId).out
        error                 = condor_%(TASK)s/%(TASK)s.$(ClusterId).$(ProcId).err
        log                   = condor_%(TASK)s/%(TASK)s.$(ClusterId).log
        
        # Send the job to Held state on failure.
        on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)
        
        # Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.
        periodic_release =  (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > 600)
        
        queue %(NUMBER)s
        
        """
        #%(EXTRA)s
        
        fname = '{}.{}'.format(name,''.join(wc))
        script_name = fname+'.sh'
        logname = script_name.replace('.sh', '.log')
        with open(fname, "w") as text_file:
            text_file.write(JOB_PREFIX)
            #for i, command in enumerate(commands):
                #tee = 'tee' if i == 0 else 'tee -a'
                #log_part = '\n'
                #if do_log: log_part = ' 2>&1 | %s ' % tee + logname + log_part
                #if command.startswith('combine') or command.startswith('pushd'):
                    #text_file.write(
                        #self.pre_cmd + 'eval ' + command + log_part)
                #else:
                    #text_file.write(command)
        st = os.stat(fname)
        os.chmod(fname, st.st_mode | stat.S_IEXEC)
        # print(JOB_PREFIX + command)
        print('Created job script: %s' % fname)

        outscriptname = 'condor_%s.sh' % fname
        subfilename = 'condor_%s.sub' % fname
        print('>> condor job script will be %s' % outscriptname)
        outscript = open(outscriptname, "w")
        outscript.write(JOB_PREFIX)
        jobs = 0
        wsp_files = set()

        cmssw_base = os.getenv('CMSSW_BASE')
        script_dir = os.path.join(cmssw_base, 'src', 'EFTFit', 'Fitter', 'scripts')
        
        #for i, proc in enumerate(range(0, points, split), points // split):
        for i,proc in enumerate(list(range(0,points,split)), points/split):
            outscript.write('\nif [ $1 -eq %i ]; then\n' % jobs)
            outscript.write('python {}/reduce.py %d %d %s %s\n'.format(script_dir) % (proc, proc+split-1, name, ' '.join(wc)))
            jobs += 1
            outscript.write('fi')

        # Uncommented block with additional logic (left for reference)
        # for i, j in enumerate(range(0, len(self.job_queue), self.merge)):
        #     outscript.write('\nif [ $1 -eq %i ]; then\n' % jobs)
        #     jobs += 1
        #     for line in self.job_queue[j:j + self.merge]:
        #         newline = line
        #         outscript.write('  ' + newline + '\n')
        #     outscript.write('fi')
        
        outscript.close()
        st = os.stat(outscriptname)
        os.chmod(outscriptname, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        subfile = open(subfilename, "w")
        condor_settings = CONDOR_TEMPLATE % {
          'EXE': outscriptname,
          'TASK': ''.join(fname.split('.')),
          #'EXTRA': self.bopts.decode('string_escape'),
          #'NAME': name,
          #'WC': ' '.join(wc),
          'NUMBER': jobs
        }
        subfile.write(condor_settings)
        subfile.close()
        if not os.path.exists('condor_{}'.format(''.join(fname.split('.')))):
            os.system('mkdir condor_{}'.format(''.join(fname.split('.'))))
        #run_command(self.dry_run, 'condor_submit %s' % (subfilename))
        return os.system('condor_submit %s' % (subfilename))

    #def batchReductionFitEFT(self, name='.EFT.Private.Unblinded.Nov16.28redo.Float.cptcpQM', wc='cpt', points=27000000, split=40000):
        #for i in range(0,points,split):
            #self.submitBatchReductionFitEFT('{}.POINTS.{}.{}'.format(name, i, i+split), wc, points, split)
        
    def batch1DBestFitEFT(self, basename='.EFT.SM.Float', wcs=[]):
        ### For each wc, run a 1D fit with others frozen. Use start point from 1D scan with other floating. ###
        if not wcs:
            wcs = self.wcs

        for wc in wcs:
            logging.info("Fitting for wc {}.".format(wc))
            start_point = self.getBestValues1DEFT(basename,[wc])
            logging.info("Start value: {}".format(start_point))
            self.bestFit('{}.BestFit.{}'.format(basename,wc), [wc], start_point, True)

    def batchRetrieve3DScansEFT(self, basename='.EFT.gridScan', batch='crab', allPairs=False, wc_triplet=[]):
        ### For pairs of wcs, retrieves finished grid jobs, extracts, and hadd's into a single file ###

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs
            for wcs in itertools.combinations(scan_wcs,2):
                self.retrieveGridScan('{}.{}{}'.format(basename,wcs[0],wcs[1]),batch)

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
            if len(wc_triplet)>0: scan_wcs = wc_triplet
            for wcs in scan_wcs:
                self.retrieveGridScan('{}.{}{}{}'.format(basename,wcs[0],wcs[1],wcs[2]),batch)
            
    def batch2DBestFitEFT(self, basenamegrid='.EFT.gridScan', basenamefit='.EFT.gridScan', wcs_POI=[], freeze=False):
        ### For each combination of wcs, do a best fit using the new start point ###
        if not wcs_POI:
            wcs_POI = self.wcs

        for pois in itertools.combinations(wcs_POI,2):
            wcs_tracked = [wc for wc in self.wcs if wc not in pois]
            startValuesString = self.getBestValues2D(name='{}.{}{}'.format(basenamegrid,pois[0],pois[1]), scan_params=pois, params_tracked=wcs_tracked)
            self.bestFit(name='{}.{}{}'.format(basenamefit,pois[0],pois[1]), params_POI=pois, startValuesString=startValuesString, freeze=freeze)

    def compareFitsEFT(self,basename='.EFT.SM.Float'):
        ### Compare results of different 1D EFT scans ###
        tfiles = {}
        limits = {}
        bestFits = {} # Nested dict; bestFit of key1 according to key2
        # First get all scan files
        for wc in self.wcs:
            tfiles[wc] = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(basename+'.'+wc))
            limits[wc] = tfiles[wc].Get('limit')
            bestFits[wc] = {}
        # Get best fits
        for poiwc in self.wcs:
            limit = limits[poiwc]
            # First get POI best fit
            bestNLL = (-1,1000000)
            for entry in range(limit.GetEntries()):
                limit.GetEntry(entry)
                currentNLL = limit.GetLeaf('deltaNLL').GetValue(0)
                if bestNLL[1] > currentNLL: bestNLL = (entry,currentNLL)
            print("Best entry for {} is {}.".format(poiwc,bestNLL[0]))
            limit.GetEntry(bestNLL[0])
            bestFits[poiwc][poiwc] = limit.GetLeaf(poiwc).GetValue(0)
            # Second get corresponding fits for the other wcs
            trackedwcs = list(self.wcs)
            trackedwcs.remove(poiwc)
            for trackedwc in trackedwcs:
                bestFits[trackedwc][poiwc] = limit.GetLeaf('trackedParam_'+wc).GetValue(0)

        # Print full set of results
        for poiwc in self.wcs:
            trackedwcs = list(self.wcs)
            trackedwcs.remove(poiwc)
            print(("Best value of {}: {}".format(poiwc,bestFits[poiwc][poiwc])))
            for trackedwc in trackedwcs:
                print(("Value according to {}: {}".format(trackedwc,bestFits[poiwc][trackedwc])))
            
    def printBestFitsSM(self, name='.EFT.SM.Float'):
        ### Print(a table of SM signal strengths, their best fits, and their uncertainties ###
        params = ['mu_ttll','mu_ttlnu','mu_ttH','mu_tllq']

        fit_array = []

        logging.info("Obtaining result of fit: multidimfit{}.root".format(name))
        fit_file = ROOT.TFile.Open('../fit_files/multidimfit{}.root'.format(name))
        fit = fit_file.Get('fit_mdf')

        for param in params:
            roorealvar = fit.floatParsFinal().find(param)
            if not roorealvar: continue

            value = round(roorealvar.getVal(),2)
            err_sym =  round(roorealvar.getError(),2)
            err_low = round(roorealvar.getErrorLo(),2)
            err_high = round(roorealvar.getErrorHi(),2)

            fit_array.append((param,value,err_sym,err_low,err_high))

        logging.info("Quick result:")
        logging.info("Param, Best Fit Value, Symmetric Error, Low side of Asym Error, High side of Asym Error")
        for row in fit_array:
            print(row[0],row[1],"+/-",row[2]," ",row[3],"+{}".format(row[4]))
            logging.debug("{} {} +/- {}".format(row[0],row[1],row[2]))

    def printBestFitsEFT(self, basename='.EFT.SM.Float', wcs=[], simultaneous=True):
        ### Print a table of wcs, their best fits, and their uncertainties ###
        if not wcs:
            wcs = self.wcs

        fit_array = []

        if simultaneous:
            logging.info("Obtaining result of fit: multidimfit{}.root".format(basename))
            fit_file = ROOT.TFile.Open('../fit_files/multidimfit{}.root'.format(basename))
            fit = fit_file.Get('fit_mdf')

            for wc in wcs:
                roorealvar = fit.floatParsFinal().find(wc)

                value = round(roorealvar.getVal(),6)
                err_sym =  round(roorealvar.getError(),6)
                err_low = round(roorealvar.getErrorLo(),6)
                err_high = round(roorealvar.getErrorHi(),6)

                fit_array.append((wc,value,err_sym,err_low,err_high))
        else:
            for wc in wcs:
                logging.info("Obtaining result of fit: multidimfit{}.{}.root".format(basename,wc))
                fit_file = ROOT.TFile.Open('../fit_files/multidimfit{}.{}.root'.format(basename,wc))
                fit = fit_file.Get('fit_mdf')

                roorealvar = fit.floatParsFinal().find(wc)

                value = round(roorealvar.getVal(),6)
                err_sym =  round(roorealvar.getError(),6)
                err_low = round(roorealvar.getErrorLo(),6)
                err_high = round(roorealvar.getErrorHi(),6)

                fit_array.append((wc,value,err_sym,err_low,err_high))

        logging.info("Quick result:")
        for row in fit_array:
            print(row[0],"+/-",row[1])
            logging.debug(row[0],"+/-",row[1])
        logging.info("WC, Best Fit Value, Symmetric Error, Low side of Asym Error, High side of Asym Error")
        for row in fit_array:
            print(', '.join([str(ele) for ele in row]))
            logging.debug(row)

    def printIntervalFitsEFT(self, basename='.EFT.SM.Float', wcs=[], wc_ranges=None):
        ### Print a table of wcs, their best fits, and their uncertainties ###
        ### Use 1D scans instead of regular MultiDimFit ###
        if not wcs:
            wcs = self.wcs

        # Set the WC ranges if none are specified
        if wc_ranges is None: wc_ranges = self.wc_ranges_njets

        ROOT.gROOT.SetBatch(True)

        fit_array = []

        canvas = ROOT.TCanvas()
        for wc in wcs:

            canvas.Clear()

            logging.debug("Obtaining result of scan: higgsCombine{}.{}.MultiDimFit.root".format(basename,wc))
            fit_file = ROOT.TFile.Open('../fit_files/higgsCombine{}.{}.MultiDimFit.root'.format(basename,wc))
            limit_tree = fit_file.Get('limit')

            limit_tree.Draw('2*deltaNLL:{}>>{}1DNLL(50,{},{})'.format(wc,wc,wc_ranges[wc][0],wc_ranges[wc][1]),'2*deltaNLL>-1','same')
            graph = canvas.GetPrimitive('Graph')
            #graph.SetName("Graph")

            graph.Sort()

            lowedges=[]
            highedges=[]
            minimums=[]
            true_minimums=[]
            best = [-1000,1000]
            prev = 1000
            for idx in range(graph.GetN()):
                y_val = graph.GetY()[idx]
                if prev>4 and 4>y_val:
                    lowedges.append((graph.GetX()[idx-1]+graph.GetX()[idx+1])/2)
                if prev<4 and 4<y_val:
                    highedges.append((graph.GetX()[idx-1]+graph.GetX()[idx+1])/2)
                if y_val < best[1]:
                    best = [graph.GetX()[idx],y_val]
                if y_val<prev and y_val<graph.GetY()[idx+1]:
                    minimums.append((graph.GetX()[idx],y_val))
                prev = y_val
            if not len(lowedges) == len(highedges):
                logging.error("Something is strange! Interval is missing endpoint!")

            def sortkey(elem):
                return elem[1]

            for interval in zip(lowedges,highedges):
                true_min = [-1000,1000]
                for minimum in minimums:
                    if minimum[1]<true_min[1] and interval[0]<minimum[0] and minimum[0]<interval[1]:
                        true_min = minimum
                true_minimums.append(true_min[0])

            fit_array.append([wc,[list(l) for l in zip(true_minimums,lowedges,highedges)]])

        for line in fit_array:
            print(line)    

    def ImpactSetup(self, workspace='workspace.root', unblind=False):

        workspace_abs = os.path.abspath(workspace)
        cmssw_base = os.getenv('CMSSW_BASE')
        test_dir = os.getcwd()
        # test_dir = os.path.join(cmssw_base, 'src', 'EFTFit', 'Fitter', 'test')

        job_dir_name = 'asimov'
        if unblind: job_dir_name = 'unblind'

        target_dir = os.path.join(test_dir, job_dir_name)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        link_target = os.path.join(target_dir, workspace)
        if not os.path.exists(link_target):
            os.symlink(workspace_abs, link_target)

        return target_dir, job_dir_name, cmssw_base, test_dir


    def Impact_sh_preamble(self, cmssw_base, target_dir):
        preamble = (
            "#!/bin/sh\n"
            "ulimit -s unlimited\n"
            "unset PERL5LIB\n"
            "set -e\n"
            f"cd {cmssw_base}/src\n"
            f"export SCRAM_ARCH={os.environ['SCRAM_ARCH']}\n"
            "eval `scramv1 runtime -sh`\n"
            f"cd {target_dir}\n\n"
        )

        return preamble


    def Impact_condorsub(self, wc, executable_path):
        condorsub_text = (
            f"executable = {executable_path}\n"
            f"arguments = $(ProcId)\n"
            f"output                = {wc}.$(ClusterId).$(ProcId).out\n"
            f"error                 = {wc}.$(ClusterId).$(ProcId).err\n"
            f"log                   = {wc}.$(ClusterId).log\n\n"
            f"# Send the job to Held state on failure.\n"
            f"on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)\n\n"
            f"# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.\n"
            f"periodic_release =  (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > 600)\n"
            f"\n"
        )

        return condorsub_text 


    def ImpactInitialFit(self, workspace='workspace.root', wcs=[], unblind=False, version=''):

        target_dir, job_dir_name, cmssw_base, test_dir = self.ImpactSetup(workspace, unblind)

        if not wcs: wcs = self.wcs
        wcs_start = ','.join(wc+'=0' for wc in self.wcs)
        for wc in wcs:
            wcs_range = []
            for name, r in self.wc_ranges.items(): 
                wcs_range.append(f"{name}={r[0]},{r[1]}")
            range_str = ":".join(wcs_range)
            freeze = ','.join([w for w in self.wcs if w != wc])
            freeze_cmd = f"--freezeParameters {freeze}" if freeze else ""

            combine_cmd = (
                f"combineTool.py -M Impacts -n {wc}{version} --doInitialFit "
                f"--redefineSignalPOIs {wc} --robustFit 1 "
                f"--setParameters {wcs_start} "
                f"{freeze_cmd} --setParameterRanges {range_str} "
                f"-m 1 -d {workspace}"
            )

            print('Submitting', wc)
            sh_path = os.path.join(target_dir, f'condor_{wc}.sh')
            with open(sh_path, 'w') as condorFile:
                condorFile.write(self.Impact_sh_preamble(cmssw_base, target_dir))
                condorFile.write("if [ $1 -eq 0 ]; then\n")
                condorFile.write(f"  {combine_cmd}")
                if len(wcs) > 1:
                    exclude = ' --exclude ' + ','.join([w for w in wcs if w != wc])
                    condorFile.write(exclude)
                if unblind: print('Running over ACTUAL DATA!'); condorFile.write('\n')
                else: condorFile.write(' -t -1\n')
                condorFile.write('fi\n')

            sub_path = os.path.join(target_dir, f'condor_{wc}_initial.sub')
            with open(sub_path, 'w') as condorFile:
                condorFile.write(self.Impact_condorsub(wc, sh_path))
                condorFile.write('\nqueue 1\n')

            os.system(f"chmod 777 {sh_path}")
            os.system(f"condor_submit {sub_path} -batch-name {wc}_initial")


    def ImpactNuisance(self, workspace='workspace.root', wcs=[], unblind=False, version=''):

        target_dir, job_dir_name, cmssw_base, test_dir = self.ImpactSetup(workspace, unblind)

        if not wcs: wcs = self.wcs
        ranges = ':'.join([wc+'='+','.join((str(r[0]), str(r[1]))) for wc,r in list(self.wc_ranges_differential.items()) if wc in self.wcs])
        wcs_start = ','.join(wc+'=0' for wc in self.wcs)
        for wc in wcs:
            if unblind:
                print('Running over ACTUAL DATA!');

            # target = 'condor_%s_fit.sh' % wc
            sh_path = os.path.join(target_dir, f'condor_{wc}_nuisance.sh')

            print('Submitting', wc)
            with open(sh_path, 'w') as condorFile:
                condorFile.write(self.Impact_sh_preamble(cmssw_base, target_dir))
                for i,np in enumerate(self.systematics):
                    condorFile.write(f"if [ $1 -eq {i} ]; then\n")
                    freeze = ','.join([w for w in wcs if w != wc])
                    freeze_cmd = f"--freezeParameters {freeze}" if freeze else ""
                    combine_cmd = (
                        f"combine -M MultiDimFit -n _paramFit_{wc}_{np}{version} "
                        f"--algo impact --redefineSignalPOIs {wc} -P {np} " 
                        f"--floatOtherPOIs 1 --saveInactivePOI 1 --robustFit 1 "
                        f"{freeze_cmd} --setParameterRanges {ranges} -m 1 -d {workspace} --setParameters {wcs_start} " 
                    )
                    condorFile.write(f"{combine_cmd}")
                    if unblind:
                        condorFile.write('\n')
                    else:
                        condorFile.write( ' -t -1\n')
                    condorFile.write('fi\n')

            sub_path = os.path.join(target_dir, f'condor_{wc}_nuisance.sub')
            with open(sub_path, 'w') as condorFile:
                condorFile.write(self.Impact_condorsub(wc, sh_path))
                condorFile.write('requestMemory = 8192\n\n')
                condorFile.write(f'queue {len(self.systematics)}\n')
            
            os.system(f"chmod 777 {sh_path}")
            os.system(f"condor_submit {sub_path} -batch-name {wc}_nuisance")#  % (target, wc))
            os.system('cd ../')


    def ImpactCollect(self, workspace='workspace.root', wcs=[], unblind=False, version=''):

        target_dir, job_dir_name, cmssw_base, test_dir = self.ImpactSetup(workspace, unblind)
       
        if not wcs: wcs = self.wcs
        ranges = ':'.join([wc+'='+','.join((str(r[0]), str(r[1]))) for wc,r in list(self.wc_ranges_differential.items()) if wc in self.wcs])
        wcs_start = ','.join(wc+'=0' for wc in self.wcs)
        for wc in wcs:
            sh_path = os.path.join(target_dir, f'condor_{wc}_collect.sh')
            print('Submitting', wc)
            with open(sh_path, 'w') as condorFile:
                condorFile.write(self.Impact_sh_preamble(cmssw_base, target_dir))
                combine_cmd = (
                    f"combineTool.py -M Impacts -d {workspace} "
                    f"-o impacts{wc}{version}.json --setParameters {wcs_start} "
                    f"-m 1 -n {wc} --redefineSignalPOIs {wc}"
                )
                condorFile.write(f"{combine_cmd}")
                if unblind: 
                    print('Running over ACTUAL DATA!')
                else: 
                    condorFile.write(' -t -1')
                exclude_list = [w for w in self.wcs if w != wc]
                if exclude_list:
                    condorFile.write(' --exclude ' + ','.join(exclude_list))
                condorFile.write('\n\n')
                condorFile.write(f"plotImpacts.py -i impacts{wc}{version}.json -o impacts{wc}{version}\n")

            sub_path = os.path.join(target_dir, f'condor_{wc}_collect.sub')
            with open(sub_path, 'w') as condorFile:
                condorFile.write(self.Impact_condorsub(wc, sh_path))
                condorFile.write('\nqueue 1\n')
                
            os.system(f"chmod 777 {sh_path}")
            os.system(f"condor_submit {sub_path} -batch-name {wc}_collect")

            
if __name__ == "__main__":
    log_file = 'EFTFit_out.log'

    FORMAT1 = '%(message)s'
    FORMAT2 = '[%(levelname)s] %(message)s'
    FORMAT3 = '[%(levelname)s][%(name)s] %(message)s'

    frmt1 = logging.Formatter(FORMAT1)
    frmt2 = logging.Formatter(FORMAT2)
    frmt3 = logging.Formatter(FORMAT3)

    logging.basicConfig(
        level=logging.DEBUG,
        format=FORMAT2,
        filename=log_file,
        filemode='w'
    )

    # Configure logging to also output to stdout
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(frmt2)
    logging.getLogger('').addHandler(console)

    fitter = EFTFit()

    #Example of a workflow:
    #fitter.makeWorkspaceEFT('EFT_MultiDim_Datacard.txt')
    #fitter.bestFit(name='.EFT.SM.Float.preScan', scan_params=['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], freeze=False, autoBounds=True)
    #fitter.gridScan(name='.EFT.SM.Float.gridScan.ctWctZ', batch='crab', scan_wcs=fitter.scan_params, params_tracked=fitter.wcs_tracked, points=50000, freeze=False)
    #fitter.retrieveGridScan(name='.EFT.SM.Float.gridScan.ctWctZ')
    #startValuesString = fitter.getBestValues2D(name='.EFT.SM.Float.gridScan.ctWctZ', scan_params=fitter.scan_wcs, params_tracked=fitter.wcs_tracked)
    #startValuesString = fitter.getBestValues1DEFT(basename='.EFT.SM.Float.gridScan', wcs=fitter.operators)
    #fitter.bestFit(name='.EFT.SM.Float.postScan', scan_params=fitter.wcs, startValuesString=startValuesString, freeze=False, autoBounds=True)

    #logging.info("Logger shutting down!")
    #logging.shutdown()
