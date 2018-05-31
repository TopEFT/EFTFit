text2workspace.py Datacard_root_test.txt -P EFTFit.Fitter.EFT1DModel:eft1D --PO scaling=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO process=ttZ --PO process=ttW --PO process=tZq --PO process=ttH --PO bin=C_2lss_p_mumu_3j_2b --PO coefficient=ctZ -o ctZ.root
combine -M MultiDimFit ctp.root --setParameterRanges ctp=-4,4 -v 3
