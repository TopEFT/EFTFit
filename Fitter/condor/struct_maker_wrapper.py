import os
import logging
import subprocess
import datetime
import argparse

parser = argparse.ArgumentParser(description='Customize the plotting macro')
parser.add_argument('--idx',   '-i', default=0, help = 'Index of the signal region')

args = parser.parse_args()
root_args = args.idx
macro_dir = '/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/scripts/'
subprocess.check_call(['root','-b','-l','-q', macro_dir + 'struct_maker.C({args})'.format(args=root_args)])
