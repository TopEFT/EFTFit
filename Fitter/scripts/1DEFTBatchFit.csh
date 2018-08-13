text2workspace.py Datacard_root_ctW.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=ctW -o ctW.root
combine -M MultiDimFit ctW.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctl1.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=ctl1 -o ctl1.root
combine -M MultiDimFit ctl1.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctp.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=ctp -o ctp.root
combine -M MultiDimFit ctp.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cpQM.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=cpQM -o cpQM.root
combine -M MultiDimFit cpQM.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctZ.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=ctZ -o ctZ.root
combine -M MultiDimFit ctZ.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cQe1.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=cQe1 -o cQe1.root
combine -M MultiDimFit cQe1.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctG.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=ctG -o ctG.root
combine -M MultiDimFit ctG.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cpQ3.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=cpQ3 -o cpQ3.root
combine -M MultiDimFit cpQ3.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cptb.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=cptb -o cptb.root
combine -M MultiDimFit cptb.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cpt.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO operator=cpt -o cpt.root
combine -M MultiDimFit cpt.root -v 3 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#Keys: ['ctW', 'ctl1', 'ctp', 'cpQM', 'ctZ', 'cQe1', 'ctG', 'cpQ3', 'cptb', 'cpt']

