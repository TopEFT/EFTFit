#!/bin/bash
cmssw=$1

echo -e "\n"
echo "##################################################"
echo "#                                                #"
echo "# Executing the super awesome mega EFTFit script #"
echo "#                                                #"
echo "##################################################"
echo -e "\n"

source /cvmfs/cms.cern.ch/crab3/crab.sh
## CMSSW part
if [[ $PWD == *"CMSSW_10_2_13"* ]]; then
  # Already in a CMSSW environment
  cmsenv
fi
if [[ -z $CMSSW_BASE && -z $cmssw && -d "CMSSW_10_2_13" ]]; then
    echo "Please specify a CMSSW path or cd into your local CMSSW directory and run: \`cmsenv\`"
    exit
fi
if [[ ! -z $CMSSW_BASE && -z $cmssw && ! -d "CMSSW_10_2_13" ]]; then
  cmssw=$CMSSW_BASE
  echo $cmssw
fi
if [[ -d $cmssw && $cmssw == *"CMSSW_10_2_13"* ]]; then
  echo "Using CMSSW installed at: ${cmssw}"
  cd $cmssw/src
  cmsenv
elif [[ ! -d $cmssw ]]; then
  # Install CMSSW in the specified directory
  echo "Installing CMSSW in: ${cmssw}"
  export SCRAM_ARCH=slc7_amd64_gcc700
  scram project CMSSW CMSSW_10_2_13
  cd CMSSW_10_2_13/src
  cmsenv
  scram b -j8
fi

## combine part
if [[ ! -d $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit ]]; then
  echo "Installing combine"
  git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
  cd HiggsAnalysis/CombinedLimit/
  git checkout v8.2.0
  scram b -j8
  cd -
fi


## CombineHarvester part
if [[ ! -d $CMSSW_BASE/src/CombineHarvester ]]; then
  # Install CombineHarvester
  echo "Installing CombineHarvester"
  git clone https://github.com/cms-analysis/CombineHarvester.git
  cd CombineHarvester
  scram b -j8
  cd -
fi

## EFTFit part
if [[ ! -d $CMSSW_BASE/src/EFTFit ]]; then
  echo "Installing the  EFTFit"
  cd $CMSSW_BASE/src/
  git clone https://github.com/TopEFT/EFTFit.git
  scram b -j8
  cd -
fi

cd $CMSSW_BASE/src/CombineHarvester/
cp $CMSSW_BASE/src/EFTFit/Fitter/test/crab_random.patch .
if ! git apply --reverse --check crab_random.patch; then
  echo "Checking to see if the patch is applied"
  echo "The above \"error\" simply means the patch must be applied."
  gdiff=$(git diff --name-only | wc -l)
  if [[ $gdiff -gt 0 ]]; then
    echo "### WARNING ###"
    echo "I've found uncommited changes. I will stash these before applying our patch to the CombineHarvester"
    echo "To view these changes, cd to the CombineHarvester directory and run: \`git stash show -p\`"
    echo "To recover them (if you're sure they won't conflict with our patch, run: \`git stash pop\`)"
    echo ""
    git stash
  fi
  git checkout b7ca691 # This is a SSH hash based on the main branch
  # Apply patch to CombineToolBase.py
  git apply crab_random.patch
  scram b -j8
  cd -
fi

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/
cp $CMSSW_BASE/src/EFTFit/Fitter/test/combine_rnd_nll.patch .
if ! git apply --reverse --check combine_rnd_nll.patch; then
  echo "Checking to see if the patch is applied"
  echo "The above \"error\" simply means the patch must be applied."
  gdiff=$(git diff --name-only | wc -l)
  if [[ $gdiff -gt 0 ]]; then
    echo "### WARNING ###"
    echo "I've found uncommited changes. I will stash these before applying our patch to the combine"
    echo "To view these changes, cd to the combine directory and run: \`git stash show -p\`"
    echo "To recover them (if you're sure they won't conflict with our patch, run: \`git stash pop\`)"
    echo ""
    git stash
  fi
  git checkout v8.2.0
  # Apply patch to src/MultiDimFit.cc
  git apply combine_rnd_nll.patch
  scram b -j8
  cd -
fi

## Initialize voms proxy
echo "Initializing voms proxy. Please make sure this line succeeds before tyring to submit to crab!"
echo "If the initialization fails, but you have a valid proxy certificate, rerun:"
echo "\`voms-proxy-init --rfc --voms cms -valid 192:00\`"
voms-proxy-init --rfc --voms cms -valid 192:00

date=`date +"%m%d%y_%H%m%S"`
cd $CMSSW_BASE/src/EFTFit/Fitter/test/
wget -nc -O ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root https://cernbox.cern.ch/remote.php/dav/public-files/rifeNMnShlOdNYc/ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root 
combineTool.py -d $CMSSW_BASE/src/EFTFit/Fitter/test/ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root -M MultiDimFit --algo random --skipInitialFit --cminDefaultMinimizerStrategy=0 -s -1 --points 1000000 -n .${date}.EFT.Float.DNN.1M --job-mode crab3 --task-name ${date}EFTFloatDNN1M --custom-crab custom_crab.py --split-points 100 --setParameterRanges cQQ1=-5.0,5.0:cQei=-4.0,4.0:cQl3i=-5.5,5.5:cQlMi=-4.0,4.0:cQq11=-0.7,0.7:cQq13=-0.35,0.35:cQq81=-1.7,1.5:cQq83=-0.6,0.6:cQt1=-4.0,4.0:cQt8=-8.0,8.0:cbW=-3.0,3.0:cpQ3=-4.0,4.0:cpQM=-10.0,17.0:cpt=-15.0,15.0:cptb=-9.0,9.0:ctG=-0.8,0.8:ctW=-1.5,1.5:ctZ=-2.0,2.0:ctei=-4.0,4.0:ctlSi=-5.0,5.0:ctlTi=-0.9,0.9:ctli=-4.0,4.0:ctp=-15.0,40.0:ctq1=-0.6,0.6:ctq8=-1.4,1.4:ctt1=-2.6,2.6 -P ctW -P ctZ -P ctp -P cpQM -P ctG -P cbW -P cpQ3 -P cptb -P cpt -P cQl3i -P cQlMi -P cQei -P ctli -P ctei -P ctlSi -P ctlTi -P cQq13 -P cQq83 -P cQq11 -P ctq1 -P cQq81 -P ctq8 -P ctt1 -P cQQ1 -P cQt8 -P cQt1 --saveToys
# Clean up large submission files
find $CMSSW_BASE/src/EFTFit/Fitter/test/ -type d -name "crab_*" -size +1M -delete

echo "Please check the crab monitoring tool at:"
echo "https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11&var-user=${USER}&var-site=All&var-current_url=%2Fd%2FcmsTMDetail%2Fcms_task_monitoring&var-task=All&from=now-7d&to=now"
echo "It may take a few minutes for your jobs to show"
