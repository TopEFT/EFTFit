echo "Setting up your local area to run the TopEFT EFTFit module"

echo "Installing CMSSW"
export SCRAM_ARCH=slc7_amd64_gcc700
scram project CMSSW CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
scram b -j8

echo "Installing combine"
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit/
git checkout v8.2.0
scram b -j8
cd -

echo "Installing the TopEFT fork of CombineHarvester"
cd $CMSSW_BASE/src/
git clone https://github.com/TopEFT/EFTFit.git EFTFit
scram b -j8
cd -

echo "Installing the  EFTFit"
cd $CMSSW_BASE/src/
git clone git@github.com:TopEFT/CombineHarvester.git --branch crab_random
scram b -j8
cd -


echo "All done! Please see the READMEs for more details on how to run EFTFit"
