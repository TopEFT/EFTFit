# EFTFit
This repository holds all of the custom files needed to run a proper EFT fit on the Govner TopEFT datacards.

# Set up Repo
This package is designed to be used with the cms-govner CombineHarvester fork. Install within the same CMSSW release. See https://github.com/cms-govner/CombineHarvester

Otherwise, this package should be compatible with most CMSSW releases. It still requires the HiggsCombineTool package though. See https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/wiki/gettingstarted#for-end-users-that-dont-need-to-commit-or-do-any-development

To install this package:

    cd $CMSSW_BASE/src/
    git clone https://github.com/cms-govner/EFTFit.git EFTFit

# Directory Structure
fit_files: Output files from calls to combine
hist_files: Input histogram files for extracting fit parameterizations
interface: C++ helper functions
python: Python helper functions
scripts: Top-level scripts for running and visualizing the fits
test: Directory to call scripts from

# Run the fit
To run a standard 16D fit:

    #(1) Navigate to the test directory.
    #(2) Generate the fit function file:
    python ../scripts/FitConversion16D.py
    #(3) Modify the default operators to fit for in scripts/EFTFit.py
    #(4) Run the fit using class functions.
        #(a) Automatic: Add function calls to the bottom of EFTFit.py and call with
        python ../scripts/EFTFit.py
        #(b) Interactive: Call functions interactively from the command line with
        python -i ../scripts/EFTFit.py
    #Example workflow:
        fitter.makeWorkspace('EFT_MultiDim_Datacard_SM.txt')
        fitter.bestFit(name='.EFT.SM.Float.preScan', operators_POI=['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], operators_tracked=[], freeze=False, autoBounds=True)
        fitter.gridScan(name='.EFT.SM.Float.gridScan.ctWctZ', batch=True, operators_POI=fitter.operators_POI, operators_tracked=fitter.operators_tracked, points=5000, freeze=False)
        fitter.retrieveGridScan(name='.EFT.SM.Float.gridScan.ctWctZ')
        startValuesString = fitter.getBestValues(name='.EFT.SM.Float.gridScan.ctWctZ', operators_POI=fitter.operators_POI, operators_tracked=fitter.operators_tracked)
        fitter.bestFit(name='.EFT.SM.Float.postScan', operators_POI=['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'], operators_tracked=[], startValuesString=startValuesString, freeze=False, autoBounds=True)
        fitter.batch1DScan(basename='.EFT.SM.Float', grid=False, freeze=False)
        fitter.batch1DScan(basename='.EFT.SM.Float', grid=False, freeze=True)

# Visualize the fit
To make the standard array of plots:

    #(1) Navigate to the test directory.
    #(2) Use the batch functions to make them all automatically
        python -i ../scripts/EFTPlot.py
        Batch2DPlots(<gridScan 'name'>,<bestFit 'name'>)
        BatchOverlayLLPlot1D(<'basename' of frozen/floating files>, <'basename' of floating/frozen files>)
    #The 2D plots will also be stored in a root file named Histos.root
        
