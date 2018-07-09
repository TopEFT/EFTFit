text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO 'map=.*/ttW:r_ttW[1,0,30]' --PO 'map=.*ttZ:r_ttZ[1,0,30]' --PO 'map=.*ttH:r_ttH[1,0,30]' --PO 'map=.*tZq:r_tZq[1,0,30]' -m 126 Datacard_root_test.txt
combine -M MultiDimFit Datacard_root_test.root --verbose 3
