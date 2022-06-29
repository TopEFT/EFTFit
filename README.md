# EFTFit
This repository holds all of the custom files needed to run a proper EFT fit on the Govner TopEFT datacards.

# Set up Repo
This package is designed to be used with the cms-govner CombineHarvester fork. Install within the same CMSSW release. See https://github.com/cms-govner/CombineHarvester

Otherwise, this package should be compatible with most CMSSW releases. It still requires the HiggsCombineTool package though. See https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/wiki/gettingstarted#for-end-users-that-dont-need-to-commit-or-do-any-development

To install this package:

    cd $CMSSW_BASE/src/
    git clone https://github.com/TopEFT/EFTFit.git EFTFit

# Directory Structure
**fit_files:** Output files from calls to combine<br/>
**hist_files:** Input histogram files for extracting fit parameterizations. Also, .npy parameterization file.<br/>
**interface:** C++ helper functions<br/>
**python:** Python helper functions<br/>
**scripts:** Top-level scripts for running and visualizing the fits<br/>
**test:** Directory to call scripts from

# Run the fit
To run a SM signal strength fit:

    #(1) Navigate to the test directory.
    #(2) Set up singularity+proxy for crab submission if using crab.
    #(3) Run the fit using EFTFitter class functions.
        # Call functions interactively from the command line with:
        python -i ../scripts/EFTFitter.py
    #Example workflow:
        fitter.makeWorkspaceSM('EFT_MultiDim_Datacard.txt')
        fitter.bestFitSM()
        fitter.batch1DScanSM('basejobname','condor'/'crab'/'')
        # These go fast enough batch submission isn't necessary
    #Wait for jobs to finish.
        fitter.batchRetrieve1DScansSM('basejobname','condor'/'crab') # Only if used batch submission
    #1D scans take a few minutes each.

To run a standard EFT fit:

    #(1) Navigate to the test directory.
    #(2) Generate the WC parameterization function file:
    python ../scripts/FitConversionEFT.py
    #(3) Set up singularity+proxy for crab submission if using crab.
    #(4) Run the fit using EFTFitter class functions.
        # Call functions interactively from the command line with:
        python -i ../scripts/EFTFitter.py
    #Example workflow:
        fitter.makeWorkspaceEFT('EFT_MultiDim_Datacard.txt')
        fitter.batch1DScanEFT('basejobname.Freeze','condor'/'crab') # Freeze other WCs 
        fitter.batch1DScanEFT('basejobname.Float','condor'/'crab') # Float other WCs 
        fitter.batch2DScanEFT('basejobname.Freeze','condor'/'crab',True) # Freeze other WCs 
        fitter.batch2DScanEFT('basejobname.Float','condor'/'crab',False) # Float other WCs
        Wait for jobs to finish.
        fitter.batchRetrieve1DScansEFT('basejobname.Freeze','condor'/'crab')
        fitter.batchRetrieve1DScansEFT('basejobname.Float','condor'/'crab')
        fitter.batchRetrieve2DScansEFT('basejobname.Freeze','condor'/'crab')
        fitter.batchRetrieve2DScansEFT('basejobname.Float','condor'/'crab')
    #1D scans take a few minutes each.
    #2D scans take 1-2 hours each.

# Visualize the fit
To make the standard array of SM plots:

    #(1) Navigate to the test directory.
    #(2) Use the batch functions to make them all automatically
        python -i ../scripts/EFTPlotter.py
        plotter.BatchLLPlot1DSM('basejobname')

To make the standard array of EFT plots:

    #(1) Navigate to the test directory.
    #(2) Use the batch functions to make them all automatically
        python -i ../scripts/EFTPlotter.py
        plotter.BatchOverlayPlot1DEFT('basejobname.Float','basejobname.Freeze')
        plotter.BestScanPlot('basejobname.Float','basejobname.Freeze')
        plotter.BatchBatch2DPlotsEFT('basejobname.Freeze') # Makes 2DLL and contour plots
        plotter.BatchBatch2DPlotsEFT('basejobname.Float') # Makes 2DLL and contour plots
    #The 2D plots will be stored in "Histos.basejobname.Float|Freeze/"

