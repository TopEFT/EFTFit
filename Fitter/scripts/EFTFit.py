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

    def log_subprocess_output(self,pipe,level):
        ### Pipes Popen streams to logging class ###
        for line in iter(pipe.readline, ''):
            if level=='info': logging.info(line.rstrip('\n'))
            if level=='error': logging.error(line.rstrip('\n'))

    def makeWorkspace(self, datacard='EFT_MultiDim_Datacard_SM.txt'):
        ### Generates a workspace from a datacard and fit parameterization file ###
        logging.info("Creating workspace")
        if not os.path.isfile(datacard):
            logging.error("Datacard does not exist!")
            sys.exit()
        CMSSW_BASE = os.getenv('CMSSW_BASE')
        args = ['text2workspace.py',datacard,'-P','EFTFit.Fitter.EFT16DModel:eft16D','--PO','fits='+CMSSW_BASE+'/src/EFTFit/Fitter/hist_files/16D_Parameterization.npy','-o','16D.root']
        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        
    def bestFit(self, name='.test', operators_POI=[], startValuesString='', freeze=False, autoBounds=True, other=[]):
        ### Multidimensional fit using default start values for operators (all 0) ###
        logging.info("Doing fit before grid scan...")
        args=['combine','-d','16D.root','-v','2','--saveFitResult','-M','MultiDimFit','-H','AsymptoticLimits','--cminPoiOnlyFit','--cminDefaultMinimizerStrategy=0']
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

        args = ['combineTool.py','-d','16D.root','-M','MultiDimFit','--algo','grid','--cminPreScan','--cminDefaultMinimizerStrategy=0']
        args.extend(['--points','{}'.format(points)])
        if name:              args.extend(['-n','{}'.format(name)])
        if operators_POI:     args.extend(['--redefineSignalPOIs',','.join(operators_POI)])
        if operators_tracked: args.extend(['--trackParameters',','.join(operators_tracked)])
        if freeze:            args.extend(['--freezeParameters',','.join([op for op in self.operators if op not in operators_POI])])
        if other:             args.extend(other)
        if crab:             args.extend(['--job-mode','crab3','--task-name',name.replace('.',''),'--custom-crab','custom_crab.py','--split-points','250'])
        logging.info(' '.join(args))

        process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
        with process.stdout,process.stderr:
            self.log_subprocess_output(process.stdout,'info')
            self.log_subprocess_output(process.stderr,'err')
        logging.info("Done with gridScan.")
        if not crab: sp.call(['mv','higgsCombine'+name+'.MultiDimFit.mH120.root','../fit_files/higgsCombine'+name+'.MultiDimFit.root'])

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

    def getBestValues(self, name, operators_POI=[], operators_tracked=[]):
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

    def batch1DScan(self, basename='.test', grid=False, operators_POI=[], points=100, freeze=False):
        ### For each operator, run a 1D deltaNLL Scan.
        if not operators_POI:
            operators_POI = self.operators

        for poi in operators_POI:
            self.gridScan('{}.{}'.format(basename,poi), grid, [poi], [], points, freeze)

    def retrieveBatch1DGridScans(self, basename='.test', operators_POI=[]):
        ### For each operator, retrieves finished 1D deltaNLL grid jobs, extracts, and hadd's into a single file ###
        if not operators_POI:
            operators_POI = self.operators

        for poi in operators_POI:
            retrieveGridScan('{}.{}'.format(basename,poi))

    def batch2DGridScan(self, basename='.test', operators_POI=[], points=5000, freeze=False):
        ### For each combination of operators, runs deltaNLL Scan in two operators using CRAB ###
        if not operators_POI:
            operators_POI = self.operators

        for pois in itertools.combinations(operators_POI,2):
            operators_tracked = [op for op in self.operators if op not in pois]
            #print pois, operators_tracked
            self.gridScan(name='{}.{}{}'.format(basename,pois[0],pois[1]), grid=True, operators_POI=list(pois), operators_tracked=operators_tracked, points=points, freeze=freeze)

    def retrieveBatch2DGridScans(self, basename='.test', operators_POI=[]):
        ### For each combination of operators, retrieves finished grid jobs, extracts, and hadd's into a single file ###
        if not operators_POI:
            operators_POI = self.operators

        for pois in itertools.combinations(operators_POI,2):
            retrieveGridScan('{}.{}{}'.format(basename,pois[0],pois[1]))

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
    #fitter.makeWorkspace('EFT_MultiDim_Datacard_SM.txt')
    #fitter.bestFit(name='.EFT.SM.Float.preScan', operators_POI=['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], freeze=False, autoBounds=True)
    #fitter.gridScan(name='.EFT.SM.Float.gridScan.ctWctZ', crab=False, operators_POI=fitter.operators_POI, operators_tracked=fitter.operators_tracked, points=5000, freeze=False)
    #fitter.retrieveGridScan(name='.EFT.SM.Float.gridScan.ctWctZ')
    #startValuesString = fitter.getBestValues(name='.EFT.SM.Float.gridScan.ctWctZ', operators_POI=fitter.operators_POI, operators_tracked=fitter.operators_tracked)
    #fitter.bestFit(name='.EFT.SM.Float.postScan', operators_POI=['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], startValuesString=startValuesString, freeze=False, autoBounds=True)

    #logging.info("Logger shutting down!")
    #logging.shutdown()
