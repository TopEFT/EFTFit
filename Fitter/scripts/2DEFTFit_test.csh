text2workspace.py Datacard_root_test.txt -P EFTFit.Fitter.EFT2DModel:eft2D --PO scaling=$CMSSW_BASE/src/EFTFit/Fitter/data/scales.npy --PO process=ttZ --PO process=ttW --PO process=tZq --PO process=ttH --PO bin=C_2lss_p_mumu_3j_2b --PO coefficient=ctZ --PO coefficient=ctG -o ctZctG.root
combine -M MultiDimFit ctZctG.root --setParameterRanges ctZ=-4,4:ctG=-4,4 -v 3 -t 2
