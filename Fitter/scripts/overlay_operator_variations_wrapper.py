import os
import logging
import subprocess
import datetime

import EFTFit.Fitter.consts as CONST

from EFTFit.Fitter.LvlFormatter import LvlFormatter
from EFTFit.Fitter.CombineHelper import CombineHelper
from EFTFit.Fitter.utils import get_files, move_files, clean_dir
from EFTFit.Fitter.make_html import make_html

# Desc:
#   Python wrapper to run the overlay_operator_variations.C ROOT macro. It runs on output produced
#   by the combine_helper.py code. It looks for input directories starting in the 'test' directory
#   of the EFTFit/Fitter package and tries to create and move output files (usually png/pdf plots)
#   to a webarea starting in ~/www/eft_stuff/misc/fitting_plots

TSTAMP1 = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
TSTAMP2 = datetime.datetime.now().strftime('%Y-%m-%d')

frmt = LvlFormatter()
logging.getLogger().setLevel(logging.DEBUG)

# Configure logging to also output to stdout
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(frmt)
logging.getLogger('').addHandler(console)

helper = CombineHelper(home=os.getcwd())

web_area = os.path.join(CONST.USER_DIR,'www')
dir_ver  = 'data2017v1'  # This is sort of versioning for which version of the histogram file is being used
testing  = True

dirs = [
    #'SM_fitting_2019-04-04_1051_simultaneous_allcats',
    #'SM_fitting_2019-04-04_1945_simultaneous_3l',
    #'SM_fitting_2019-04-03_1357_simultaneous-notllq_2lss'
    #'SM_fitting_2019-04-10_2022_simultaneous_adhocSFs_allcats',
    #'SM_fitting_2019-04-10_2144_simultaneous_allcats_centralSamples',
    #'SM_fitting_2019-04-19_1229_simultaneous_reducedJetBins_allcats',
    # 'SM_fitting_2019-04-23_1822_simultaneous_newAdhocSFs_allcats'
    # 'SM_fitting_2019-12-06_ana32_private'
    # 'SM_fitting_2020-01-10_ana32_central'
    # 'SM_fitting_2020-01-11_ana32_central'
    # 'SM_fitting_2020-01-22_ana32_private_sgnl_Default-PSWeights-Symmetrized_MatchingSyst_moreStats'
    # 'EFT_fitting_testing'
    # 'EFT_fitting_2020-01-10_ana32_private'
    # 'EFT_fitting_2020-01-22_ana32_private_sgnl_Default-PSWeights-Symmetrized_MatchingSyst_moreStats'
    # 'EFT_fitting_2020-03-31_ana32_private_sgnl_Default-PSWeights-Symmetrized_MatchingSyst_moreStats_with-NuisOnly',
    # 'EFT_fitting_2020-04-01_ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_with-NuisOnly',
    'EFT_fitting_2020-04-02_ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_with-NuisOnly_cmin0', # This is the one most commonly used in the TOP-19-001 Paper
    # 'EFT_fitting_2020-04-02_ana32_private_sgnl_Decorrelated-PS-PDF-Q2RF-QCUT_with-NuisOnly_cmin2'
]

for d in dirs:
    print d
    input_dir  = os.path.join(CONST.EFTFIT_TEST_DIR,dir_ver,d)
    output_dir = os.path.join(web_area,'eft_stuff/misc/fitting_plots',dir_ver,"{tstamp}_{dir}".format(tstamp=TSTAMP2,dir=d))
    if testing:
        output_dir = os.path.join(web_area,'eft_stuff/misc/fitting_plots','testing')
    # output_dir = helper.getOutputDirectory()

    if not os.path.exists(output_dir):
        print "Making output directory: %s" % (output_dir)
        os.makedirs(output_dir)
    helper.cleanDirectory(output_dir)

    root_args = "\"{indir}\",\"{outdir}\"".format(indir=input_dir,outdir=output_dir)
    # subprocess.check_call(['root','-b','-l','-q','overlay_operator_variations.C(\"%s\",\"%s\")' % (input_dir,output_dir)])
    subprocess.check_call(['root','-b','-l','-q','overlay_operator_variations.C({args})'.format(args=root_args)])
    plots = get_files('.',targets=['.png','.pdf'])
    if len(plots):
        for fn in plots:
            print "fname: {}".format(fn)
        move_files(plots,output_dir)
        make_html(output_dir)