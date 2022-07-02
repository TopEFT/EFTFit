# EFTFit
This repository holds the custom files needed to run a EFT fit topcoffea datacards.

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
scram b -j8
```


### Fitting

Now we can actually run combine to perform the fits.

#### Running the fits
- Make sure you have done a `cmsenv` inside of `CMSSW_10_2_13/src/` (wherever you have it installed)
- Enter `CMSSW_10_2_13/src/EFTFit/Fitter/test`
- Copy all .txt and .root files created by `python analysis/topEFT/datacard_maker.py` (in the `histos` directory of your toplevel topcoffea directory)
- Run `combineCards.py` to merge them all into one txt file. **DO NOT** merge multiple variables!
  - E.g. `njets` only: `combineCards.py ttx_multileptons-*{b,p,m}.txt > combinedcard.txt`
  - E.g. `ptbl` for all categories _but_ `3l off-shell Z` (using `HT` instead): `combineCards.py ttx_multileptons-2lss_*ptbl.txt ttx_multileptons-3l_onZ*ptbl.txt ttx_multileptons-3l_*_offZ_*ht.txt ttx_multileptons-4l_*ptbl.txt > combinedcard.txt`
- NOTE: combine uses a lot of recursive function calls to create the workspace. When running with systematics, this can cause a segmentation fault. You must run `ulimit -s unlimited` once per session to avoid this.
- Run the following command to generate the workspace file:
    ```
    text2workspace.py combinedcard.txt -o wps.root -P EFTFit.Fitter.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative --X-allow-no-background
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
plotter.BatchLLPlot1DEFT(basename='.081121.njet.16wc.Float')
```
To make comparison plots (e.g. `njets` vs. `njets+ptbl`):
```
python -i ../scripts/EFTPlotter.py
plotter.BestScanPlot(basename_float='.081721.njet.Float', basename_freeze='.081821.njet.ptbl.Float', filename='_float_njet_ptbl', titles=['N_{jet} prof.', 'N_{jet}+p_{T}(b+l) prof.'], printFOM=True)
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
