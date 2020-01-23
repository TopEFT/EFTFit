import os

# Various path related constants
CMSSW_SRC   = os.path.expandvars("$CMSSW_BASE/src")
USER_DIR    = os.path.expanduser("~")
WEB_DIR     = os.path.join(USER_DIR,"www")

HIGGS_DIR      = os.path.join(CMSSW_SRC,"HiggsAnalysis/CombinedLimit")
HIGGS_TEST_DIR = os.path.join(HIGGS_DIR,"test")

COMBINE_DIR     = os.path.join(CMSSW_SRC,"CombineHarvester")
TOPEFT_DATA_DIR = os.path.join(COMBINE_DIR,"TopEFT/hist_files")
TOPEFT_TEST_DIR = os.path.join(COMBINE_DIR,"TopEFT/test")

EFTFIT_DIR      = os.path.join(CMSSW_SRC,"EFTFit/Fitter")
EFTFIT_DATA_DIR = os.path.join(EFTFIT_DIR,"data")
EFTFIT_HIST_DIR = os.path.join(EFTFIT_DIR,"hist_files")
EFTFIT_FITS_DIR = os.path.join(EFTFIT_DIR,"fit_files")
EFTFIT_TEST_DIR = os.path.join(EFTFIT_DIR,"test")