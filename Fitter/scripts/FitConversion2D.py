import numpy as np
import os

scales = {'cuW': {('ttZ','C_2lss_p_mumu_3j_2b'): (1, 0.322778, 653.371), ('ttW','C_2lss_p_mumu_3j_2b'): (1, 1.20998, 205.528)}, 'cuT': {('ttZ','C_2lss_p_mumu_3j_2b'): (1, 0.4102, 255), ('ttH','C_lss_p_mumu_3j_2b'): (1, 0.7821, 301)}}
np.save(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/scales2D.npy', scales)
