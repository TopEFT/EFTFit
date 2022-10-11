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
