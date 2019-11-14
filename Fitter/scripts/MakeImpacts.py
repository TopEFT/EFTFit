import os
import sys
import logging
import datetime
import shutil

import EFTFit.Fitter.consts as CONST

from EFTFit.Fitter.LvlFormatter import LvlFormatter
from EFTFit.Fitter.CombineHelper import CombineMethod,FitAlgo,WorkspaceType,HelperOptions,CombineHelper

frmt = LvlFormatter()
logging.getLogger().setLevel(logging.DEBUG)

# Configure logging to also output to stdout
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(frmt)
logging.getLogger('').addHandler(console)

# Configure logging to an output file
def setup_logger(log_file):
    outlog = logging.FileHandler(filename=log_file,mode='w')
    outlog.setLevel(logging.DEBUG)
    outlog.setFormatter(frmt)
    logging.getLogger('').addHandler(outlog)

    logging.info("Log file: %s",log_file)

def main():
    # A template set of options for doing the SM signal fits, these will get passed (copied) to the actual
    #   instantiated CombineHelper object
    SM_SIGNAL_OPS = HelperOptions(
        ws_file      = 'SMWorkspace.root',
        model        = 'HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel',
        ws_type      = WorkspaceType.SM,
        sm_signals = [# This is used to define the 'map=./proc:mu_proc[...]' physics option in the text2workspace command
            ('ttH',  'mu_ttH',  [1]),
            ('tllq', 'mu_tllq', [1]),
            ('ttll', 'mu_ttll', [1]),
            ('ttlnu','mu_ttlnu',[1]),
            ('tHq',  'mu_ttH',  [1]),

            # If the list element in the tuple has length 3, CombineHelper will use those values to set corresponding PoI ranges
            # ('ttH',  'mu_ttH',  [1,0,30]),
            # ('tllq', 'mu_tllq', [1,0,30]),
            # ('ttll', 'mu_ttll', [1,0,30]),
            # ('ttlnu','mu_ttlnu',[1,0,30]),
            # ('tHq',  'mu_ttH',  [1,0,30]),
        ],
        prefit_value = 1.0,
        algo         = FitAlgo.Singles, # This is the default used for the MultiDimFit method
    )

    # This is always relative to the test directory of EFTFit, if sub-directories are specifed
    #   CombineHelper will make all intermediate directories as needed
    out_dir = 'example_impacts_output'

    # Now actually insantiate the CombineHelper object
    helper = CombineHelper(home=os.getcwd(),out_dir=out_dir,preset=SM_SIGNAL_OPS)

    # Important: This needs to come after the CombineHelper is insantiated, b/c of the logger in the
    #   helper class itself
    setup_logger(os.path.join(helper.output_dir,'out.log'))

    # Now modify some options, the only one that really matters is the histogram_file option, since the default is anatest10.root
    # Note1: The CombineHelper actually copies the settings from the templated options, so changing these
    #   settings won't modify the previously defined template object (if for example you used the template elsewhere)
    # Note2: The histogram file needs to actually exist in the hist_files directory of the TopEFT git repo!
    helper.setOptions(histogram_file='anatest31.root')

    # Can have multiple calls to setOptions to overwrite pre-existing options
    helper.setOptions(
        verbosity=2,        # Verbosity of the actual combine calls
        fake_data=False,    # Use real data
        use_central=False,  # Whether or not to use the central or private >signal< samples
        use_poi_ranges=False,   # If true, will always try to set limits for the poi ranges in the combine fit (not actually used for impact plots)
    )

    # If you specify the special keyword 'extend' to be True, then setOptions will extend w/e lists
    #   you give to the corresponding Helper options, rather then overwrite (only works for lists)
    helper.setOptions(extend=True,
        # other_options is just a list of combine options that will get added to the end of every combine call 
        other_options=[
            '--cminDefaultMinimizerStrategy=2',
            '--cminPoiOnlyFit',
            '--autoMaxPOIs=*'
        ]
    )

    # Clean-up the output directory if it was previously used
    # Important: This will remove everything from the corresponding directory except that which matches
    #   to at least one of the items in the 'keep' list. The search strings support regex matching
    helper.cleanDirectory(helper.output_dir,keep=["^EFT_MultiDim_Datacard.txt$","^16D.root$","^SMWorkspace.root$","^out.log$"])
    helper.make_datacard()  # Make the datacard from a histogram file via the TopEFT DatacardMaker class
    helper.make_workspace() # Make the RooWorkspace via the text2workspace script
    helper.loadDatacard(force=True) # (re-)load the datacard into the underlying DatacardReader class
                                    #   This is usually only needed if you want to make use of the
                                    #   'modifyDatacard()' method

    # Make the impact plots, can also specify combine options at this point if needed
    logging.info("Making impacts for all POIs: {}".format(pois))
    helper.runCombine(method=CombineMethod.IMPACTS,
        overwrite=False,    # Special keyword, if False the Helper options specfied here will only
                            #   take affect for this single 'runCombine' call and no others
        extend=False,       # Also supports the special 'extend' keyword
        # Change some arbitrary number of options
        robust_fit=False    # This is the default setting, but is just for example
    )

    copy_output = False
    if copy_output:
        # Note: Keep in mind that helper.output_dir != out_dir,
        #   but rather helper.output_dir == os.path.join(CONST.EFTFIT_TEST_DIR,out_dir)
        copy_dir = os.path.join(CONST.USER_DIR,'www',out_dir)
        # Copies w/e matches to one of the elements of 'rgx_lst' to the specified directory. As with
        #   the output directory, CombineHelper will make intermediate directories as needed
        helper.copyOutput(copy_dir,rgx_list=["^impacts_.*pdf$"],clean_directory=False)

    logging.info('Logger shutting down!')
    logging.shutdown()

if __name__ == "__main__":
    main()