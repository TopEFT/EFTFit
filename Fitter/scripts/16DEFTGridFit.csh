#starttime = $SECONDS
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy -o 16D.root

# Best quick fit for correlation matrix
combine -d 16D.root --saveFitResult -n EFT -M MultiDimFit -H AsymptoticLimits --cminPoiOnlyFit --setParameters "" --freezeParameters "" --floatParameters "" --redefineSignalPOIs "" --autoBoundsPOIs="*" --cminDefaultMinimizerStrategy=0

# 16D grid scan
#combine -d 16D.root --saveFitResult -n EFT -M MultiDimFit -H AsymptoticLimits --algo grid --points 5000 --cminPreScan --setParameters "" --freezeParameters "" --floatParameters "" --redefineSignalPOIs "" --autoBoundsPOIs="*" --cminDefaultMinimizerStrategy=0

# 1D scans
#combine -d 16D.root --saveFitResult -n EFT -M MultiDimFit --algo grid --points 100 --cminPreScan --setParameters "" --freezeParameters "" --floatParameters "" --redefineSignalPOIs "ctW" --cminDefaultMinimizerStrategy=0
#mv higgsCombineEFT.MultiDimFit.mH120.root higgsCombineEFT.MultiDimFit.mH120.ctW.root
#root -b -l -q '../scripts/LLPlots2D.cxx("higgsCombineEFT.MultiDimFit.mH120.ctW.root","multidimfitEFT.root")'
#combine -d 16D.root --saveFitResult -n EFT -M MultiDimFit --algo grid --points 100 --cminPreScan --setParameters "" --freezeParameters "" --floatParameters "" --redefineSignalPOIs "ctZ" --cminDefaultMinimizerStrategy=0
#mv higgsCombineEFT.MultiDimFit.mH120.root higgsCombineEFT.MultiDimFit.mH120.ctZ.root
#root -b -l -q '../scripts/LLPlots2D.cxx("higgsCombineEFT.MultiDimFit.mH120.ctZ.root","multidimfitEFT.root")'



#combine -d 16D.root -n EFT -M MultiDimFit --cminPreScan --algo cross -v 2 --cl=0.68 --autoBoundsPOIs "*" --cminDefaultMinimizerStrategy 0 --saveFitResult

#combine -M FitDiagnostics cptb.root --autoBoundsPOIs cptb #--setParameterRanges cptb=-4,4 #--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#duration = $(( SECONDS -start ))
