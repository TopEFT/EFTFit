import os
import sys
import logging
import subprocess
import datetime
import argparse

CMSSW_SRC   = os.path.expandvars("$CMSSW_BASE/src")
sys.path.append("{}/EFTFit/Fitter/scripts".format(CMSSW_SRC))
from EFTPlotter import EFTPlot

parser = argparse.ArgumentParser(description='Customize the plotting macro')
parser.add_argument('--SR',    '-s', default=0, help = 'Index of the signal region')
parser.add_argument('--limit', '-l', default=0, help = 'Index of the chosen limit of the WC')
parser.add_argument('--asimov','-a', action='store_true', help = 'Use asimov data instead')

args = parser.parse_args()
iSR = args.SR
ilimit = args.limit
data_type = args.asimov

wc_list    = ["ctW", "ctZ", "ctp", "cpQM", "ctG", "cbW", "cpQ3", "cptb", "cpt", "cQl3i", "cQlMi", "cQei", "ctli", "ctei", "ctlSi", "ctlTi", "cQq13", "cQq83", "cQq11", "ctq1", "cQq81", "ctq8", "ctt1", "cQQ1", "cQt8", "cQt1"]
limit_list = ["-2sigma", "+2sigma"]

iWC = int(int(ilimit)/2)
iPM = int(ilimit)%2
wc = wc_list[iWC]
limit = limit_list[iPM]

scan_lst = ''
if (data_type):
	scan_lst = '.110822.differential.fullR2.Float';
else:
	scan_lst = '.differential.fullR2.Float.RealData';

os.chdir('/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/fit_files')
plotter = EFTPlot()
wc_arr = plotter.getIntervalFits(basename_lst=[scan_lst], params=[wc])
wc_val = wc_arr[0][2+iPM][0] if len(wc_arr[0][2+iPM]) == 1 else wc_arr[0][2+iPM][iPM]

macro_dir = '/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/scripts/'
subprocess.check_call(['root', '-b', '-l', '-q', macro_dir + "struct_maker_2sigma_byWC.C({},\"{}\",\"{}\",{})".format(iSR, wc, limit, wc_val)])
