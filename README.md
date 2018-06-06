# EFTFit
This repository holds all of the custom files needed to run a proper EFT fit on the Govner TopEFT datacards. For convenience, sample datacards are provided in the test folder.

# Set up Repo
This package is designed to be used with the cms-govner CombineHarvester fork. Install within the same CMSSW release. See https://github.com/cms-govner/CombineHarvester

Otherwise, this package should be compatible with most CMSSW releases. It still requires the HiggsCombineTool package though. See https://cms-hcomb.gitbooks.io/combine/content/part1/#for-end-users-that-dont-need-to-commit-or-do-any-development

To install this package:

    cd $CMSSW_BASE/src/
    git clone https://github.com/cms-govner/EFTFit.git EFTFit
    
# Run the fit
To run a 1D Fit:

    #(1) Navigate to the test directory.
    #(2) Generate the fit function file (if changed):
    python ../scripts/FitConversion.py
    #(3) Edit ../scripts/1DEFTFit.csh to change the operator to fit for (change both lines, 3 locations)
    #(4) Run the fit:
    source ../scripts/1DEFTFit.csh

To run a test 2D Fit using a mixed quadratic function:

    #(1) Navigate to the test directory
    #(2) Generate the fit function file (if changed):
    python ../scripts/FitConversion2D.py
    #(3) Run the fit:
    source ../scripts/testFit2D.csh
