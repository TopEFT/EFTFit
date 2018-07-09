text2workspace.py Datacard_root_cptb.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=cptb -o cptb.root
#combine -M FitDiagnostics cptb.root --autoBoundsPOIs cptb #--setParameterRanges cptb=-4,4 #--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
combine -M MultiDimFit -v 3 cptb.root

#Keys: ['ctW', 'ctl1', 'ctp', 'cpQM', 'ctZ', 'cQe1', 'ctG', 'cpQ3', 'cptb', 'cpt']
