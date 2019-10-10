import os
import logging
import shutil
import copy

import consts as CONST

from CombineHarvester.TopEFT.DatacardMaker import DatacardMaker
from DatacardReader import DatacardReader
from LvlFormatter import LvlFormatter
from utils import regex_match,run_command


class CombineMethod(object):
    NONE = "None"
    MULTIDIMFIT = "MultiDimFit"
    FITDIAGNOSTIC = "FitDiagnostics"
    IMPACTS = "Impacts"

class FitAlgo(object):
    NONE = "none"
    SINGLES = "singles"
    CROSS = "cross"
    CONTOUR2D = "contour2d"
    RANDOM = "random"
    FIXED = "fixed"
    GRID = "grid"
    IMPACT = "impact"

class WorkspaceType(object):
    EFT = "EFT"
    SM  = "SM"

class OptionsBase(object):
    PROTECTED = ['logger']  # Will need to re-work how we handle protected
                            # options for inherited classes
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.__protected = [
            '__protected',
            'logger'
        ]

    # Modify class instance data members
    def setOptions(self,extend=False,**kwargs):
        # extend: If true we extend list type options instead of overwriting them 
        for k,v in kwargs.iteritems():
            if not self.hasOption(k):
                self.logger.error("Unknown option: %s",k)
                raise RuntimeError
            elif k in self.__protected:
                self.logger.error("Tried to set protected option: %s",k)
                raise RuntimeError
            elif type(v) != type(self.__dict__[k]) and self.__dict__[k] is not None:
                self.logger.error("Found option with type mis-match: %s",k)
                raise RuntimeError
            if isinstance(v,list) and extend:
                self.__dict__[k].extend([x for x in v])
                continue
            self.__dict__[k] = copy.deepcopy(v)

    # Get a specific option
    def getOption(self,k):
        if not self.hasOption(k):
            self.logger.error("Unknown option: %s",k)
            raise RuntimeError
        return self.__dict__[k]

    # Return a deep copy dictionary of class instance data members
    def getCopy(self):
        # Note: We can't deepcopy logger objects, my workaround here feels really stupid...
        logger = self.__dict__.pop('logger')    # Temporarily remove the logger from the dictionary
        cpy = copy.deepcopy(self.__dict__)
        self.__dict__['logger'] = logger        # Add the logger back in
        return cpy

    # Check if the data member name is valid
    def hasOption(self,k):
        return self.__dict__.has_key(k)

    # Print a subset of the class data member names and their corresponding values
    def printOptions(self,rgx_lst=[]):
        # rgx_lst: A list of regular expressions to filter which options get printed,
        #          an empty list means all un-protected options should be printed
        to_print = []
        colw = 0
        for k in self.__dict__.keys():
            if k in self.__protected: continue
            if rgx_lst and len(regex_match([k],rgx_lst)) == 0: continue
            colw = max(colw,len(k))
            to_print.append(k)
        for k in to_print:
            line = "%s:" % (k.ljust(colw)),self.getOption(k)
            self.logger.info(line)

# A container class for specifying information relating some particular Systematic
class CombineSystematic(OptionsBase):
    def __init__(self,**kwargs):
        super(CombineSystematic,self).__init__()    # This initializes the logger
        self.bins  = []
        self.procs = []
        self.syst_name = ""
        self.syst_type = ""
        self.val_u = -1.0
        self.val_d = None

        self.setOptions(extend=False,**kwargs)

