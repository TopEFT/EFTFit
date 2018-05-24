text2workspace.py Datacard_test.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO scaling=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO process=ttZ --PO process=ttW --PO bin=C_2lss_p_mumu_3j_2b --PO coefficient=cuW -o cuW.root
combine -M MultiDimFit cuW.root --setParameterRanges cuW=-4,4 -t 5
