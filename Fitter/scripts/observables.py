import numpy as np
import ROOT
import json
import sys
from collections import OrderedDict
import optparse

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-j', '--json',        dest='json'  ,      help='json with list of files',        default='/afs/crc.nd.edu/user/b/byates2/CMSSW_8_1_0/src/EFTFit/Fitter/test/wc.json',              type='string')
(opt, args) = parser.parse_args()


#read list of samples                                              
jsonFile = open(opt.json,'r')
wcs=json.load(jsonFile,encoding='utf-8',object_pairs_hook=OrderedDict)#.items()
jsonFile.close()

fits = np.load('../hist_files/EFT_Parameterization.npy')[()]
bins = []
for procbin in fits:
    name = 'r_{0}_{1}'.format(procbin[0],procbin[1])
    bins.append((procbin[1],procbin[0]))
bins.sort()

obs = ['_'.join(o.split('_')[1:]) for o,_ in bins]
obs = list(dict.fromkeys(obs))
obs.sort()
obs_hist = ['_'.join(o.split('_')[:-2]) for o in obs]
obs_hist = list(dict.fromkeys(obs_hist))
obs_hist.sort()
obs_wc = ROOT.TH2F('obsVwc', 'Observables vs WCs', 16, 0, 16, len(obs_hist), 0, len(obs_hist))
#uncomment for all bins
#for i in xrange(0, len(obs)):
#    label = obs[i].replace('ge', '#geq')
#    #label = ' '.join(label.split('_'))
#    obs_wc.GetYaxis().SetBinLabel(i+1, label)
for i in xrange(0, len(obs_hist)):
    obs_wc.GetYaxis().SetBinLabel(i+1, obs_hist[i])

fin = ROOT.TFile('EFTWorkspace.root')
w = fin.Get('w')
wcs=wcs[0]
for wc in xrange(0, len(wcs)):
    obs_wc.GetXaxis().SetBinLabel(wc+1, wcs.keys()[wc])
    for limit in wcs[wcs.keys()[wc]]: #loop over -2 sigma and 2 sigma
        r = []
        proc_sm = {}
        proc = {}
        for bin in bins: #loop over all bins
            #replace b with bin[0] for all bins
            b = '_'.join(bin[0].split('_')[:-2])
            if b not in proc_sm:
                proc_sm[b] = []
            if b not in proc:
                proc[b] = []
            #name = 'r_{0}_{1}'.format(bin[1],bin[0]) #generate RooWorkspace signal strength name
            name = 'n_exp_bin{1}_proc_{0}'.format(bin[1],bin[0]) #generate RooWorkspace signal strength name
            proc_sm[b].append(w.function(name).getVal()) #store the signal strength
            w.var(wcs.keys()[wc]).setVal(limit) #set WC to CI
            proc[b].append(w.function(name).getVal()) #store the signal strength
            w.var(wcs.keys()[wc]).setVal(0) #set WC back to to SM
    if wcs.keys()[0] == wc:
        proc_sm_lst = list(proc_sm)
        proc_sm_lst.sort()
    for p,v in proc.items():
        proc_lst = list(proc)
        proc_lst.sort()
    for prc in zip(proc.items(),proc_sm.items()):
        pr = [x for p in prc for x in p]
        obs_wc.Fill(wc, proc_lst.index(pr[0]), (sum(pr[1]) - sum(pr[3]))/sum(pr[3])**.5) #fill 2D hist
        #if 'mix' in pr[0] and wc == 0: print pr[0], wcs.keys()[wc], (sum(pr[1]) - sum(pr[3])) / sum(pr[3])**.5

obs_wc.GetXaxis().SetLabelSize(0.02)
obs_wc.GetYaxis().SetLabelSize(0.02)
obs_wc.SetMarkerSize(0.5)
obs_wccol = obs_wc.Clone('obs_wccol')
#normalize colors to column max
for wc in xrange(0, len(wcs)):
    sum = 0
    max = 0
    for o in xrange(0, len(obs)):
        bin = obs_wc.GetBinContent(wc+1, o+1)
        obs_wc.SetBinError(wc+1, o+1, abs(bin)**.5)
        sum = sum + bin
        if abs(bin) > max: max = abs(bin)
    for o in xrange(0, len(obs)):
        bin = abs(obs_wccol.GetBinContent(wc+1, o+1))
        obs_wccol.SetBinContent(wc+1, o+1, abs(bin)) #np.interp(bin, [0, max], [0, 1]))

ROOT.gROOT.SetBatch(True)
canvas = ROOT.TCanvas('canvas','Observable vs WC',1600,1200)
#canvas = ROOT.TCanvas()
canvas.SetGrid(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPaintTextFormat('4.2f')
obs_wccol.SetMaximum(7)
obs_wccol.SetMinimum(-1e-2)
obs_wccol.Draw('colz')
obs_wc.SetMaximum(7)
obs_wc.Draw('same text')
canvas.Print('hist_normCol.pdf')
canvas.Print('hist_normCol.png')
