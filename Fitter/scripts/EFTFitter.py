import os
import sys
import logging
import subprocess as sp
import ROOT
import itertools
import getpass

class EFTFit(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # WCs lists for easy use
        # Full list of opeators
        self.wcs = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        # Default pair of wcs for 2D scans
        self.scan_wcs = ['ctW','ctZ']
        # Default wcs to keep track of during 2D scans
        self.wcs_tracked = ['ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        # Scan ranges of the wcs
        self.wc_ranges = {  'ctW':(-6,6),   'ctZ':(-7,7),
                            'cpt':(-40,30), 'ctp':(-35,65),
                            'ctli':(-20,20),'ctlSi':(-22,22),
                            'cQl3i':(-20,20),'cptb':(-40,40),
                            'ctG':(-3,3),   'cpQM':(-30,50),  
                            'ctlTi':(-4,4),'ctei':(-20,20),
                            'cQei':(-16,16),'cQlMi':(-17,17),
                            'cpQ3':(-20,12),'cbW':(-10,10)
                         }
        # Systematics names except for FR stats. Only used for debug
        self.systematics = ['CERR1','CERR2','CMS_eff_em','CMS_scale_j','ChargeFlips','FR_FF','LEPID','MUF','MUR','PDF','PSISR','PU',
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

    def bestFitSM(self, name='.test', freeze=[], autoMaxPOIs=True, other=[]):
        ### Multidimensional fit ###
        args=['combine','-d','SMWorkspace.root','-v','2','--saveFitResult','-M','MultiDimFit','--cminPoiOnlyFit','--cminDefaultMinimizerStrategy=2']
        if name:        args.extend(['-n','{}'.format(name)])
        if freeze:      args.extend(['--freezeParameters',','.join(freeze)])
        if autoMaxPOIs:  args.extend(['--autoMaxPOIs=*'])
        #if autoMaxPOIs:  args.extend(['--autoBounds=mu_tllq'])
        if other:       args.extend(other)

        logging.info(" ".join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with SMFit.")
        sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
        sp.call(['mv','multidimfit'+name+'.root','../fit_files/'])
        self.printBestFitsSM(name)

    def gridScanSM(self, name='.test', crab=False, scan_params=['mu_ttll'], params_tracked=['mu_ttlnu','mu_ttH','mu_tllq'], points=300, freeze=False, other=[]):
        ### Runs deltaNLL Scan in a parameter using CRAB ###
        ### Can be used to do 2D scans as well ###
        logging.info("Doing grid scan...")

        args = ['combineTool.py','-d','SMWorkspace.root','-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=0']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if scan_params:     args.extend(['-P',' -P '.join(scan_params)]) # Preserves constraints
        if params_tracked: args.extend(['--trackParameters',','.join(params_tracked)])
        if not freeze:        args.extend(['--floatOtherPOIs','1'])
        if other:             args.extend(other)
        # Common 'other' uses: --setParameterRanges param=min,max
        if crab:              args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points','2000'])
        logging.info(' '.join(args))

        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with gridScan.")
        if not crab: sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
        
    def batch1DScanSM(self, basename='.test', crab=False, scan_params=[], points=300, freeze=False):
        ### For each SM signal strength, run a 1D deltaNLL Scan.
        if not scan_params:
            scan_params = ['mu_ttll','mu_ttlnu','mu_ttH','mu_tllq']

        for param in scan_params:
            self.gridScanSM('{}.{}'.format(basename,param), crab, [param], self.systematics+[params for params in scan_params if params != param], points, freeze, ['--setParameterRanges','{}=0,3'.format(param)])
            
            

    def makeWorkspaceEFT(self, datacard='EFT_MultiDim_Datacard.txt'):
        ### Generates a workspace from a datacard and fit parameterization file ###
        logging.info("Creating workspace")
        if not os.path.isfile(datacard):
            logging.error("Datacard does not exist!")
            sys.exit()
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['text2workspace.py',datacard,'-P','EFTFit.Fitter.EFT16DModel:eft16D','--PO','fits='+CMSSW_BASE+'/src/EFTFit/Fitter/hist_files/16D_Parameterization.npy','-o','16DWorkspace.root']

        logging.info(' '.join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        
    def bestFit(self, name='.test', params_POI=[], startValuesString='', freeze=False, autoBounds=True, other=[]):
        ### Multidimensional fit ###
        args=['combine','-d','16DWorkspace.root','-v','2','--saveFitResult','-M','MultiDimFit','-H','AsymptoticLimits','--cminPoiOnlyFit','--cminDefaultMinimizerStrategy=2']
        if name:              args.extend(['-n','{}'.format(name)])
        if scan_params:     args.extend(['-P',' -P '.join(scan_params)]) # Preserves constraints
        args.extend(['--trackParameters',','.join([wc for wc in self.wcs if wc not in scan_params])])
        if startValuesString: args.extend(['--setParameters',startValuesString])
        if not freeze:        args.extend(['--floatOtherPOIs','1'])
        if autoBounds:        args.extend(['--autoBoundsPOIs=*'])
        if other:             args.extend(other)

        logging.info(" ".join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with bestFit.")
        sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
        if os.path.isfile('multidimfit'+name+'.root'):
            sp.call(['mv','multidimfit'+name+'.root','../fit_files/'])
        self.printBestFits(name)

    def gridScan(self, name='.test', crab=False, scan_params=['ctW','ctZ'], params_tracked=['ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], points=5000, freeze=False, other=[]):
        ### Runs deltaNLL Scan in two parameters using CRAB ###
        logging.info("Doing grid scan...")

        args = ['combineTool.py','-d','16DWorkspace.root','-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=0']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if scan_params:     args.extend(['-P',' -P '.join(scan_params)]) # Preserves constraints
        if params_tracked: args.extend(['--trackParameters',','.join(params_tracked)])
        if not freeze:        args.extend(['--floatOtherPOIs','1'])
        if other:             args.extend(other)
        if crab:              args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points','2000'])
        logging.info(' '.join(args))

        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with gridScan.")
        if not crab: sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])

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


    def retrieveGridScan(self, name='.test', user=getpass.getuser()):
        ### Retrieves finished grid jobs, extracts, and hadd's into a single file ###
        taskname = name.replace('.','')
        logging.info("Retrieving gridScan files. Task name: "+taskname)

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
            sys.exit()

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

        # Remove the temporary directory and split root files
        sp.call(['rm','-r',taskname+'tmp'])

    def batch1DScanEFT(self, basename='.test', crab=False, scan_wcs=[], points=300, freeze=False):
        ### For each wc, run a 1D deltaNLL Scan.
        if not scan_wcs:
            scan_wcs = self.wcs

        for param in scan_wcs:
            self.gridScan('{}.{}'.format(basename,wc), crab, [wc], [wcs for wcs in self.wcs if wcs != wc], points, freeze)

    def batch2DScanEFT(self, basename='.EFT.gridScan', freeze=False, points=160000, allPairs=False, other=[]):
        ### For pairs of wcs, runs deltaNLL Scan in two wcs using CRAB ###

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs

            for wcs in itertools.combinations(scan_wcs,2):
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print pois, wcs_tracked
                self.gridScan(name='{}.{}{}'.format(basename,wcs[0],wcs[1]), crab=True, scan_wcs=list(wcs), wcs_tracked=wcs_tracked, points=points, freeze=freeze, other=other)

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]

            for wcs in scan_wcs:
                wcs_tracked = [wc for wc in self.wcs if wc not in wcs]
                #print pois, wcs_tracked
                self.gridScan(name='{}.{}{}'.format(basename,wcs[0],wcs[1]), crab=True, scan_wcs=list(wcs), wcs_tracked=wcs_tracked, points=points, freeze=freeze, other=other)

    def batchResubmit1DScansEFT(self, basename='.EFT.gridScan', scan_wcs=[]):
        ### For each wc, attempt to resubmit failed CRAB jobs ###
        if not scan_wcs:
            scan_wcs = self.wcs

        for wc in scan_wcs:
            process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+wc], stdout=sp.PIPE, stderr=sp.PIPE)
            with process.stdout,process.stderr:
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')

    def batchResubmit2DScansEFT(self, basename='.EFT.gridScan', allPairs=False):
        ### For pairs of wcs, attempt to resubmit failed CRAB jobs ###

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs

            for wcs in itertools.combinations(scan_wcs,2):
                process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+wcs[0]+wcs[1]], stdout=sp.PIPE, stderr=sp.PIPE)
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]

            for wcs in scan_wcs:
                process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+wcs[0]+wcs[1]], stdout=sp.PIPE, stderr=sp.PIPE)
                with process.stdout,process.stderr:
                    self.log_subprocess_output(process.stdout,'info')
                    self.log_subprocess_output(process.stderr,'err')

    def batchRetrieve1DScansEFT(self, basename='.test', scan_wcs=[]):
        ### For each wc, retrieves finished 1D deltaNLL grid jobs, extracts, and hadd's into a single file ###
        if not scan_wcs:
            scan_wcs = self.wcs

        for wc in scan_wcs:
            self.retrieveGridScan('{}.{}'.format(basename,wc))

    def batchRetrieve2DScansEFT(self, basename='.EFT.gridScan', allPairs=False):
        ### For pairs of wcs, retrieves finished grid jobs, extracts, and hadd's into a single file ###

        # Use EVERY combination of wcs
        if allPairs:
            scan_wcs = self.wcs
            for wcs in itertools.combinations(scan_wcs,2):
                self.retrieveGridScan('{}.{}{}'.format(basename,wcs[0],wcs[1]))

        # Use each wc only once
        if not allPairs:
            scan_wcs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
            for wcs in scan_wcs:
                self.retrieveGridScan('{}.{}{}'.format(basename,wcs[0],wcs[1]))

    def batch1DBestFitEFT(self, basename='.EFT.SM.Float', wcs=[]):
        ### For each wc, run a 1D fit with others frozen. Use start point from 1D scan with other floating. ###
        if not wcs:
            wcs = self.wcs

        for wc in wcs:
            logging.info("Fitting for wc {}.".format(wc))
            start_point = self.getBestValues1DEFT(basename,[wc])
            logging.info("Start value: {}".format(start_point))
            self.bestFit('{}.BestFit.{}'.format(basename,wc), [wc], start_point, True)
            
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

            value = round(roorealvar.getVal(),2)
            err_sym =  round(roorealvar.getError(),2)
            err_low = round(roorealvar.getErrorLo(),2)
            err_high = round(roorealvar.getErrorHi(),2)

            fit_array.append((param,value,err_sym,err_low,err_high))

        logging.info("Quick result:")
        for row in fit_array:
            print row[0],"+/-",row[1]
            logging.debug(row[0],"+/-",row[1])
        logging.info("Param, Best Fit Value, Symmetric Error, Low side of Asym Error, High side of Asym Error")
        for row in fit_array:
            print ', '.join([str(ele) for ele in row])
            logging.debug(row)

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

    def printIntervalFitsEFT(self, basename='.EFT.SM.Float', wcs=[]):
        ### Print a table of wcs, their best fits, and their uncertainties ###
        ### Use 1D scans instead of regular MultiDimFit ###
        if not wcs:
            wcs = self.wcs

        ROOT.gROOT.SetBatch(True)

        fit_array = []

        canvas = ROOT.TCanvas()
        for wc in wcs:

            canvas.Clear()

            logging.debug("Obtaining result of scan: higgsCombine{}.{}.MultiDimFit.root".format(basename,wc))
            fit_file = ROOT.TFile.Open('../fit_files/higgsCombine{}.{}.MultiDimFit.root'.format(basename,wc))
            limit_tree = fit_file.Get('limit')

            limit_tree.Draw('2*deltaNLL:{}>>{}1DNLL(50,{},{})'.format(wc,wc,self.wc_ranges[wc][0],self.wc_ranges[wc][1]),'2*deltaNLL>-1','same')
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
    #fitter.gridScan(name='.EFT.SM.Float.gridScan.ctWctZ', crab=True, scan_wcs=fitter.scan_params, params_tracked=fitter.wcs_tracked, points=50000, freeze=False)
    #fitter.retrieveGridScan(name='.EFT.SM.Float.gridScan.ctWctZ')
    #startValuesString = fitter.getBestValues2D(name='.EFT.SM.Float.gridScan.ctWctZ', scan_params=fitter.scan_wcs, params_tracked=fitter.wcs_tracked)
    #startValuesString = fitter.getBestValues1DEFT(basename='.EFT.SM.Float.gridScan', wcs=fitter.operators)
    #fitter.bestFit(name='.EFT.SM.Float.postScan', scan_params=fitter.wcs, startValuesString=startValuesString, freeze=False, autoBounds=True)

    #logging.info("Logger shutting down!")
    #logging.shutdown()
