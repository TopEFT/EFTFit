#starttime = $SECONDS
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy -o 16D.root
combine -d 16D.root -n EFT -M MultiDimFit --cl=0.68 --autoBoundsPOIs "*" --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1 --saveFitResult
combine -d 16D.root -n EFT -M MultiDimFit -v 2 --algo cross --cl=0.68 --autoBoundsPOIs "*" --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#combine -d 16D.root -n EFT -M MultiDimFit --algo grid --points 5000 --cl=0.68 --autoBoundsPOIs "*" --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#combine -d 16D.root -n EFT -M MultiDimFit --algo singles -v 2 --cl=0.68 --autoBoundsPOIs "*" --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1 --saveFitResult


#operators=cQl31,cpt,cptb,ctlT1,cpQ3,cpQM,ctG,cbW

#combine -M FitDiagnostics cptb.root --autoBoundsPOIs cptb #--setParameterRanges cptb=-4,4 #--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#Keys: ['ctW', 'ctl1', 'ctp', 'cpQM', 'ctZ', 'cQe1', 'ctG', 'cpQ3', 'cptb', 'cpt']
#duration = $(( SECONDS -start ))
