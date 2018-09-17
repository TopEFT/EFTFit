# EFTFit
This repository holds all of the custom files needed to run a proper EFT fit on the Govner TopEFT datacards.

# Set up Repo
This package is designed to be used with the cms-govner CombineHarvester fork. Install within the same CMSSW release. See https://github.com/cms-govner/CombineHarvester

Otherwise, this package should be compatible with most CMSSW releases. It still requires the HiggsCombineTool package though. See https://cms-hcomb.gitbooks.io/combine/content/part1/#for-end-users-that-dont-need-to-commit-or-do-any-development

To install this package:

    cd $CMSSW_BASE/src/
    git clone https://github.com/cms-govner/EFTFit.git EFTFit
    
# Run the fit
To run a standard 16D fit:

    #(1) Navigate to the test directory.
    #(2) Generate the fit function file:
    python ../scripts/FitConversion16D.py
    #(3) Edit ../python/EFT16DModel.py L31 to change the operators to fit for
    #(4) Run the fit:
    source ../scripts/16DEFTMultiFit.csh
