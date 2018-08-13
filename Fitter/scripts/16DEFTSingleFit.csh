text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cQl31 -o cQl31.root
combine -M MultiDimFit -v 3 cQl31.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#operators=cQl31,cpt,cptb,ctlT1,cpQ3,cpQM,ctG,cbW

#combine -M FitDiagnostics cptb.root --autoBoundsPOIs cptb #--setParameterRanges cptb=-4,4 #--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#Keys: ['ctW', 'ctl1', 'ctp', 'cpQM', 'ctZ', 'cQe1', 'ctG', 'cpQ3', 'cptb', 'cpt']
