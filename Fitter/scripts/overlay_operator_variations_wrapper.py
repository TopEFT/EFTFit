import os
import logging
import subprocess
import datetime
import argparse

import EFTFit.Fitter.consts as CONST

from EFTFit.Fitter.LvlFormatter import LvlFormatter
from EFTFit.Fitter.utils import get_files, move_files, clean_dir
from EFTFit.Fitter.make_html import make_html

# Desc:
#   Python wrapper to run the overlay_operator_variations.C ROOT macro. It runs on output produced
#   by the combine_helper.py code. It looks for input directories starting in the 'test' directory
#   of the EFTFit/Fitter package and tries to create and move output files (usually png/pdf plots)
#   to a webarea starting in ~/www/eft_stuff/misc/fitting_plots

parser = argparse.ArgumentParser(description='Customize the plotting macro')
parser.add_argument('--inpath',  '-i', default=os.getcwd()   , help = 'Input directory')
parser.add_argument('--outpath', '-o', default=None          , help = 'Output directory')
parser.add_argument('--test',   '-t' , action='store_true'   , help = 'Run test')

args = parser.parse_args()
in_dir  = args.inpath
out_dir = args.outpath
dotest  = args.test

if dotest:
    if out_dir is None:
        out_dir = os.path.join(os.getcwd(), 'test')
    else:
        out_dir = os.path.join(out_dir, 'test')

TSTAMP1 = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
TSTAMP2 = datetime.datetime.now().strftime('%Y-%m-%d')

frmt = LvlFormatter()
logging.getLogger().setLevel(logging.DEBUG)

# Configure logging to also output to stdout
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(frmt)
logging.getLogger('').addHandler(console)

# Delete the files on the output directory only if it's given by the user
if out_dir is None:
    out_dir = os.getcwd() # Default output path: the current directory
else:
    if not os.path.exists(out_dir):
        print "Making output directory: %s" % (out_dir)
        os.makedirs(out_dir)
    for filename in os.listdir(out_dir):
        file_path = os.path.join(out_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            
macro_dir = os.path.join(CONST.EFTFIT_TEST_DIR,'../scripts/')
root_args = "\"{indir}\",\"{outdir}\"".format(indir=in_dir,outdir=out_dir)
subprocess.check_call(['root','-b','-l','-q', macro_dir + 'overlay_operator_variations.C+({args})'.format(args=root_args)])
    
to_convert = get_files('.',targets=['.eps','.ps'])
for fn in to_convert:
    continue
    # Note:
    #   This is so that the "\ell" symbol can get rendered properly when converted to a PDF and
    #   displayed in the analysis paper built by CMS TeX tools
    subprocess.check_call(['sed','-i','-e',"s|STIXGeneral-Italic|STIXXGeneral-Italic|g",fn])
    # The '-dEPSCrop' is to fix the large whitespace caused by bound box
    # ps_conv_args = ['ps2pdf14','-dPDFSETTINGS=/prepress','-dEPSCrop',fn]
    # print " ".join(ps_conv_args)
    subprocess.check_call(['ps2pdf14','-dPDFSETTINGS=/prepress','-dEPSCrop',fn])

# Skip this step if the output path is the current directory
if not out_dir is os.getcwd():
    plots = get_files('.',targets=['.png','.pdf','.ps','.eps'])
    if 0:#len(plots):
        for fn in plots:
            print "fname: {}".format(fn)
        move_files(plots,out_dir)
        make_html(out_dir)
