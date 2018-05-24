# EFTFit
This repository holds all of the custom files needed to run a proper EFT fit on the Govner TopEFT datacards. For convenience, a sample datacard is provided in the test folder.

To run a test 1D Fit:

    #(1) Navigate to the test directory.
    #(2) Generate the fit function file (if changed):
    python ../scripts/FitConversion.py
    #(3) Run the fit:
    source ../scripts/testFit.csh

To run a test 2D Fit using a mixed quadratic function:

    #(1) Navigate to the test directory
    #(2) Generate the fit function file (if changed):
    python ../scripts/FitConversion2D.py
    #(3) Run the fit:
    source ../scripts/testFit2D.csh
