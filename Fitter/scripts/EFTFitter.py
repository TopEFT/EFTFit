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
from collections import defaultdict
from EFTFit.Fitter.findMask import findMask 

# Batch modes supported are: CRAB3 ('crab') and Condor ('condor')

class EFTFit(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # WCs lists for easy use
        # Full list of opeators
        self.wcs = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi', 'cQq13', 'cQq83', 'cQq11', 'ctq1', 'cQq81', 'ctq8', 'ctt1', 'cQQ1', 'cQt8', 'cQt1', ]
        #self.wcs = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        # Default pair of wcs for 2D scans
        self.scan_wcs = ['ctW','ctZ']
        # Scan ranges of the wcs

        # Limits appropriate for asimov ptz-lj0pt fits (for prof, but can be used for frozen too)
        self.wc_ranges_differential = {
            'cQQ1' : (-4.0,4.0),
            'cQei' : (-4.0,4.0),
            'cQl3i': (-5.5,5.5),
            'cQlMi': (-4.0,4.0),
            'cQq11': (-0.7,0.7),
            'cQq13': (-0.35,0.35),
            'cQq81': (-1.7,1.5),
            'cQq83': (-0.6,0.6),
            'cQt1' : (-4.0,4.0),
            'cQt8' : (-8.0,8.0),
            'cbW'  : (-3.0,3.0),
            'cpQ3' : (-4.0,4.0),
            'cpQM' : (-10.0,17.0),
            'cpt'  : (-15.0,15.0),
            'cptb' : (-9.0,9.0),
            'ctG'  : (-0.8,0.8),
            'ctW'  : (-1.5,1.5),
            'ctZ'  : (-2.0,2.0),
            'ctei' : (-4.0,4.0),
            'ctlSi': (-5.0,5.0),
            'ctlTi': (-0.9,0.9),
            'ctli' : (-4.0,4.0),
            'ctp'  : (-11.0,35.0),
            'ctq1' : (-0.6,0.6),
            'ctq8' : (-1.4,1.4),
            'ctt1' : (-2.1,2.1),
        }

        # Limits appropriate for asimov njets fits (for prof, but can be used for frozen too)
        self.wc_ranges_njets = {
            'cQQ1' : (-6.0,6.0),
            'cQei' : (-7.0,7.0),
            'cQl3i': (-10.0,10.0),
            'cQlMi': (-8.0,8.0),
            'cQq11': (-1.5,1.5),
            'cQq13': (-0.6,0.6),
            'cQq81': (-4.0,3.0),
            'cQq83': (-1.2,1.2),
            'cQt1' : (-5.0,5.0),
            'cQt8' : (-10.0,10.0),
            'cbW'  : (-5.0,5.0),
            'cpQ3' : (-10.0,7.0),
            'cpQM' : (-11.0,30.0),
            'cpt'  : (-25.0,20.0),
            'cptb' : (-17.0,17.0),
            'ctG'  : (-1.5,1.5),
            'ctW'  : (-4.0,3.0),
            'ctZ'  : (-4.0,4.0),
            'ctei' : (-8.0,8.0),
            'ctlSi': (-8.0,8.0),
            'ctlTi': (-1.4,1.4),
            'ctli' : (-8.0,8.0),
            'ctp'  : (-11.0,35.0),
            'ctq1' : (-1.4,1.4),
            'ctq8' : (-3.0,3.0),
            'ctt1' : (-3.0,3.0),
        }


        # Systematics names except for FR stats. Only used for debug
        self.systematics = ['CERR1','CERR2','CMS_eff_em','CMS_scale_j','ChargeFlips','FR_FF','LEPID','MUFR','PDF','PSISR','PFSR','PU',
                            'missing_parton',
                            'QCDscale_V','QCDscale_VV','QCDscale_VVV','QCDscale_tHq','QCDscale_ttG','QCDscale_ttH','QCDscale_ttbar',
                            'hf','hfstats1','hfstats2','lf','lfstats1','lfstats2','lumi_13TeV_2017','pdf_gg','pdf_ggttH','pdf_qgtHq','pdf_qq',
                           ]

    def log_subprocess_output(self,pipe,level):
        ### Pipes Popen streams to logging class ###
        for line in iter(pipe.readline, ''):
            if level=='info': logging.info(line.rstrip('\n'))
            if level=='err': logging.error(line.rstrip('\n'))

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
                    print 'No bins found containig ' + m + '! Please check the spelling, and try again.'
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

    def gridScan(self, name='.test', batch='', freeze=False, scan_params=['ctW','ctZ'], params_tracked=[], points=90000, other=[], mask=[], mask_syst=[], workspace='EFTWorkspace.root'):
        ### Runs deltaNLL Scan in two parameters using CRAB or Condor ###
        logging.info("Doing grid scan...")

        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['combineTool.py','-d',CMSSW_BASE+'/src/EFTFit/Fitter/test/'+workspace,'-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=0']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if scan_params:     args.extend(['-P',' -P '.join(scan_params)]) # Preserves constraints
        track = []
        if any('trackParameters' in s for s in other):
            index = other.index('--trackParameters')
            other.pop(index)
            track.append(other.pop(index))
        if params_tracked: args.extend(['--trackParameters',','.join(params_tracked+track)])
        if not freeze:        args.extend(['--floatOtherPOIs','1'])
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
                    print 'No bins found containig ' + m + '! Please check the spelling, and try again.'
                    return
                if 'sfz' not in m:
                    msk = [x for x in msk if 'sfz' not in x]
                masks.append(msk)
            masks = [item for sub in masks for item in sub]
            args.extend(['--setParameters',','.join(masks)])

        if batch=='crab':              args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points','3000'])
        if batch=='condor' and freeze==False and points>3000: args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','3000','--dry-run'])
        elif batch=='condor' and freeze==False: args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','10','--dry-run'])
        elif batch=='condor':          args.extend(['--job-mode','condor','--task-name',name.replace('.',''),'--split-points','10','--dry-run'])
        logging.info(' '.join(args))

        # Run the combineTool.py command
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        process.wait()

        # Condor needs executable permissions on the .sh file, so we used --dry-run
        # Add the permission and complete the submission.
        if batch=='condor':
            if os.path.exists('condor{}'.format(name)):
                logging.error("Directory condor{} already exists!".format(name))
                logging.error("Aborting submission.")
                #return
            sp.call(['mkdir','condor{}'.format(name)])
            sp.call(['chmod','a+x','condor_{}.sh'.format(name.replace('.',''))])
            sp.call(['sed','-i','s/queue/\\n\\nrequestMemory=3072\\n\\nqueue/','condor_{}.sub'.format(name.replace('.',''))]) # Ask for at least 3GB of RAM
            logging.info('Now submitting condor jobs.')
            condorsub = sp.Popen(['condor_submit','-append','initialdir=condor{}'.format(name),'condor_{}.sub'.format(name.replace('.',''))], stdout=sp.PIPE, stderr=sp.PIPE)
            with condorsub.stdout,condorsub.stderr:
                self.log_subprocess_output(condorsub.stdout,'info')
                self.log_subprocess_output(condorsub.stderr,'err')
            condorsub.wait()
            
        if batch: logging.info("Done with gridScan batch submission.")
            
        if not batch:
            sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
            logging.info("Done with gridScan.")

    def getBestValues2D(self, name, scan_params=[], params_tracked=[]):
        ### Gets values of parameters for grid scan point with best deltaNLL ###
  
        bestDeltaNLL=1000000;
        bestEntry=-1;

        fitFile = '../fit_files/higgsCombine'+name+'.MultiDimFit.root'
        print fitFile

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


    def retrieveGridScan(self, name='.test', batch='crab', user='byates'):#getpass.getuser()):
        ### Retrieves finished grid jobs, extracts, and hadd's into a single file ###
        taskname = name.replace('.','')
        logging.info("Retrieving gridScan files. Task name: "+taskname)


        if batch=='crab':
            # Find crab output files (defaults to user's hadoop directory)
            hadooppath = '/hadoop/store/user/{}/EFT/Combine/{}'.format(user, taskname)
            (tarpath,tardirs,tarfiles) = os.walk(hadooppath)
            if not tarfiles[2]:
                logging.error("No files found in store!")
                sys.exit()

            # Make a temporary folder to hold the extracted root files
            if not os.path.isdir(taskname+'tmp'):
                sp.call(['mkdir',taskname+'tmp'])
            else:
                logging.error("Directory {}tmp/ already exists! Please rename this directory.".format(taskname))
                return

            # Extract the root files
            for tarfile in tarfiles[2]:
                if tarfile.endswith('.tar'):
                    print tarfiles[0]+'/'+tarfile
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
            haddargs = ['hadd','-f','../fit_files/higgsCombine'+name+'.MultiDimFit.root']+sorted(glob.glob('higgsCombine{}.POINTS*.root'.format(name)))
            process = sp.Popen(haddargs, stdout=sp.PIPE, stderr=sp.PIPE)
            with process.stdout,process.stderr:
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')
            process.wait()
            for rootfile in glob.glob('higgsCombine{}.POINTS*.root'.format(name)):
                os.remove(rootfile)
            if os.path.isfile('condor_{}.sh'.format(name.replace('.',''))):
                os.rename('condor_{}.sh'.format(name.replace('.','')),'condor{0}/condor_{0}.sh'.format(name))
            if os.path.isfile('condor_{}.sub'.format(name.replace('.',''))):
                os.rename('condor_{}.sub'.format(name.replace('.','')),'condor{0}/condor_{0}.sub'.format(name))

    def batch1DScanEFT(self, basename='.test', batch='crab', freeze=False, scan_wcs=[], points=300, other=[], mask=[], mask_syst=[], workspace='EFTWorkspace.root', ignore=[], wc_ranges=None):
        ### For each wc, run a 1D deltaNLL Scan.
        if not scan_wcs:
            scan_wcs = self.wcs
        #else: self.wcs = scan_wcs

        # Set the WC ranges if not specified
        if wc_ranges is None: wc_ranges = self.wc_ranges_njets

        zero_ignore = []
        freeze_ignore = []
        if len(ignore)>0:
            zero_ignore = ['--setParameters ' + ','.join(['{}=0'.format(wc) for wc in ignore])]
            freeze_ignore = ['--freezeParameters ' + ','.join(['{}'.format(wc) for wc in ignore])]
            for iwc in ignore:
                if iwc in scan_wcs: scan_wcs.remove(iwc)
        params = ','.join(['{}=0'.format(wc) for wc in scan_wcs])
        for wc in scan_wcs:
            self.gridScan('{}.{}'.format(basename,wc), batch, freeze, [wc], [wcs for wcs in scan_wcs if wcs != wc], points, ['--setParameterRanges {}={},{}'.format(wc,wc_ranges[wc][0],wc_ranges[wc][1])]+zero_ignore+freeze_ignore+other+['--setParameters', params], mask, mask_syst, workspace)

    '''
    example: `fitter.batch2DScanEFT('.test.ctZ', batch='crab', wcs=['ctZ'], workspace='wps_njet_runII.root')`
    example: `fitter.batch2DScanEFT('.test.ctZ', batch='crab', wcs='ctZ', workspace='wps_njet_runII.root')`
    '''
    def batch2DScanEFT(self, basename='.EFT.gridScan', batch='crab', freeze=False, points=90000, allPairs=False, other=[], mask=[], mask_syst=[], wcs=[], workspace='EFTWorkspace.root', differential=None):
        ### For pairs of wcs, runs deltaNLL Scan in two wcs using CRAB or Condor ###
        if differential is None:
            differential = 'njets' not in workspace
            print 'Assuming',
            print 'njets' if not differential else 'differential',
            print 'based on the workspace.\nTo force differential or njets set `differential=True/False` respectively.'
            wc_ranges = self.wc_ranges_differential if differential else self.wc_ranges_njets

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs

            for wcs in itertools.combinations(scan_wcs,2):
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print pois, wcs_tracked
                self.gridScan(name='{}.{}{}'.format(basename,wcs[0],wcs[1]), batch=batch, freeze=freeze, scan_params=list(wcs), params_tracked=wcs_tracked, points=points, other=+other, mask=mask, mask_syst=mask_syst, workspace=workspace)

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('ctW','ctG'),('ctZ','ctG'),('ctp','ctG'),('cpQM','ctG'),('cbW','ctG'),('cpQ3','ctG'),('cptb','ctG'),('cpt','ctG'),('cQl3i','ctG'),('cQlMi','ctG'),('cQei','ctG'),('ctli','ctG'),('ctei','ctG'),('ctlSi','ctG'),('ctlTi','ctG')]
            #pairs from AN
            scan_wcs = [('cQlMi','cQei'),('cpQ3','cbW'),('cptb','cQl3i'),('ctG','cpQM'),('ctZ','ctW'),('ctei','ctlTi'),('ctlSi','ctli'),('ctp','cpt')]
            scan_wcs = [('ctW','ctZ'),('ctG','ctZ'),('ctp','ctZ'),('cpQM','ctZ'),('cbW','ctZ'),('cpQ3','ctZ'),('cptb','ctZ'),('cpt','ctZ'),('cQl3i','ctZ'),('cQlMi','ctZ'),('cQei','ctZ'),('ctli','ctZ'),('ctei','ctZ'),('ctlSi','ctZ'),('ctlTi','ctZ')]
            if len(wcs) > 0:
                scan_wcs = []
                if isinstance(wcs, str): wcs = [wcs]
                for wc in wcs:
                    if isinstance(wc, tuple): scan_wcs.append(wc)
                    else: scan_wcs = scan_wcs + [(wc, other_wc) for other_wc in self.wcs if wc != other_wc]

            params = ','.join(['{}=0'.format(w) for wc in scan_wcs for w in wc])
            for wcs in scan_wcs:
                wcs_tracked = [wc for wc in wcs if wc not in wcs]
                #print pois, wcs_tracked
                self.gridScan(name='{}.{}{}'.format(basename,wcs[0],wcs[1]), batch=batch, freeze=freeze, scan_params=list(wcs), params_tracked=wcs_tracked, points=points, other=['--setParameterRanges {}={},{}:{}={},{}'.format(wcs[0],wc_ranges[wcs[0]][0],wc_ranges[wcs[0]][1],wcs[1],wc_ranges[wcs[1]][0],wc_ranges[wcs[1]][1])]+other+['--setParameters', params], mask=mask, mask_syst=mask_syst, workspace=workspace)

    def batch3DScanEFT(self, basename='.EFT.gridScan', batch='crab', freeze=False, points=27000000, allPairs=False, other=[], wc_triplet=[], mask=[], mask_syst=[]):
        ### For pairs of wcs, runs deltaNLL Scan in two wcs using CRAB or Condor ###

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs

            for wcs in itertools.combinations(scan_wcs,2):
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print pois, wcs_tracked
                self.gridScan(name='{}.{}{}{}'.format(basename,wcs[0],wcs[1],wcs[2]), batch=batch, freeze=freeze, scan_params=list(wcs), params_tracked=wcs_tracked, points=points, other=other, mask=mask, mask_syst=mask_syst, workspace=workspace)

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('ctZ','ctp','cpt')]
            if len(wc_triplet)>0: scan_wcs = wc_triplet
            #scan_wcs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
            #scan_wcs = [('ctW','ctG'),('ctZ','ctG'),('ctp','ctG'),('cpQM','ctG'),('cbW','ctG'),('cpQ3','ctG'),('cptb','ctG'),('cpt','ctG'),('cQl3i','ctG'),('cQlMi','ctG'),('cQei','ctG'),('ctli','ctG'),('ctei','ctG'),('ctlSi','ctG'),('ctlTi','ctG')]

            for wcs in scan_wcs:
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print pois, wcs_tracked
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
            scan_wcs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
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
            scan_wcs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
            scan_wcs = [('ctW','ctG'),('ctZ','ctG'),('ctp','ctG'),('cpQM','ctG'),('cbW','ctG'),('cpQ3','ctG'),('cptb','ctG'),('cpt','ctG'),('cQl3i','ctG'),('cQlMi','ctG'),('cQei','ctG'),('ctli','ctG'),('ctei','ctG'),('ctlSi','ctG'),('ctlTi','ctG')]
            #pairs from AN
            scan_wcs = [('cQlMi','cQei'),('cpQ3','cbW'),('cptb','cQl3i'),('ctG','cpQM'),('ctZ','ctW'),('ctei','ctlTi'),('ctlSi','ctli'),('ctp','cpt')]
            scan_wcs = [('ctW','ctZ'),('ctG','ctZ'),('ctp','ctZ'),('cpQM','ctZ'),('cbW','ctZ'),('cpQ3','ctZ'),('cptb','ctZ'),('cpt','ctZ'),('cQl3i','ctZ'),('cQlMi','ctZ'),('cQei','ctZ'),('ctli','ctZ'),('ctei','ctZ'),('ctlSi','ctZ'),('ctlTi','ctZ')]
            if len(wcs) > 0:
                scan_wcs = []
                if isinstance(wcs, str): wcs = [wcs]
                for wc in wcs:
                    if isinstance(wc, tuple): scan_wcs.append(wc)
                    else: scan_wcs = scan_wcs + [(wc, other_wc) for other_wc in self.wcs if wc != other_wc]
            for wcs in scan_wcs:
                print wcs
                print '{}.{}{}'.format(basename,wcs[0],wcs[1]), batch
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
        #if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
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
        for event in range(len(wc_dict_reduced.keys())):
            wc_branch[0] = wc_dict_reduced.keys()[event]
            deltaNLL_branch[0] = wc_dict_reduced.values()[event]
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
        # print JOB_PREFIX + command
        print 'Created job script: %s' % fname

        outscriptname = 'condor_%s.sh' % fname
        subfilename = 'condor_%s.sub' % fname
        print '>> condor job script will be %s' % outscriptname
        outscript = open(outscriptname, "w")
        outscript.write(JOB_PREFIX)
        jobs = 0
        wsp_files = set()
        for i,proc in enumerate(range(0,points,split), points/split):
            outscript.write('\nif [ $1 -eq %i ]; then\n' % jobs)
            outscript.write('python /afs/crc.nd.edu/user/b/byates2/CMSSW_8_1_0/src/EFTFit/Fitter/scripts/reduce.py %d %d %s %s\n' % (proc, proc+split-1, name, ' '.join(wc)))
            jobs += 1
            outscript.write('fi')
        #for i, j in enumerate(range(0, len(self.job_queue), self.merge)):
            #outscript.write('\nif [ $1 -eq %i ]; then\n' % jobs)
            #jobs += 1
            #for line in self.job_queue[j:j + self.merge]:
                #newline = line
                #outscript.write('  ' + newline + '\n')
            #outscript.write('fi')
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
            #scan_wcs = [('ctW','ctG'),('ctZ','ctG'),('ctp','ctG'),('cpQM','ctG'),('cbW','ctG'),('cpQ3','ctG'),('cptb','ctG'),('cpt','ctG'),('cQl3i','ctG'),('cQlMi','ctG'),('cQei','ctG'),('ctli','ctG'),('ctei','ctG'),('ctlSi','ctG'),('ctlTi','ctG')]
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
            print "Best entry for {} is {}.".format(poiwc,bestNLL[0])
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
            print("Best value of {}: {}".format(poiwc,bestFits[poiwc][poiwc]))
            for trackedwc in trackedwcs:
                print("Value according to {}: {}".format(trackedwc,bestFits[poiwc][trackedwc]))
            
    def printBestFitsSM(self, name='.EFT.SM.Float'):
        ### Print a table of SM signal strengths, their best fits, and their uncertainties ###
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
            print row[0],row[1],"+/-",row[2]," ",row[3],"+{}".format(row[4])
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
            print row[0],"+/-",row[1]
            logging.debug(row[0],"+/-",row[1])
        logging.info("WC, Best Fit Value, Symmetric Error, Low side of Asym Error, High side of Asym Error")
        for row in fit_array:
            print ', '.join([str(ele) for ele in row])
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
            print line              

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
