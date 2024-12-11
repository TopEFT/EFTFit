# EFTFit
This repository holds the custom files needed to run a EFT fit topcoffea datacards.

## New fancy install script
To quickly install this repo, simply run:<br>
`wget -O - https://raw.githubusercontent.com/TopEFT/EFTFit/master/install.sh | sh`<br>
NOTE: This will install the TopEFT custom CombineHarvester fork. If you need to use `-s -1` as implemented in combine, you'll need to install the main CombineHarvester repo.

### Setting up
 
  In order to run combine, you will need to get the appropriate CMSSW release and to clone several repositories.

#### Set up the CMSSW release
Install CMSSW_10_2_13 ***OUTSIDE OF YOUR TOPCOFFEA DIR AND NOT IN CONDA***
```
export SCRAM_ARCH=slc7_amd64_gcc700
scram project CMSSW CMSSW_10_2_13
cd CMSSW_10_2_13/src
scram b -j8
```

#### Get the Combine repository
Currently working with tag `v8.2.0`:

```
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit/
git checkout v8.2.0
cd -
scram b -j8
```

#### Get the EFTFit repository
```
cd $CMSSW_BASE/src/
git clone https://github.com/TopEFT/EFTFit.git EFTFit
scram b -j8
```

#### Get the CombineHarvester repository
This package is designed to be used with the CombineHarvester fork. This might cause errors when compiling, but you can safely ignore them.

```
git clone git@github.com:cms-analysis/CombineHarvester.git
cd CombineHarvester
git checkout 128e41eb
scram b -j8
```


### Fitting

Now we can actually run combine to perform the fits.

#### Running the fits
- Make sure you have done a `cmsenv` inside of `CMSSW_10_2_13/src/` (wherever you have it installed)
- Enter `CMSSW_10_2_13/src/EFTFit/Fitter/test`
- Copy all .txt and .root files created by `python analysis/topEFT/datacard_maker.py` (in the `histos` directory of your toplevel topcoffea directory)
- Run `combineCards.py` to merge them all into one txt file. **DO NOT** merge multiple variables for the **same** channel, as this would artifically double the statistics!
  - E.g. `njets` only: `combineCards.py ttx_multileptons-*{b,p,m}.txt > combinedcard.txt`
  - E.g. `ptbl` for all categories _but_ `3l off-shell Z` (using `HT` instead): `combineCards.py ttx_multileptons-2lss_*ptbl.txt ttx_multileptons-3l_onZ*ptbl.txt ttx_multileptons-3l_*_offZ_*ht.txt ttx_multileptons-4l_*ptbl.txt > combinedcard.txt`
  - TOP-22-006 selection (old mehtod): `combineCards.py ttx_multileptons-{2,4}*lj0pt.txt ttx_multileptons-3l_{p,m}_offZ*lj0pt.txt ttx_multileptons-3l_onZ_1b_*ptz.txt ttx_multileptons-3l_onZ_2b_{4,5}j*ptz.txt ttx_multileptons-3l_onZ_2b_{2,3}j*lj0pt.txt > combinedcard.txt`
  - TOP-22-006 selection (new mehtod): The latest tools should produce the correct lj0pt or ptz datacards for the corresponding categoes. Therefore, you can simply run: `combineCards.py ttx_multileptons-*.txt > combinedcard.txt`
- NOTE: combine uses a lot of recursive function calls to create the workspace. When running with systematics, this can cause a segmentation fault. You must run `ulimit -s unlimited` once per session to avoid this.
- Run the following command to generate the workspace file:
    ```
    text2workspace.py combinedcard.txt -o wps.root -P EFTFit.Fitter.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative --X-allow-no-background --for-fits --no-wrappers --X-pack-asympows --optimize-simpdf-constraints=cms
    ``` 
    You can Specify a subset of WCs using `--PO`, e.g.:
    ```
    text2workspace.py combinedcard.txt -o wps.root -P EFTFit.Fitter.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative --X-allow-no-background --PO cpt,ctp,cptb,cQlMi,cQl3i,ctlTi,ctli,cbW,cpQM,cpQ3,ctei,cQei,ctW,ctlSi,ctZ,ctG
    ```
