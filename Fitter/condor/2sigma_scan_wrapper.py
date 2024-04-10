import os
import sys
import logging
import subprocess
import datetime
import argparse

CMSSW_SRC   = os.path.expandvars("$CMSSW_BASE/src")
sys.path.append("{}/EFTFit/Fitter/scripts".format(CMSSW_SRC))
from EFTPlotter import EFTPlot

wc_list    = ["ctW", "ctZ", "ctp", "cpQM", "ctG", "cbW", "cpQ3", "cptb", "cpt", "cQl3i", "cQlMi", "cQei", "ctli", "ctei", "ctlSi", "ctlTi", "cQq13", "cQq83", "cQq11", "ctq1", "cQq81", "ctq8", "ctt1", "cQQ1", "cQt8", "cQt1"]
limit_list = ["-2sigma", "+2sigma"]

parser = argparse.ArgumentParser(description='Customize the fitting macro')
parser.add_argument('--idx',   '-i', default=0,           help = 'Index of the WC')
parser.add_argument('--asimov','-a', action='store_true', help = 'Use asimov data instead')

args = parser.parse_args()
iWC = int(int(args.idx)/2)
iPM = int(args.idx)%2
wc = wc_list[iWC]
limit = limit_list[iPM]

scan_lst = ''
if (args.asimov):
	scan_lst = '.110822.differential.fullR2.Float'
else:
	scan_lst = '.differential.fullR2.Float.RealData'

scan_lst = 'Freeze'

# os.chdir('/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/fit_files')
# plotter = EFTPlot()
# wc_arr = plotter.getIntervalFits(basename_lst=[scan_lst], params=[wc])
# wc_val = wc_arr[0][2+iPM][0] if len(wc_arr[0][2+iPM]) == 1 else wc_arr[0][2+iPM][iPM]

val_dic = {
	'ctlSi': [-0.40, 0.40],
	'ctlTi': [-2.80, 2.80],
	'ctei':  [-1.90, 2.39],
	'ctli':  [-2.01, 2.20],
	'cQei':  [-2.04, 2.12],
	'cQlMi': [-1.80, 2.33],
	'cQl3i': [-2.68, 2.58],
	'cpt':   [-4.95, 3.19],
	'cptb':  [-3.15, 3.19],
	'cpQ3':  [-0.84, 1.91],
	'cbW':   [-0.75, 0.75],
	'ctG':   [-0.22, 0.25],
	'cpQM':  [-2.66, 2.95],
	'ctp':   [-7.68, 2.15],
	'ctZ':   [-0.58, 0.59],
	'ctW':   [-0.47, 0.41],
	'cQt1':  [-2.75, 2.62],
	'cQt8':  [-5.24, 5.66],
	'cQQ1':  [-3.04, 3.28],
	'ctt1':  [-1.54, 1.63],
	'ctq8':  [-0.68, 0.24],
	'cQq81': [-0.67, 0.21],
	'ctq1':  [-0.22, 0.20],
	'cQq11': [-0.19, 0.19],
	'cQq83': [-0.17, 0.16],
	'cQq13': [-0.08, 0.07],
}
wc_val = val_dic[wc][iPM]

wc_name = ""
for wc_any in wc_list:
	wc_name += '{},'.format(wc_any)
opt1 = "{}".format(wc_name[:-1])

wc_list.remove(wc)
val_list = ""
for wc_other in wc_list:
    val_list += '{}=0,'.format(wc_other)
val_list += '{}={}'.format(wc, wc_val)
opt2 = "{}".format(val_list)

scan_type = 'Float'
opt3 = "{}".format(wc)
if "Freeze" in scan_lst:
	scan_type = "Freeze"
	for wc_other in wc_list:
	    opt3 += ',{}'.format(wc_other)

data_type = "_asimov" if args.asimov else ""
opt4 = "_{}_{}{}_{}".format(wc, limit, data_type, scan_type)

os.chdir('/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/card_anatest24')
# command = "time combine --algo none --cminPreScan --cminDefaultMinimizerStrategy=0 -M MultiDimFit -d wps.root -v 2 --saveFitResult {} {} {} {}".format(opt1, opt2, opt3, opt4)
# print(command)

if (args.asimov):
    subprocess.check_call(['combine', '-M', 'MultiDimFit', '--algo', 'none', '--cminPreScan', '--cminDefaultMinimizerStrategy=0', '-d', 'wps.root', '-v', '2', '--saveFitResult',
	                       '--trackParameters', opt1, '--setParameters', opt2, '--freezeParameters', opt3, '-n', opt4, '-t', '-1'])
else:
    subprocess.check_call(['combine', '-M', 'MultiDimFit', '--algo', 'none', '--cminPreScan', '--cminDefaultMinimizerStrategy=0', '-d', 'wps.root', '-v', '2', '--saveFitResult',
	                       '--trackParameters', opt1, '--setParameters', opt2, '--freezeParameters', opt3, '-n', opt4])
