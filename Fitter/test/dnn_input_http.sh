#!/bin/bash
cmssw=$1

echo -e "\n"
echo "##################################################"
echo "#                                                #"
echo "# Executing the super awesome mega EFTFit script #"
echo "#                                                #"
echo "##################################################"
echo -e "\n"

## CMSSW part
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
elif [[ -d $cmssw ]]; then
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
  git clone http://github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
  cd HiggsAnalysis/CombinedLimit/
  git checkout v8.2.0
  scram b -j8
  cd -
fi


## CombineHarvester part
if [[ ! -d $CMSSW_BASE/src/CombineHarvester ]]; then
  # Install CombineHarvester
  echo "Installing CombineHarvester"
  git clone http://github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
  cd HiggsAnalysis/CombinedLimit/
  git checkout v8.2.0
  scram b -j8
  cd -
fi

## EFTFit part
if [[ ! -d $CMSSW_BASE/src/EFTFit ]]; then
  echo "Installing the  EFTFit"
  cd $CMSSW_BASE/src/
  git clone http://github.com:cms-analysis/CombineHarvester.git
  scram b -j8
  cd -

fi
cd $CMSSW_BASE/src/CombineHarvester/CombineTools/python/combine/
cp $CMSSW_BASE/src/EFTFit/Fitter/test/crab_random.patch .
if ! git apply --reverse --check crab_random.patch; then
  echo "Checking to see if the patch is applied"
  echo "The above \"error\" simply means the patch must be applied."
  gdiff=$(git diff --name-only master | wc -l)
  if [[ $gdiff -gt 0 ]]; then
    echo "### WARNING ###"
    echo "I've found uncommited changes. I will stash these before applying our patch to the CombineHarvester"
    echo "To view these changes, cd to the CombineHarvester directory and run: \`git stash show -p\`"
    echo "To recover them (if you're sure they won't conflict with our patch, run: \`git stash pop\`)"
    echo ""
    git stash
  fi
  # Apply patch to CombineToolBase.py
  git apply crab_random.patch
fi

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/
cp $CMSSW_BASE/src/EFTFit/Fitter/test/combine_rnd_nll.patch .
if ! git apply --reverse --check crab_random.patch; then
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
  # Apply patch to CombineToolBase.py
  git apply crab_random.patch
  scram b -j8
fi

cd $CMSSW_BASE/src/EFTFit/Fitter/test/crab_random.patch .

## Initialize voms proxy
echo "Initializing voms proxy. Please make sure this line succeeds before tyring to submit to crab!"
echo "If the initialization fails, but you have a valid proxy certificate, rerun:"
echo "\`voms-proxy-init --rfc --voms cms -valid 192:00\`"
voms-proxy-init --rfc --voms cms -valid 192:00

date=`date +"%m%d%y_%H%m%S"`
cd $CMSSW_BASE/src/EFTFit/Fitter/test/
wget -nc https://cernbox.cern.ch/files/spaces/eos/user/b/byates/EFT/ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root
combineTool.py -d /afs/cern.ch/user/${USER:0:1}/${USER}/CMSSW_10_2_13/src/EFTFit/Fitter/test/ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root -M MultiDimFit --algo random --skipInitialFit --cminDefaultMinimizerStrategy=0 -s -1 --points 1000000 -n .${date}.EFT.Float.DNN.1M --job-mode crab3 --task-name ${date}EFTFloatDNN1M --custom-crab custom_crab.py --split-points 100 --setParameterRanges ctlTi=-0.374607534482,0.374565530096:ctq1=-0.21843745263,0.211490768825:ctq8=-0.684973317267,0.259134430666:cQq83=-0.172982013312,0.164393560733:cQQ1=-3.06229434848,3.32957946073:cQt1=-2.75493174781,2.70914063328:cQt8=-5.20851917113,5.8460702909:ctli=-1.79129195489,2.13132757518:cQq81=-0.693160523097,0.22472203594:cQlMi=-1.57015809391,2.30856227126:cbW=-0.774498659892,0.778576099742:cpQ3=-0.799926741902,2.10535102349:ctei=-1.7890995999,2.21964159432:ctlSi=-2.62979860715,2.63179492407:ctW=-0.559580150961,0.467065683794:cpQM=-6.14373711624,8.09670260566:cQei=-1.92444869487,1.96143403803:ctZ=-0.728670875381,0.645039586692:cQl3i=-2.92095208758,2.63905091692:ctG=-0.278085429908,0.239456990615:cQq13=-0.0766066091416,0.071026796871:cQq11=-0.194708263067,0.194727737288:cptb=-3.3626617209,3.36181881128:ctt1=-1.58129610231,1.62272822644:ctp=-9.34032472115,2.29607071949:cpt=-10.5073906899,7.93857570177 -P ctW -P ctZ -P ctp -P cpQM -P ctG -P cbW -P cpQ3 -P cptb -P cpt -P cQl3i -P cQlMi -P cQei -P ctli -P ctei -P ctlSi -P ctlTi -P cQq13 -P cQq83 -P cQq11 -P ctq1 -P cQq81 -P ctq8 -P ctt1 -P cQQ1 -P cQt8 -P cQt1 --saveToys --custom-crab-post custom-crab-post
# Clean up large submission files
find $CMSSW_BASE/src/EFTFit/Fitter/test/ -type d -name "crab_*" -size +1M -delete

echo "Please check the crab monitoring tool at:"
echo "https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11&var-user=${USER}&var-site=All&var-current_url=%2Fd%2FcmsTMDetail%2Fcms_task_monitoring&var-task=All&from=now-7d&to=now"
echo "It may take a few minutes for your jobs to show"
