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

        # Operator lists for easy use
        # Full list of opeators
        self.operators = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        # Default pair of operators for 2D scans
        self.operators_POI = ['ctW','ctZ']
        # Default operators to keep track of during 2D scans
        self.operators_tracked = ['ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        # Scan ranges of the operators
        self.op_ranges = {  'ctW':(-6,6),   'ctZ':(-7,7),
                            'cpt':(-40,30), 'ctp':(-35,65),
                            'ctli':(-20,20),'ctlSi':(-22,22),
                            'cQl3i':(-20,20),'cptb':(-40,40),
                            'ctG':(-3,3),   'cpQM':(-30,50),  
                            'ctlTi':(-4,4),'ctei':(-20,20),
                            'cQei':(-16,16),'cQlMi':(-17,17),
                            'cpQ3':(-20,12),'cbW':(-10,10)
                         }

    def log_subprocess_output(self,pipe,level):
        ### Pipes Popen streams to logging class ###
        for line in iter(pipe.readline, ''):
            if level=='info': logging.info(line.rstrip('\n'))
            if level=='error': logging.error(line.rstrip('\n'))

    def makeWorkspaceSM(self, datacard='EFT_MultiDim_Datacard.txt'):
        ### Generates a workspace from a datacard ###
        logging.info("Creating workspace")
        if not os.path.isfile(datacard):
            logging.error("Datacard does not exist!")
            sys.exit()
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['text2workspace.py',datacard,'-P','HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel',
                #'--PO','map=.*/ttll:mu_ttll[1,0,30]','--PO','map=.*/tHq:mu_tHq[1,0,40]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,30]','--PO','map=.*/ttH:mu_ttH[1,0,30]','--PO','map=.*/tllq:mu_tllq[1,0,30]',
                '--PO','map=.*/ttll:mu_ttll[1,0,30]','--PO','map=.*/tHq:mu_ttH[1,0,30]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,30]','--PO','map=.*/ttH:mu_ttH[1,0,30]','--PO','map=.*/tllq:mu_tllq[1,0,30]',
                #'--PO','map=.*/ttll:mu_ttll[1,0,5]','--PO','map=.*/tHq:mu_ttH[1,0,5]','--PO','map=.*/ttlnu:mu_ttlnu[1,0,5]','--PO','map=.*/ttH:mu_ttH[1,0,5]','--PO','map=.*/tllq:mu_tllq[1,0,5]',
                '-o','SMWorkspace.root']

        logging.info(" ".join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')

    def SMFit(self, name='.test', freeze=[], autoBounds=True, other=[]):
        ### Multidimensional fit ###
        args=['combine','-d','SMWorkspace.root','-v','2','--saveFitResult','-M','MultiDimFit','--cminDefaultMinimizerStrategy=2']
        if name:        args.extend(['-n','{}'.format(name)])
        if freeze:      args.extend(['--freezeParameters',','.join(freeze)])
        if autoBounds:  args.extend(['--autoBoundsPOIs=*'])
        if other:       args.extend(other)

        logging.info(" ".join(args))
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with SMFit.")
        sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])
        sp.call(['mv','multidimfit'+name+'.root','../fit_files/'])
        #if os.path.isfile('multidimfit'+name+'.root'):
        #    sp.call(['mv','multidimfit'+name+'.root','../fit_files/'])

    def SMGridScan(self, name='.test', crab=False, operators_POI=['mu_ttlnu'], operators_tracked=['mu_ttH','mu_ttll','mu_tllq'], points=500, freeze=False, other=[]):
        ### Runs deltaNLL Scan in two operators using CRAB ###
        logging.info("Doing grid scan...")

        args = ['combineTool.py','-d','SMWorkspace.root','-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=2']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if operators_POI:     args.extend(['--redefineSignalPOIs',','.join(operators_POI)])
        if operators_tracked: args.extend(['--trackParameters',','.join(operators_tracked)])
        if freeze:            args.extend(['--freezeParameters',','.join([op for op in ['mu_ttH','mu_ttll','mu_ttlnu','mu_tllq'] if op not in operators_POI])])
        if other:             args.extend(other)
        if crab:              args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points','2000'])
        logging.info(' '.join(args))

        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with gridScan.")
        if not crab: sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])

    def makeWorkspace16D(self, datacard='EFT_MultiDim_Datacard.txt'):
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
        
    def bestFit(self, name='.test', operators_POI=[], startValuesString='', freeze=False, autoBounds=True, other=[]):
        ### Multidimensional fit ###
        args=['combine','-d','16DWorkspace.root','-v','2','--saveFitResult','-M','MultiDimFit','-H','AsymptoticLimits','--cminPoiOnlyFit','--cminDefaultMinimizerStrategy=2']
        if name:              args.extend(['-n','{}'.format(name)])
        if operators_POI:     args.extend(['--redefineSignalPOIs',','.join(operators_POI)])
        args.extend(['--trackParameters',','.join([op for op in self.operators if op not in operators_POI])])
        if startValuesString: args.extend(['--setParameters',startValuesString])
        if freeze:            args.extend(['--freezeParameters',','.join([op for op in self.operators if op not in operators_POI])])
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

    def gridScan(self, name='.test', crab=False, operators_POI=['ctW','ctZ'], operators_tracked=['ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], points=5000, freeze=False, other=[]):
        ### Runs deltaNLL Scan in two operators using CRAB ###
        logging.info("Doing grid scan...")

        args = ['combineTool.py','-d','16DWorkspace.root','-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=2']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if operators_POI:     args.extend(['--redefineSignalPOIs',','.join(operators_POI)])
        if operators_tracked: args.extend(['--trackParameters',','.join(operators_tracked)])
        if freeze:            args.extend(['--freezeParameters',','.join([op for op in self.operators if op not in operators_POI])])
        if other:             args.extend(other)
        if crab:              args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points','2000'])
        logging.info(' '.join(args))

        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with gridScan.")
        if not crab: sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])

    def getBestValues2D(self, name, operators_POI=[], operators_tracked=[]):
        ### Gets values of operators for grid scan point with best deltaNLL ###
  
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
        for op in operators_POI:
            value = limitTree.GetLeaf(op).GetValue(0)
            startValues.append('{}={}'.format(op,value))
        for op in operators_tracked:
            value = limitTree.GetLeaf('trackedParam_'+op).GetValue(0)
            startValues.append('{}={}'.format(op,value))
        return ','.join(startValues)

    def getBestValues1D(self, basename, operators=[]):
        ### Gets values of operators for grid scan point with best deltaNLL ###
        if not operators:
            operators = self.operators

        startValues = []

        for op in operators:
  
            bestDeltaNLL=1000000;
            bestEntry=-1;

            fitFile = '../fit_files/higgsCombine{}.{}.MultiDimFit.root'.format(basename,op)
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

            value = limitTree.GetLeaf(op).GetValue(0)
            startValues.append('{}={}'.format(op,value))

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

    def batch1DScan(self, basename='.test', crab=False, operators_POI=[], points=100, freeze=False):
        ### For each operator, run a 1D deltaNLL Scan.
        if not operators_POI:
            operators_POI = self.operators

        for poi in operators_POI:
            self.gridScan('{}.{}'.format(basename,poi), crab, [poi], [pois for pois in self.operators if pois != poi], points, freeze)

    def batch2DScan(self, basename='.EFT.gridScan', freeze=False, points=50000, allPairs=False):
        ### For pairs of operators, runs deltaNLL Scan in two operators using CRAB ###

        # Use EVERY combination of operators
        if allPairs:
            operators_POI = self.operators

            for pois in itertools.combinations(operators_POI,2):
                operators_tracked = [op for op in self.operators if op not in pois]
                #print pois, operators_tracked
                self.gridScan(name='{}.{}{}'.format(basename,pois[0],pois[1]), crab=True, operators_POI=list(pois), operators_tracked=operators_tracked, points=points, freeze=freeze)

        # Use each operator only once
        if not allPairs:
            operators_POI = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]

            for pois in operators_POI:
                operators_tracked = [op for op in self.operators if op not in pois]
                #print pois, operators_tracked
                self.gridScan(name='{}.{}{}'.format(basename,pois[0],pois[1]), crab=True, operators_POI=list(pois), operators_tracked=operators_tracked, points=points, freeze=freeze)

    def batchResubmit1DScans(self, basename='.EFT.gridScan', operators_POI=[]):
        ### For each operator, attempt to resubmit failed CRAB jobs ###
        if not operators_POI:
            operators_POI = self.operators

        for poi in operators_POI:
            process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+poi], stdout=sp.PIPE, stderr=sp.PIPE)
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')

    def batchResubmit2DScans(self, basename='.EFT.gridScan', allPairs=False):
        ### For pairs of operators, attempt to resubmit failed CRAB jobs ###

        # Use EVERY combination of operators
        if allPairs:
            operators_POI = self.operators

            for pois in itertools.combinations(operators_POI,2):
                process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+pois[0]+pois[1]], stdout=sp.PIPE, stderr=sp.PIPE)
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')

        # Use each operator only once
        if not allPairs:
            operators_POI = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]

            for pois in operators_POI:
                process = sp.Popen(['crab','resubmit','crab_'+basename.replace('.','')+pois[0]+pois[1]], stdout=sp.PIPE, stderr=sp.PIPE)
                self.log_subprocess_output(process.stdout,'info')
                self.log_subprocess_output(process.stderr,'err')

    def batchRetrieve1DScans(self, basename='.test', operators_POI=[]):
        ### For each operator, retrieves finished 1D deltaNLL grid jobs, extracts, and hadd's into a single file ###
        if not operators_POI:
            operators_POI = self.operators

        for poi in operators_POI:
            self.retrieveGridScan('{}.{}'.format(basename,poi))

    def batchRetrieve2DScans(self, basename='.EFT.gridScan', allPairs=False):
        ### For pairs of operators, retrieves finished grid jobs, extracts, and hadd's into a single file ###

        # Use EVERY combination of operators
        if allPairs:
            operators_POI = self.operators
            for pois in itertools.combinations(operators_POI,2):
                self.retrieveGridScan('{}.{}{}'.format(basename,pois[0],pois[1]))

        # Use each operator only once
        if not allPairs:
            operators_POI = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
            for pois in operators_POI:
                self.retrieveGridScan('{}.{}{}'.format(basename,pois[0],pois[1]))

    def batchBestFit(self, basenamegrid='.EFT.gridScan', basenamefit='.EFT.gridScan', operators_POI=[], freeze=False):
        ### For each combination of operators, do a best fit using the new start point ###
        if not operators_POI:
            operators_POI = self.operators

        for pois in itertools.combinations(operators_POI,2):
            operators_tracked = [op for op in self.operators if op not in pois]
            startValuesString = self.getBestValues2D(name='{}.{}{}'.format(basenamegrid,pois[0],pois[1]), operators_POI=pois, operators_tracked=operators_tracked)
            self.bestFit(name='{}.{}{}'.format(basenamefit,pois[0],pois[1]), operators_POI=pois, startValuesString=startValuesString, freeze=freeze)

    def batch1DBestFit(self, basename='.EFT.SM.Float', operators=[]):
        ### For each operator, run a 1D fit with others frozen. Use start point from 1D scan with other floating. ###
        if not operators:
            operators = self.operators

        for op in operators:
            logging.info("Fitting for operator {}.".format(op))
            start_point = self.getBestValues1D(basename,[op])
            logging.info("Start value: {}".format(start_point))
            self.bestFit('{}.BestFit.{}'.format(basename,op), [op], start_point, True)

    def comparefits(self,basename='.EFT.SM.Float'):
        ### Compare results of different 1D scans ###
        tfiles = {}
        limits = {}
        bestFits = {} # Nested dict; bestFit of key1 according to key2
        for poi in self.operators:
            tfiles[poi] = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(basename+'.'+poi))
            limits[poi] = tfiles[poi].Get('limit')
            bestFits[poi] = {}
        for limitpoi in self.operators:
            limit = limits[limitpoi]
            bestNLL = (-1,1000000)
            for entry in range(limit.GetEntries()):
                limit.GetEntry(entry)
                currentNLL = limit.GetLeaf('deltaNLL').GetValue(0)
                if bestNLL[1] > currentNLL: bestNLL = (entry,currentNLL)
            print "Best entry for {} is {}.".format(limitpoi,bestNLL[0])
            limit.GetEntry(bestNLL[0])
            bestFits[limitpoi][limitpoi] = limit.GetLeaf(limitpoi).GetValue(0)
            trackedpois = list(self.operators)
            trackedpois.remove(limitpoi)
            for poi in trackedpois:
                bestFits[poi][limitpoi] = limit.GetLeaf('trackedParam_'+poi).GetValue(0)

        for poi in self.operators:
            trackedpois = list(self.operators)
            trackedpois.remove(poi)
            print("Best value of {}: {}".format(poi,bestFits[poi][poi]))
            for trackedpoi in trackedpois:
                print("Value according to {}: {}".format(trackedpoi,bestFits[poi][trackedpoi]))
                #print("Diff according to {}: {}".format(trackedpoi,bestFits[poi][poi]-bestFits[poi][trackedpoi]))
            

    def printBestFits(self, basename='.EFT.SM.Float', operators=[], simultaneous=True):
        ### Print a table of operators, their best fits, and their uncertainties ###
        if not operators:
            operators = self.operators

        fit_array = []

        if simultaneous:
            logging.info("Obtaining result of fit: multidimfit{}.root".format(basename))
            fit_file = ROOT.TFile.Open('../fit_files/multidimfit{}.root'.format(basename))
            fit = fit_file.Get('fit_mdf')

            for op in operators:
                roorealvar = fit.floatParsFinal().find(op)

                value = round(roorealvar.getVal(),6)
                err_sym =  round(roorealvar.getError(),6)
                err_low = round(roorealvar.getErrorLo(),6)
                err_high = round(roorealvar.getErrorHi(),6)

                fit_array.append((op,value,err_sym,err_low,err_high))
        else:
            for op in operators:
                logging.info("Obtaining result of fit: multidimfit{}.{}.root".format(basename,op))
                fit_file = ROOT.TFile.Open('../fit_files/multidimfit{}.{}.root'.format(basename,op))
                fit = fit_file.Get('fit_mdf')

                roorealvar = fit.floatParsFinal().find(op)

                value = round(roorealvar.getVal(),6)
                err_sym =  round(roorealvar.getError(),6)
                err_low = round(roorealvar.getErrorLo(),6)
                err_high = round(roorealvar.getErrorHi(),6)

                fit_array.append((op,value,err_sym,err_low,err_high))

        logging.info("WC, Best Fit Value, Symmetric Error, Low side of Asym Error, High side of Asym Error")

        for var in fit_array:
            print var
            logging.debug(var)

    def printIntervalFits(self, basename='.EFT.SM.Float', operators=[]):
        ### Print a table of operators, their best fits, and their uncertainties ###
        ### Use 1D scans instead of regular MultiDimFit ###
        if not operators:
            operators = self.operators

        ROOT.gROOT.SetBatch(True)

        fit_array = []

        canvas = ROOT.TCanvas()
        for op in operators:

            canvas.Clear()

            logging.debug("Obtaining result of scan: higgsCombine{}.{}.MultiDimFit.root".format(basename,op))
            fit_file = ROOT.TFile.Open('../fit_files/higgsCombine{}.{}.MultiDimFit.root'.format(basename,op))
            limit_tree = fit_file.Get('limit')

            limit_tree.Draw('2*deltaNLL:{}>>{}1DNLL(50,{},{})'.format(op,op,self.op_ranges[op][0],self.op_ranges[op][1]),'2*deltaNLL>-1','same')
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

            fit_array.append([op,[list(l) for l in zip(true_minimums,lowedges,highedges)]])

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
    #fitter.makeWorkspace16D('EFT_MultiDim_Datacard.txt')
    #fitter.bestFit(name='.EFT.SM.Float.preScan', operators_POI=['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], freeze=False, autoBounds=True)
    #fitter.gridScan(name='.EFT.SM.Float.gridScan.ctWctZ', crab=True, operators_POI=fitter.operators_POI, operators_tracked=fitter.operators_tracked, points=50000, freeze=False)
    #fitter.retrieveGridScan(name='.EFT.SM.Float.gridScan.ctWctZ')
    #startValuesString = fitter.getBestValues2D(name='.EFT.SM.Float.gridScan.ctWctZ', operators_POI=fitter.operators_POI, operators_tracked=fitter.operators_tracked)
    #startValuesString = fitter.getBestValues1D(basename='.EFT.SM.Float.gridScan', operators=fitter.operators)
    #fitter.bestFit(name='.EFT.SM.Float.postScan', operators_POI=['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], startValuesString=startValuesString, freeze=False, autoBounds=True)

    #logging.info("Logger shutting down!")
    #logging.shutdown()
