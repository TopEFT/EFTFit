# TL;DR
`cd` to submission directory<br>
Submit with e.g.:
`python -i $CMSSW_BASE/src/EFTFit/Fitter/scripts/EFTFitter.py`
```python
fitter.batchDNNScan(name='.11102022.EFT.Float.DNN.1M', workspace='ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root', points=100000)
```

Monitor on [grafana task monitor](https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11)

Collect with e.g.:
```python
retrieveDNNScan('.11102022.EFT.Float.DNN.1M', points=1000000)
```
<br>

# Initial setup
## New fancy install script
There are a few ways to use this script:
1. If you want a fresh install, please `cd` to a directory where CMSSW is NOT installed
2. If you already have CMSSW 10_2_13 installed, please make sure you run `cmsenv` in the base directory first.
To quickly install this repo, simply run:<br>
`wget -O - https://raw.githubusercontent.com/TopEFT/EFTFit/master/dnn_input.sh | sh`<br>
NOTE: This will patch the CombineHarvester with a custom submission option. If you need to use `-s -1` as implemented in combine, you'll need to install the main CombineHarvester repo.
If you do not have an SSH key configured for GitHub, you can use the http install script instead:<br>
`wget -O - https://raw.githubusercontent.com/TopEFT/EFTFit/master/dnn_input_http.sh | sh`<br>
## Install CMSSW
Follow the instructions in https://github.com/TopEFT/EFTFit/#readme.
## NOTE
We have for of the CombineHarvester repo designed for this task. It handles the custom seed generation when sending jobs to crab.<br>
There are two ways to install this version:
1. Instead of teh git clone command in the EFTFit README, run:<br>
`git clone git@github.com:TopEFT/CombineHarvester.git --branch crab_random`<br>
and run `scram b -j8` like normal
2. If you've already installed the default CombineHarvester, run
```python
cd $CMSSW_BASE/src/CombineHarvester/CombineTools/
git remote add topeft git@github.com:TopEFT/CombineHarvester.git
git fetch topeft
git checkout -b crab_random topeft/crab_random
scrab b -j8
cd -
```

## Adjust the custom CRAB config file
Open `custom_crab.py` in `test` and modify the output path in `outLFNDirBase`. If you're using `CERNBOX`, chang it to `T3_CH_CERNBOX`.
The modified settings of 8000 MB of RAM and 4 CPUs should be fine for running combine over our workspace.
The modified runtime is set to 48 hrs, but when checking the job status you'll see a warning about only allowing 2775. This is ok to ignore.

## Additional setup
These job submissions can take up a lot of space. If your `lxplus` home directory is running low, consider using the `work` area (`/afs/cern.ch/user/<first-letter>/<user-name>/work/`). Either install CMSSW there, or make a symbolic link in your `test` directory.

# Submit jobs to CRAB
### Initialize voms proxy
This must be done before any jobs are submitted
`voms-proxy-init --rfc --voms cms -valid 192:00`

### Submission script
CRAB submissions can be very slow. The script is designed to submit 10 tasks at a time in parallel (`chunks` in the script), with each task consisting of 100 jobs. I found this is a good compromise to not overload the `lxplus` CPUs.

Launch the `EFTFitter.py` script with `python -i $CMSSW_BASE/src/EFTFit/Fitter/scripts/EFTFitter.py` (if using a symbolic link like suggested above, you'll need to provide an _absolute_ path, otherwise `../scripts/EFTFitter.py` works)
An example command to submit 1M jobs is
```python
fitter.batchDNNScan(name='.11102022.EFT.Float.DNN.1M', workspace='ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root', points=1000000)
```
NOTE: You must have the workspace in whatever directory you run the submission command from. The latest workspace is `ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root`.

## Monitoring CRAB jobs
The most reliable way to monitor jobs is to run `crab status -d <directory-of-task>` from the directory where you submitted your jobs. The [grafana task monitor](https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11) is also very useful, but can be slow to update.

## Collecting jobs from CRAB
Use `retrieveDNNScan` to collect the finished jobs.<br>
Note that this will _not_ check which jobs are done, so if some are still running, the results will be incomplete. To crab a particular task, use `retrieveGridScan` (don't forget to specify the batch type, as it defaults to `condor`).<br>
Example:
```python
fitter.retrieveGridScan('.11102022.EFT.Float.DNN.1M', batch='crab')
```
