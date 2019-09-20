#!/usr/bin/env python
import ROOT
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("basename", help="basename of fit file to extract discontinuities from")
parser.add_argument("poi", help="parameter to find discontinuities in")
args = parser.parse_args()

systematics = ['CERR1','CERR2','CMS_eff_em','CMS_scale_j','ChargeFlips','FR_FF','LEPID','MUF','MUR','PDF','PSISR','PU',
               'QCDscale_V','QCDscale_VV','QCDscale_VVV','QCDscale_tHq','QCDscale_ttG','QCDscale_ttH','QCDscale_ttbar',
               'hf','hfstats1','hfstats2','lf','lfstats1','lfstats2','lumi_13TeV_2017','pdf_gg','pdf_ggttH','pdf_qgtHq','pdf_qq',
              ]

print('../fit_files/higgsCombine{}.MultiDimFit.root'.format(args.basename))
rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(args.basename))
limitTree = rootFile.Get('limit')

for entry in range(2,limitTree.GetEntries()): # 0 is the fit point, so ignore it
    limitTree.GetEntry(entry-1)
    deltaNLLprev = limitTree.GetLeaf('deltaNLL').GetValue(0)+1
    tllqprev = round(limitTree.GetLeaf(args.poi).GetValue(0),3)
    limitTree.GetEntry(entry)
    tllqcurr = round(limitTree.GetLeaf(args.poi).GetValue(0),3)
    deltaNLLcurr = limitTree.GetLeaf('deltaNLL').GetValue(0)+1
    if(abs(deltaNLLcurr-deltaNLLprev)/deltaNLLprev > 0.03):
        print("Found deltaNLL discontinuity between {} [{},{}]".format(args.poi,tllqprev,tllqcurr))
        for sys in systematics:
            syscurr = round(limitTree.GetLeaf('trackedParam_'+sys).GetValue(0),3)
            limitTree.GetEntry(entry-1)
            sysprev = round(limitTree.GetLeaf('trackedParam_'+sys).GetValue(0),3)
            limitTree.GetEntry(entry)
            if(abs(syscurr-sysprev)/(sysprev+1) > 0.03 and abs(syscurr-sysprev) > 0.3):
                print("Found discontinuity in systematic {}, [{},{}]".format(sys,sysprev,syscurr))