- Run combine with our EFTFit tools
  - Example:
    ```
    python -i ../scripts/EFTFitter.py
    fitter.batch1DScanEFT(basename='.081921.njet.ptbl.Float', batch='condor', workspace='wps.root', other=['-t', '-1'])
    ```
  - Once all jobs are finished, run the following (again inside `python -i ../scripts/EFTFitter.py`) to collect them in the `EFTFit/Fitter/fit_files` folder: 
    ```
    fitter.batchRetrieve1DScansEFT(basename='.081921.njet.ptbl.Float', batch='condor')
    ````

#### Plot making

To make simple 1D plots, use:
```
python -i ../scripts/EFTPlotter.py
plotter.BatchOverlayLLPlot1DEFT(basename1_lst=['.081121.njet.16wc.Float'], basename2_lst=['.EFT.SM.Freeze'], wcs=[], log=False, final=False, titles=['Others profiled', 'Others fixed to SM'])
```
To make comparison plots (e.g. `njets` vs. `njets+ptbl`):
```
python -i ../scripts/EFTPlotter.py
plotter.BestScanPlot(basename_float_lst='.081721.njet.Float', basename_freeze_lst='.081821.njet.ptbl.Float', filename='_float_njet_ptbl', titles=['N_{jet} prof.', 'N_{jet}+p_{T}(b+l) prof.'], printFOM=True)
```
## Steps for reproducing the "official" TOP-22-006 workspace:
1. Combine the cards: Inside of the EFTFit repo, copy the relevant cards (`.txt` files) and templates (`.root` files) for the categories that you want to make a worksapce for into the same directory. For the TOP-22-006 results, this should correspond to the appropriate mix-and-match combination of `ptz` and `lj0pt` that can be obtained with the `datacards_post_processing.py` script (as explained in the "To reproduce the TOP-22-006 histograms and datacards" section of the `topcoffea` readme). Then from within this directory (that contains only the relevant cards/templates _and no extraneous cards/templates_), run `combineCards.py ttx_multileptons-*.txt > combinedcard.txt` to make a combined card. 
1. Copy your selected WC file that was made with your cards (called `selectedWCs.txt`) to somewhere that is accessible from where you will be running the `text2workspace` step.  
1. Make the workspace by running the following command. Note that this command can take ~2 hours up to about ~8 hours or more (depending on where it is run). 

    ```
    text2workspace.py combinedcard.txt -o yourworkspacename.root -P EFTFit.Fitter.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative --X-allow-no-background --for-fits --no-wrappers --X-pack-asympows --optimize-simpdf-constraints=cms --PO selectedWCs=/path/to/your/selectedWCs.txt
    ```


# Making impact plots
Impact plots must be done in three stages:
### Initial fit
Run 
```python
fitter.ImpactInitialFit(workspace='ptz-lj0pt_fullR2_anatest17_noAutostats_withSys.root', wcs=[])
```
to produce the initial fits. A blank `wcs` will run over all WCs.
### Nuisance fit
Run 
```python
fitter.ImpactNuisance(workspace='ptz-lj0pt_fullR2_anatest17_noAutostats_withSys.root', wcs=[])
```
to fit each NP. A blank `wcs` will run over all WCs.
### Produce plots
Run 
```python
fitter.ImpactCollect(workspace='ptz-lj0pt_fullR2_anatest17_noAutostats_withSys.root', wcs=[])
```
to collect all jobs and create the final pdf plots. A blank `wcs` will run over all WCs.


# Making postfit
Note: If you are making Asimov data postfit, the best way to approach this is to simply create a seperate Asimov workspace with only Asimov datacards and perform the exact same steps in this section. (For topeft analysis group, turn off `--unblind` option to obtain Asimov datacards)
1. Copy your workspace into `/Fitter/test` directory, make sure you activate `cmsenv`
### Making the postfit root file
2. In `Fitter/test` run `MultidimFit` to make postfit for the workspace `wsp.root` with the following command:
```
time combine --algo none --cminPreScan --cminDefaultMinimizerStrategy=0 -P ctW --trackParameters ctW,ctZ,ctp,cpQM,ctG,cbW,cpQ3,cptb,cpt,cQl3i,cQlMi,cQei,ctli,ctei,ctlSi,ctlTi,cQq13,cQq83,cQq11,ctq1,cQq81,ctq8,ctt1,cQQ1,cQt8,cQt1 --floatOtherPOIs 1 --setParameters ctW=0,ctZ=0,ctp=0,cpQM=0,ctG=0,cbW=0,cpQ3=0,cptb=0,cpt=0,cQl3i=0,cQlMi=0,cQei=0,ctli=0,ctei=0,ctlSi=0,ctlTi=0,cQq13=0,cQq83=0,cQq11=0,ctq1=0,cQq81=0,ctq8=0,ctt1=0,cQQ1=0,cQt8=0,cQt1=0 -M MultiDimFit -d wsp.root -v 2 --saveFitResult -n multidimfit
```
A file named `multidimfit.root` will be made in the `Fitter/test` directory.
### Constructing postfit for all signal regions with condor
3. Add the file `multidimfit.root` to `../../script/structMaker.C`, and change option `do_postfit` to `true` in the script.
4. Open `../../condor/submit` script then queue the corresponding number of signal regions, which is 11 for top22-006. (Make sure all the necessary scripts to run condor have the correct directory to eventually point to your `../../script/structMaker.C`.)
5. In `Fitter/test` directory, make a new directory called `fit_results`, and inside, make `SR_postfit` and `SR_sum_postfit` two directories. (The scripts are set already to read these directories otherwise it would fail the command.)
6. Make a directory in `fit_results` called `condor/logs`.
7. Run the condor jobs through:
```
condor_submit ../../condor/submit
```
8. When the jobs are finished, there will be 11 (or whatever number of signal regions your analysis has) SR files in `SR_postfit`, and the same number of files in `SR_sum_postfit`. (Note that file naming would start from zero)
### Making the SR plots
9. Go into `test/fit_results` directory, and run:
```
root -b -l -q '../../scripts/plot_maker.C("")'
```
The corresponding plots will be made in `fit_results/plots`

### Changing WCs to other values
For step 2. the command is used to fit all WCs = 0 case. If you want to set certain WC value to non-zero, simply change `--setParameters` option. 