# A class for storing a named set of options for the CombineHelper class
class HelperOptions(OptionsBase):
    def __init__(self,**kwargs):
        super(HelperOptions,self).__init__()    # This initializes the logger

        # Generic Options
        self.verbosity    = 2       # The verbosity level to use in the combine methods
        self.mass         = 125

        self.fake_data      = True      # If we should use fake or real data when making the datacard
        self.robust_fit     = False     # Whether or not to use the --robustFit option
        self.save_fitresult = False     # Whether a RooFitResult object should be saved or not
        self.save_workspace = False     # Whether a RooWorkspace object should be saved or not

        self.histogram_file  = 'anatest10.root'                     # The histogram file to generate the datacard
        self.original_card   = 'EFT_MultiDim_Datacard.txt'          # The name of the original datacard
        self.datacard_file   = self.original_card                   # The name of the (potentially modified) datacard
        self.conversion_file = '16D_Parameterization.npy'           # The EFT 16D WC parameterization mapping
        self.ws_file         = '16D.root'                           # The name of the workspace root file
        self.model           = 'EFTFit.Fitter.EFT16DModel:eft16D'   # The physics model used to make the RooWorkspace
        self.ws_type         = WorkspaceType.EFT
        self.method          = CombineMethod.NONE
        self.name            = 'EFT'

        self.phys_ops          = []
        self.freeze_parameters = []         # Parameters for the --freezeParameters option
        self.redefine_pois     = []         # Parameters for the --redefineSignalPOIs option
        self.track_parameters  = []         # Parameters for the --trackParameters option
        self.parameter_values  = []         # Parameter values for the --setParameters option
        self.auto_bounds_pois  = []         # Adjust bounds for the POIs if they end up close to the boundary
        self.sm_signals        = []
        self.other_options     = []         # A list of additional options. These should be fully
                                            # formed options e.g. '--cminDefaultMinimizerStrategy=2'
        # FitDiagnostic Options
        self.prefit_value = 0.0     # The prefit value of the POI used

        self.minos_arg = 'poi'      # Which parameters to compute MINOS errors for

        # MultiDimFit Options
        self.float_other_pois = False   # Whether or not the other POIs should be floating or fixed
        self.fast_scan        = False   # Whether or not to do a fast scan, evaluating the likelihood without profiling it
        self.robust_hesse     = False   # Use a more robust calculation of the hessian/covariance matrix

        self.algo = FitAlgo.NONE

        self.set_parameters = []        # List of parameters to set with the --parameters (or -P) option

        self.setOptions(extend=False,**kwargs)  # Overwrite any default options with those passed to the constructor

