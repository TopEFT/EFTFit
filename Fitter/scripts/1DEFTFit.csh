text2workspace.py Datacard_root_test.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO scaling=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO process=ttZ --PO process=ttW --PO process=tZq --PO process=ttH --PO bin=C_2lss_p_mumu_3j_2b --PO coefficient=cQe1 -o cQe1.root
combine -M MultiDimFit cQe1.root --setParameterRanges cQe1=-4,4 -v 3
