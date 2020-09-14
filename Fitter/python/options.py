import logging
import copy

from utils import CombineMethod,FitAlgo,WorkspaceType

class OptionsBase(object):
    '''
        Base class that defines the methods for getting and setting options
    '''
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

class CombineSystematic(OptionsBase):
    '''
        A container class for specifying information relating to some particular Systematic
    '''
    def __init__(self,**kwargs):
        super(CombineSystematic,self).__init__()    # This initializes the logger
        self.bins  = []
        self.procs = []
        self.syst_name = ""
        self.syst_type = ""
        self.val_u = -1.0
        self.val_d = None

        self.setOptions(extend=False,**kwargs)

class HelperOptions(OptionsBase):
    '''
        A class for storing a named set of options for the CombineHelper class
    '''
    def __init__(self,**kwargs):
        super(HelperOptions,self).__init__()    # This initializes the logger

        # Generic Options
        self.verbosity    = 2       # The verbosity level to use in the combine methods
        self.mass         = 125

        self.fake_data      = True      # If we should use fake or real data when making the datacard
        self.use_central    = False     # Which signal samples to use from the anatest file (Only relevant for signal mu fits)
        self.robust_fit     = False     # Whether or not to use the --robustFit option
        self.save_fitresult = False     # Whether a RooFitResult object should be saved or not
        self.save_workspace = False     # Whether a RooWorkspace object should be saved or not
        self.use_poi_ranges = True      # If true we should limit the poi ranges in the combine fit
        self.stats_only     = False     # If true, ignore systematics constraint terms from the datacard

        self.histogram_file  = 'anatest10.root'                     # The histogram file to generate the datacard
        self.original_card   = 'EFT_MultiDim_Datacard.txt'          # The name of the original datacard
        self.datacard_file   = self.original_card                   # The name of the (potentially modified) datacard
        self.conversion_file = 'EFT_Parameterization.npy'           # The EFT 16D WC parameterization mapping
        self.ws_file         = '16D.root'                           # The name of the workspace root file
        self.model           = 'EFTFit.Fitter.EFTModel:eftmodel'    # The physics model used to make the RooWorkspace
        self.ws_type         = WorkspaceType.EFT
        self.method          = CombineMethod.NONE
        self.name            = 'EFT'

        self.phys_ops          = []
        self.drop_model_pois   = []         # A list of POIs to drop from the PhysicsModel when making the RooWorkspace
        self.freeze_parameters = []         # Parameters for the --freezeParameters option
        self.redefine_pois     = []         # Parameters for the --redefineSignalPOIs option
        self.track_parameters  = []         # Parameters for the --trackParameters option
        self.parameter_values  = []         # Parameter values for the --setParameters option
        self.auto_bounds_pois  = []         # Adjust bounds for the POIs if they end up close to the boundary
        self.sm_signals        = []
        self.exclude_nuisances = []         # A list of parameters to skip when running the Impacts method
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