# Helper class for running various combine related commands
class CombineHelper(object):
    def __init__(self,home_dir,out_dir="test_dir",preset=None):
        self.logger = logging.getLogger(__name__)

        self.home_dir = home_dir
        self.output_dir = os.path.join(CONST.EFTFIT_TEST_DIR,out_dir)   # Note: This path is relative to the 'test' directory

        if not os.path.exists(self.output_dir):
            self.logger.info("Making output directory: %s",self.output_dir)
            os.makedirs(self.output_dir)

        self.poi_ranges = {}
        self.default_range = [-5.0,5.0]

        self.dc_maker = DatacardMaker()
        self.dc_reader = DatacardReader()

        self.ops = HelperOptions()
        if not preset is None: self.setOptions(preset=preset)

    def setOptions(self,preset=None,extend=False,**kwargs):
        # preset: A HelperOptions object with preset values for all the options
        # extend: If true, list type options will be extended instead of replaced
        if not preset is None:
            self.ops = HelperOptions(**preset.getCopy())
            return
        self.ops.setOptions(extend=extend,**kwargs)

    def setPOIRange(self,poi,lo,hi):
        self.poi_ranges[poi] = [lo,hi]

    def getPOIRangeStr(self,pois):
        poi_ranges = ''
        for idx,poi in enumerate(pois):
            lo,hi = self.default_range
            if self.poi_ranges.has_key(poi):
                lo,hi = self.poi_ranges[poi]
            if idx: poi_ranges += ":"
            poi_ranges += poi + "=%.2f,%.2f" % (lo,hi)
        return poi_ranges

    # Attempt to parse the text datacard into the dc_reader
    def loadDatacard(self,force=False):
        if self.dc_reader.hasCard() and not force:
            # The card has already been loaded
            return
        datacard = self.ops.getOption('datacard_file')
        card_file = os.path.join(self.output_dir,datacard)
        if not os.path.exists(card_file):
            self.logger.error("Unable to load datacard file %s.",card_file)
            return
        self.dc_reader.load(card_file)

    def chdir(self,dir_path):
        if os.getcwd() == dir_path: return
        self.logger.info("Moving to: %s",dir_path)
        os.chdir(dir_path)

    def cleanDirectory(self,target_directory,keep=[],remove=[]):
        # NOTE: This only works on a flat directory structure, it wont remove files in sub-dirs
        initial_dir = os.getcwd()
        if not os.path.exists(target_directory):
            self.logger.error("Failed to clean directory. Missing directory: %s",target_directory)
            return
        self.chdir(target_directory)

        self.logger.info("Cleaning directory: %s",target_directory)
        lst = os.listdir('.')
        for f in lst:
            if os.path.isdir(f): continue
            if len(keep) and len(regex_match([f],keep)):
                # Keep files which match any of the 'keep' list (supersedes remove)
                self.logger.info("Keeping file: %s" % (f))
                continue
            if len(remove) and not len(regex_match([f],remove)):
                # Skip files which don't match any of the 'remove' list
                self.logger.info("Keeping file: %s" % (f))
                continue
            self.logger.info("Removing file: %s" % (f))
            os.remove(f)
        self.chdir(initial_dir)

    # Copies all files in the output directory that match one of the given regex patterns to a target directory
    def copyOutput(self,tar_dir,rgx_list=[],clean_directory=False):
        # clean_directory: Whether the target directory should be cleaned before copying files
        # rgx_list: If this list is empty, we will copy all non-directory files
        self.logger.info("Copying output to: %s",tar_dir)
        rel_path = os.path.relpath(tar_dir,CONST.USER_DIR)
        if rel_path.split('/')[0] == '..':
            self.logger.error("Invalid target directory. The target directory must be a sub-directory of the user: %s",CONST.USER_DIR)
            return
        self.chdir(self.output_dir)
        to_copy = []
        for out in sorted(os.listdir('.')):
            fpath = os.path.join('.',out)
            if os.path.isdir(fpath): continue
            if len(rgx_list) and not len(regex_match([out],rgx_list)):
                # The file didn't match any of our rgxs
                continue
            to_copy.append(out)
        if len(to_copy) == 0:
            self.logger.info("Found nothing to copy!")
            return
        if not os.path.exists(tar_dir):
            self.logger.info("Making directory to copy to: %s",tar_dir)
            os.makedirs(tar_dir)
        if clean_directory:
            self.cleanDirectory(tar_dir)
        for f in to_copy:
            self.logger.info("Copying: %s",f)
            dst = os.path.join(tar_dir,f)
            shutil.copy(f,dst)

    # Modify an existing datacard, save it, then re-load it
    def modifyDatacard(self,new_card,remove_systs=[],add_systs=[],filter_bins=[]):
        self.loadDatacard() # Try to load the default datacard (if we already loaded a card this does nothing)
        if not self.dc_reader.hasCard():
            self.logger.error("Unable to modify datacard. No card has been loaded!")
            return
        old_card = self.ops.getOption('datacard_file')
        self.logger.info("Modifying datacard %s...",old_card)
        self.chdir(self.output_dir)
        if filter_bins: self.dc_reader.filterBins(bins=filter_bins)
        for syst in remove_systs:
            procs = syst.getOption('procs')
            bins  = syst.getOption('bins')
            syst_name = "^%s$" % (syst.getOption('syst_name'))  # Only remove exact matches
            self.dc_reader.removeSyst(procs=procs,bins=bins,syst_name=syst_name)
        for syst in add_systs:
            procs     = syst.getOption('procs')
            bins      = syst.getOption('bins')
            syst_name = syst.getOption('syst_name')
            val_u     = syst.getOption('val_u')
            val_d     = syst.getOption('val_d')
            syst_type = syst.getOption('syst_type')
            self.dc_reader.addSyst(procs=procs,bins=bins,syst_name=syst_name,val_u=val_u,val_d=val_d,syst_type=syst_type)
        self.logger.info("Creating new datacard: %s",new_card)
        self.setOptions(datacard_file=new_card)
        self.dc_reader.write(new_card)
        self.loadDatacard(force=True)
        # Write/Load a second time to remove empty systematics from the datacard
        self.dc_reader.write(new_card)
        self.loadDatacard(force=True)

    # Run combine using the configured options
    def runCombine(self,overwrite=True,extend=False,**kwargs):
        # overwrite: Whether or not the adjusted options should be kept after the runCombine call finishes
        # extend: If true, list type options will be extended instead of replaced
        if not overwrite:
            tmp_ops = HelperOptions(**self.ops.getCopy())

        self.setOptions(extend=extend,**kwargs)   # Adjust helper options on each call
        method = self.ops.getOption('method')
        if method == CombineMethod.NONE:
            pass
        elif method == CombineMethod.FITDIAGNOSTIC:
            self.make_fitdiagnostics()
        elif method == CombineMethod.MULTIDIMFIT:
            self.make_multidimfit()
        elif method == CombineMethod.IMPACTS:
            self.make_impact_plots()
        else:
            self.logger.error("Unknown combine method: %s",method)
            raise RuntimeError

        if not overwrite:
            self.setOptions(preset=tmp_ops)

    # Call DatacardMaker() to create the initial datacard text file
    def make_datacard(self):
        card_file = self.ops.getOption('datacard_file')
        hist_file = self.ops.getOption('histogram_file')
        fake_data = self.ops.getOption('fake_data')

        self.logger.info("Creating datacard %s...",card_file)
        self.chdir(self.output_dir)
        self.dc_maker.outf = card_file
        fpath = os.path.join(CONST.TOPEFT_DATA_DIR,hist_file)
        self.logger.info("Using Histogram File: %s" % (fpath))
        self.dc_maker.make(fpath,fake_data)
        self.loadDatacard()

    # Call FitConversion16D.py script to create the parameterization file
    def make_parameterization(self):
        self.logger.info("Making parameterization file...")

        file  = self.ops.getOption('histogram_file')
        fpath = os.path.join(CONST.TOPEFT_DATA_DIR,file)
        script_path = os.path.join(CONST.EFTFIT_TEST_DIR,'../scripts/FitConversion16D.py')
        args  = ['python',script_path,fpath]

        self.logger.info("FitConversion command: %s",' '.join(args))
        run_command(args)

    def make_workspace(self):
        '''
            Description:
                Create a RooWorkspace and save it to a root file
            Can directly modify:
                None
            Can indirectly modify:
                self.dc_maker.hp.operators_fakedata --> DatacardMaker.setOperators()
                self.poi_ranges --> self.setPOIRange()
            Depends on:
                self.ops.ws_file: The name of the output file
                self.ops.datacard_file: The name of the input datacard file
                self.ops.model: The physics model to use
                self.ops.phys_ops: The physics options relevant to the physics model to use
                self.ops.ws_type: Modifies the fitting behavior to either fit for signal strengths
                    (WorkspaceType.SM) or to fit for EFT WC values (WorkspaceType.EFT) 
        '''
        self.logger.info("Making workspace file...")
        self.chdir(self.output_dir)

        ws_file  = self.ops.getOption('ws_file')
        datacard = self.ops.getOption('datacard_file')
        model    = self.ops.getOption('model')
        ws_type  = self.ops.getOption('ws_type')
        phys_ops = [x for x in self.ops.getOption('phys_ops')]

        if ws_type == WorkspaceType.EFT:
            self.make_parameterization()    # Make sure we generated the parameterization file
            conv_file = self.ops.getOption('conversion_file')
            fits_file = os.path.join(CONST.EFTFIT_HIST_DIR,conv_file)
            pois_to_fit = ','.join(self.dc_maker.getOperators())
            phys_ops.extend(['fits=%s' % (fits_file),'operators=%s' % (pois_to_fit)])
        elif ws_type == WorkspaceType.SM:
            sm_signals = self.ops.getOption('sm_signals')
            tmp = set()
            for p,mu,lst in sm_signals:
                self.setPOIRange(mu,lst[1],lst[2])
                tmp.add(mu)
            self.dc_maker.setOperators(list(tmp))
            phys_ops.extend(['map=.*/%s:%s[%d,%d,%d]' % (proc,mu,l[0],l[1],l[2]) for proc,mu,l in sm_signals])
        else:
            self.logger.error("Unknown workspace type: %s",ws_type)
            raise RuntimeError

        args = ['text2workspace.py',datacard]
        args.extend(['-o',ws_file])
        args.extend(['-P',model])
        for po in phys_ops: args.extend(['--PO',po])

        self.logger.info("text2workspace command: %s",' '.join(args))
        run_command(args)

    # Run combine using the FitDiagnostic method
    def make_fitdiagnostics(self):
        self.logger.info("Making fit diagnostic...")
        self.chdir(self.output_dir)

        ws_file    = self.ops.getOption('ws_file')
        method     = self.ops.getOption('method')
        verb       = self.ops.getOption('verbosity')
        name       = self.ops.getOption('name')
        minos_arg  = self.ops.getOption('minos_arg')
        pf_val     = self.ops.getOption('prefit_value')
        redef_pois = self.ops.getOption('redefine_pois')
        other_ops  = self.ops.getOption('other_options')

        args = ['combine',ws_file]
        args.extend(['-n',name])
        args.extend(['-M',method])
        args.extend(['-v','%d' % (verb)])
        args.extend(['--minos',minos_arg])
        args.extend(['--preFitValue','%.2f' % (pf_val)])
        if redef_pois: args.extend(['--redefineSignalPOIs',','.join(redef_pois)])
        if other_ops: args.extend([x for x in other_ops])
        
        self.logger.info("Combine command: %s", ' '.join(args))
        run_command(args)

    # Run combine using the MultiDimFit method
    def make_multidimfit(self):
        self.logger.info("Making MultiDimFit...")
        self.chdir(self.output_dir)

        ws_file    = self.ops.getOption('ws_file')
        method     = self.ops.getOption('method')
        verb       = self.ops.getOption('verbosity')
        name       = self.ops.getOption('name')
        algo       = self.ops.getOption('algo')
        frz_lst    = self.ops.getOption('freeze_parameters')
        trk_pars   = self.ops.getOption('track_parameters')
        redef_pois = self.ops.getOption('redefine_pois')
        param_vals = self.ops.getOption('parameter_values')
        other_ops  = self.ops.getOption('other_options')

        pois   = self.dc_maker.getOperators()
        ranges = self.getPOIRangeStr(pois)

        args = ['combine',ws_file]
        args.extend(['-n',name])
        args.extend(['-M',method])
        args.extend(['-v','%d' % (verb)])
        args.extend(['--algo=%s' % (algo)])
        args.extend(['--setParameterRanges',ranges])
        if frz_lst: args.extend(['--freezeParameters',','.join(frz_lst)])
        if trk_pars: args.extend(['--trackParameters',','.join(trk_pars)])
        if redef_pois: args.extend(['--redefineSignalPOIs',','.join(redef_pois)])
        if param_vals: args.extend(['--setParameters',','.join(param_vals)])
        if self.ops.getOption('save_fitresult'): args.extend(['--saveFitResult'])
        if self.ops.getOption('save_workspace'): args.extend(['--saveWorkspace'])
        if self.ops.getOption('robust_fit'): args.extend(['--robustFit','1'])
        if other_ops: args.extend([x for x in other_ops])

        self.logger.info("Combine command: %s", ' '.join(args))
        run_command(args)

    def make_impact_plots(self):
        '''
            Description:
                Run CombineTools using the Impacts method to generate impact plots
            Can directly modify:
                None
            Can indirectly modify:
                None
            Depends on:
                self.ops.ws_file: The name of the input dataset file
                self.ops.ws_type: Used to modify the output name
                self.ops.method: The method option (-M) to use for the combineTool, should be "Impacts"
                self.ops.verbosity: The verbosity setting (-v) for the combineTool
                self.ops.mass: The mass option (-m) of combineTool, this only modifies the name of the outputs
                self.ops.name: Currently unused
                self.ops.freeze_parameters: Passed to the '--freezeParameters' option of combineTool
                self.ops.redefine_pois: Passed to the '--redefineSignalPOIs' option of combineTool
        '''
        self.logger.info("Making impact plots...")
        self.chdir(self.output_dir)

        self.cleanDirectory(self.output_dir,remove=['^higgsCombine_paramFit_.*','^higgsCombine_initialFit_.*'])

        ws_file    = self.ops.getOption('ws_file')
        ws_type    = self.ops.getOption('ws_type')
        method     = self.ops.getOption('method')
        verb       = self.ops.getOption('verbosity')
        mass       = self.ops.getOption('mass')
        name       = self.ops.getOption('name')
        frz_lst    = self.ops.getOption('freeze_parameters')
        redef_pois = self.ops.getOption('redefine_pois')
        auto_pois  = self.ops.getOption('auto_bounds_pois')
        other_ops  = self.ops.getOption('other_options')    # Note: These options will be applied to both
                                                            #       the '--doInitialFit' and '--doFits' steps

        # Do the initial fits
        args = ['combineTool.py','-M',method,'--doInitialFit']
        args.extend(['-d',ws_file,'-n',ws_type])
        args.extend(['-v','%d' % (verb),'-m','%d' % (mass)])
        if frz_lst: args.extend(['--freezeParameters',','.join(frz_lst)])
        if redef_pois: args.extend(['--redefineSignalPOIs',','.join(redef_pois)])
        if auto_pois: args.extend(['--autoBoundsPOIs=%s' % (','.join(auto_pois))])
        if other_ops: args.extend([x for x in other_ops])
        if self.ops.getOption('robust_fit'): args.extend(['--robustFit','1'])
        self.logger.info("Initial Fits command: %s", ' '.join(args))
        run_command(args)

        # Do a fit for each nuisance parameter in the datacard
        args = ['combineTool.py','-M',method,'--doFits','--allPars']
        args.extend(['-d',ws_file,'-n',ws_type])
        args.extend(['-v','%d' % (verb),'-m','%d' % (mass)])
        if frz_lst: args.extend(['--freezeParameters',','.join(frz_lst)])
        if redef_pois: args.extend(['--redefineSignalPOIs',','.join(redef_pois)])
        if auto_pois: args.extend(['--autoBoundsPOIs=%s' % (','.join(auto_pois))])
        if other_ops: args.extend([x for x in other_ops])
        if self.ops.getOption('robust_fit'): args.extend(['--robustFit','1'])
        self.logger.info("Do Fits command: %s", ' '.join(args))
        run_command(args)

        # Create a json file using as input the files generated in the previous two steps
        args = ['combineTool.py','-M',method,'-o','impacts.json','--allPars']
        args.extend(['-d',ws_file,'-n',ws_type])
        args.extend(['-v','%d' % (verb),'-m','%d' % (mass)])
        if redef_pois: args.extend(['--redefineSignalPOIs',','.join(redef_pois)])
        self.logger.info("To JSON command: %s", ' '.join(args))
        run_command(args)

        # Create the impact plot pdf file
        pois = [x for x in redef_pois] if redef_pois else [x for x in self.dc_maker.getOperators()]
        for poi in pois:
            outf = 'impacts_%s' % (poi)
            args = ['plotImpacts.py','-i','impacts.json','--POI','%s' % (poi),'-o',outf]
            self.logger.info("%s POI command: %s",poi,' '.join(args))
            run_command(args)

