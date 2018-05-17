text2workspace.py Datacard_test.txt -P EFTFit.Fitter.EFT1DModel:eft2 --PO scaling=/afs/crc.nd.edu/user/a/alefeld/Private/CombineHarvester/CMSSW_8_1_0/src/EFTFit/Fitter/data/scales.npy --PO process=ttZ --PO process=ttW --PO coefficient=cuW -o cuW.root
combine -M MultiDimFit cuW.root --setParameterRanges cuW=-4,4 -t 5
