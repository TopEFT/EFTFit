text2workspace.py Datacard_root_ctW.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=ctW -o ctW.root
combine -M MultiDimFit ctW.root -v 3 --setParameterRanges ctW=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctl1.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=ctl1 -o ctl1.root
combine -M MultiDimFit ctl1.root -v 3 --setParameterRanges ctl1=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctp.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=ctp -o ctp.root
combine -M MultiDimFit ctp.root -v 3 --setParameterRanges ctp=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cpQM.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=cpQM -o cpQM.root
combine -M MultiDimFit cpQM.root -v 3 --setParameterRanges cpQM=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctZ.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=ctZ -o ctZ.root
combine -M MultiDimFit ctZ.root -v 3 --setParameterRanges ctZ=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cQe1.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=cQe1 -o cQe1.root
combine -M MultiDimFit cQe1.root -v 3 --setParameterRanges cQe1=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_ctG.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=ctG -o ctG.root
combine -M MultiDimFit ctG.root -v 3 --setParameterRanges ctG=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cpQ3.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=cpQ3 -o cpQ3.root
combine -M MultiDimFit cpQ3.root -v 3 --setParameterRanges cpQ3=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cptb.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=cptb -o cptb.root
combine -M MultiDimFit cptb.root -v 3 --setParameterRanges cptb=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
text2workspace.py Datacard_root_cpt.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO fits=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO coefficient=cpt -o cpt.root
combine -M MultiDimFit cpt.root -v 3 --setParameterRanges cpt=-4,4 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1
#Keys: ['ctW', 'ctl1', 'ctp', 'cpQM', 'ctZ', 'cQe1', 'ctG', 'cpQ3', 'cptb', 'cpt']