if __name__ == "__main__":
    frmt = LvlFormatter()
    logging.getLogger().setLevel(logging.DEBUG)

    # Configure logging to also output to stdout
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(frmt)
    logging.getLogger('').addHandler(console)

    # Examples of how to define templated options
    EFT_OPS = HelperOptions(
        ws_file      = '16D.root',
        model        = 'EFTFit.Fitter.EFT16DModel:eft16D',
        ws_type      = WorkspaceType.EFT,
        prefit_value = 0.0
    )

    sm_signals = [
        ('ttll', 'mu_ttll', [1,0,30]),
        ('tHq',  'mu_ttH',  [1,0,30]),  # Ties tHq process to be scaled by ttH signal
        ('ttlnu','mu_ttlnu',[1,0,30]),
        ('ttH' , 'mu_ttH',  [1,0,30]),
        ('tllq', 'mu_tllq', [1,0,30])
    ]

    SM_OPS = HelperOptions(
        ws_file      = 'SMWorkspace.root',
        model        = 'HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel',
        ws_type      = WorkspaceType.SM,
        sm_signals   = [x for x in sm_signals],
        prefit_value = 1.0,
        algo         = FitAlgo.SINGLES
    )

    use_fake_data = True

    # Create a new options object from a template and modify it however you want
    helper_ops = HelperOptions(**SM_OPS.getCopy())
    helper_ops.setOptions(verbosity=2,fake_data=use_fake_data,save_fitresult=True)

    # Create our actual combine helper class using the options we configured above
    out_dir = os.path.join('ana14','combine_testing')   # Note: The output directory path is relative to the 'test' directory!
    helper = CombineHelper(os.getcwd(),out_dir=out_dir,preset=helper_ops)

    # Configure logging to an output file
    # TODO: Would probably make more sense to put this in the CombineHelper class?
    #       Maybe not, since we don't want multiple loggers logging to the same file
    #       at potentially the same time. Need to get a better understanding of how
    #       the logging module works...
    log_file = os.path.join(helper.output_dir,'out.log')
    outlog = logging.FileHandler(filename=log_file,mode='w')
    outlog.setLevel(logging.DEBUG)
    outlog.setFormatter(frmt)
    logging.getLogger('').addHandler(outlog)

    # Can make further changes to the options later on
    hist_file = 'anatest14.root'        # Note: Looks in the CombineHarvester/TopEFT/hist_files directory for this file
    helper.setOptions(histogram_file=hist_file)
    helper.setOptions(robust_fit=False)
    helper.setOptions(extend=True,verbosity=3,other_options=['--cminDefaultMinimizerStrategy=2'])

    # Do some fitting!
    helper.make_datacard()
    helper.make_workspace()
    helper.runCombine(method=CombineMethod.FITDIAGNOSTIC,name='Prefit',minos_arg='all')
    helper.setOptions(# Can modify the options between subsequent combine calls
        extend=True,
        other_options=['--cminDefaultMinimizerStrategy=0','--cminPoiOnlyFit']
    )
    helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='Postfit')