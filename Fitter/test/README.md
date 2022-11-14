# TL;DR
`cd` to submission directory<br>
Launch tmux<br>
Run `kinit && aklog` if this is a new tmux session<br>
Submit with e.g.:
`python -i $CMSSW_BASE/src/EFTFit/Fitter/scripts/EFTFitter.py`
```python
fitter.batchDNNScan(name='.11102022.EFT.Float.DNN.1M', workspace='ptz-lj0pt_fullR2_anatest23v01_withAutostats_withSys.root', points=100000)
```
Detach TMUX

Monitor on [grafana task monitor](https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11)

Collect with e.g.:
```python
retrieveDNNScan('.11102022.EFT.Float.DNN.1M', points=1000000)
```
<br>

# Initial setup
## Install CMSSW
Follow the instructions in https://github.com/TopEFT/EFTFit/#readme.

## Adjust the custom CRAB config file
Open `custom_crab.py` in `test` and modify the output path in `outLFNDirBase`. If you're using `CERNBOX`, chang it to `T3_CH_CERNBOX`.
The modified settings of 8000 MB of RAM and 4 CPUs should be fine for running combine over our workspace.
The modified runtime is set to 48 hrs, but when checking the job status you'll see a warning about only allowing 2775. This is ok to ignore.

## Additional setup
These job submissions can take up a lot of space. If your `lxplus` home directory is running low, consider using the `work` area (`/afs/cern.ch/user/<first-letter>/<user-name>/work/`). Either install CMSSW there, or make a symbolic link in your `test` directory.

# Submit jobs to CRAB
Submission will take a while, so it is best to run in something like `tmux` or `screen`
### tmux
First, make sure you save what `lxplus` node you're running on (use `uname -a` if unsure)<br>
Run `tmux` to start a new tmux session<br>
The AFS system has some permissions issues with tmux if you detach and log out. Run `kinit && aklog` to fix this.<br>
Start the job submissions (see below).<br>
Press `ctrl+b` followd by `d` to detach tmux.<br>
You can then logout .

To come back to your jobs later, connect to lxplus, then ssh to the node from above (`ssh lxplus<node-number>`)<br>
Run `tmux -a` to attach the tmux session

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

## Monitoring CRAB jobs
The most reliable way to monitor jobs is to run `crab status -d <directory-of-task>` from the directory where you submitted your jobs. The [grafana task monitor](https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11) is also very useful, but can be slow to update.

## Collecting jobs from CRAB
Use `retrieveDNNScan` to collect the finished jobs. 
```python
retrieveDNNScan('.11102022.EFT.Float.DNN.1M', points=1000000)
```
Note that this will _not_ check which jobs are done, so if some are still running, the results will be incomplete. To crab a particular task, use `retrieveGridScan` (don't forget to specify the batch type, as it defaults to `condor`).<br>
Example:
```python
fitter.retrieveGridScan('.11102022.EFT.Float.DNN.1M70', batch='crab')
```
