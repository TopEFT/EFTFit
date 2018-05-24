text2workspace.py Datacard_test.txt -P EFTFit.Fitter.EFT2DModel:eft2D --PO scaling=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO process=ttZ --PO process=ttW --PO bin=C_2lss_p_mumu_3j_2b --PO coefficient=cuW --PO coefficient=cuT -o cuWcuT.root
combine -M MultiDimFit cuWcuT.root --setParameterRanges cuW=-5,5:cuT=-5,5 --setParameters cuW=3,cuT=3 --expectSignal 0 -v 3
