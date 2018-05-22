import numpy as np
import os

scales = {'cuW': {('ttZ','C_2lss_p_mumu_3j_2b'): (1, 0.322778, 653.371), ('ttW','C_2lss_p_mumu_3j_2b'): (1, 1.20998, 205.528)}}
np.save(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/scales.npy', scales)
