text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cQe1 -o cQe1.root
combine -M MultiDimFit -v 3 cQe1.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cQl31 -o cQl31.root
combine -M MultiDimFit -v 3 cQl31.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cQlM1 -o cQlM1.root
combine -M MultiDimFit -v 3 cQlM1.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cbW -o cbW.root
combine -M MultiDimFit -v 3 cbW.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cpQ3 -o cpQ3.root
combine -M MultiDimFit -v 3 cpQ3.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cpQM -o cpQM.root
combine -M MultiDimFit -v 3 cpQM.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cpt -o cpt.root
combine -M MultiDimFit -v 3 cpt.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cptb -o cptb.root
combine -M MultiDimFit -v 3 cptb.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=ctG -o ctG.root
combine -M MultiDimFit -v 3 ctG.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=ctW -o ctW.root
combine -M MultiDimFit -v 3 ctW.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=ctZ -o ctZ.root
combine -M MultiDimFit -v 3 ctZ.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=cte1 -o cte1.root
combine -M MultiDimFit -v 3 cte1.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=ctl1 -o ctl1.root
combine -M MultiDimFit -v 3 ctl1.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=ctlS1 -o ctlS1.root
combine -M MultiDimFit -v 3 ctlS1.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=ctlT1 -o ctlT1.root
combine -M MultiDimFit -v 3 ctlT1.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFT16DModel:eft16D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/16D_Parameterization.npy --PO operators=ctp -o ctp.root
combine -M MultiDimFit -v 3 ctp.root --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1