# Merging lepton flavors
In the combine fit we merge lepton flavors into the same bins. A script is available to do this automatically and is located [here](https://github.com/cms-govner/CombineHarvester/blob/master/TopEFT/scripts/CombineLepFlavors.py). The script assumes that the file to be converted, specified by `Filename`, is located in the `hist_files` sub-directory of the `CombineHarvester/TopEFT` module. The script will also place the output file in the same `hist_files` sub-directory using the `Filename` base name appended with the string `_MergeLepFl.root`. Below is an example of how to run the script from outside of the `CombineHarvest/TopEFT/scripts` location (assuming you have the git repo already cloned into your CMSSW release):
```python
import os
import shutil
sys.path.append(os.path.expandvars('${CMSSW_BASE}/src/CombineHarvester/TopEFT/scripts'))
from CombineLepFlavors import CombineLepFlavors

src_hist_loc = os.path.expanduser('~awightma/Public/anatest_files/anatest32.root')
dst_hist_loc = os.path.expandvars('${CMSSW_BASE}/src/CombineHarvester/TopEFT/hist_files')
shutil.copy(src_hist_loc,dst_hist_loc)

CLF = CombineLepFlavors()
CLF.Filename = 'anatest32.root'
CLF.execute()
```

# Using CombineHelper
The `CombineHelper` class is a helper class that wraps the various tools and scripts needed to convert a histogram ROOT file into inputs that can be passed directly to combine. The class itself hosts a set of configurable options maintained via the `HelperOptions` class. The user can instantiate their own `HelperOptions` instance and configure the options however they want and then pass that on to the `CombineHelper` instantiation as a preset configuration:
```python
user_ops = HelperOptions(
    name         = 'cleverName',
    ws_file      = '16D.root',
    model        = 'EFTFit.Fitter.EFTModel:eftmodel',
    prefit_value = 0.0,
)
user_ops.setOptions(
    verbosity=2,
    save_fitresult=True
)
helper = CombineHelper(out_dir="test_dir",preset=user_ops)
```
Alternatively, the user may choose to configure the options via the `CombineHelper` instance itself:
```python
helper = CombineHelper(out_dir="test_dir")
helper.setOptions(
    name           = 'cleverName',
    ws_file        = '16D.root',
    model          = 'EFTFit.Fitter.EFTModel:eftmodel',
    prefit_value   = 0.0,
    verbosity      = 2,
    save_fitresult = True
)
```
All `HelperOptions` options are basic python primitives such as strings, floats, ints, and bools or lists of such primitives. There are some important configuration options that make use of specific string names used within combine and so are defined using static classes located in [utils.py](https://github.com/cms-govner/EFTFit/blob/master/Fitter/python/utils.py) as `CombineMethod` and `FitAlgo`, which correspond to the named `HelperOptions` options `method` and `algo` respectively. There is a third static class defined in `utils.py` which is for the `ws_type` option called `WorkspaceType`, which is for swapping between the more standard SM signal strength style fits and the WC bin parameterized EFT style fits. The last important configuration option is the `histogram_file` option, which is the name of the ROOT histogram file that you would like to turn into a datacard and perform combine fits with. This file is assumed to be located in the directory defined by the `CONST.TOPEFT_DATA_DIR` global variable, which can be found in [consts.py](https://github.com/cms-govner/EFTFit/blob/master/Fitter/python/consts.py).

Once the `CombineHelper` class is configured, running all the processing steps and performing fits is as simple as:
```python
helper.make_datacard()
helper.make_workspace()
helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='ExFit1')
```
All arguments passed to the `runCombine` method with the exception of the special `overwrite` keyword are considered as additional `HelperOptions` configuration settings, which can be used to further adjust how combine is called during the `runCombine` call itself:
```python
helper.runCombine(method=CombineMethod.MULTIDIMFIT,name='ExFit2',algo=FitAlgo.NONE)
```
By default the extra options passed to the `runCombine` method will overwrite the corresponding `HelperOptions` settings. If the user specifies the `runCombine` option `overwrite=False`, the additional configuration options will only be used for that specific `runCombine` call and will be discarded for any subsequent `CombineHelper` method calls.

The user can refer to the [combine_helper.py](https://github.com/cms-govner/EFTFit/blob/master/Fitter/scripts/combine_helper.py) script for a detailed implementation example of the `CombineHelper` class, which makes use of a number of the useful convenience methods included in the `CombineHelper` class and also to the [HelperOptions](https://github.com/cms-govner/EFTFit/blob/master/Fitter/python/options.py#L86-L139) class definition for additional information on configuring the `CombineHelper` class.


# Making impact plots
Impact plots must be done in three stages:
### Initial fit
Run 
```python
fitter.ImpactInitialFit(workspace='ptz-lj0pt_fullR2_anatest17_noAutostats_withSys.root', wcs=[]):
```
to produce the initial fits. A blank `wcs` will run over all WCs.
### Nuisance fit
Run 
```python
fitter.ImpactNuisance(workspace='ptz-lj0pt_fullR2_anatest17_noAutostats_withSys.root', wcs=[]):
```
to fit each NP. A blank `wcs` will run over all WCs.
### Produce plots
Run 
```python
fitter.ImpactCollect(workspace='ptz-lj0pt_fullR2_anatest17_noAutostats_withSys.root', wcs=[]):
```
to collect all jobs and create the fin pdf plots.
