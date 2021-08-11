from ROOT import TFile,RooWorkspace,RooRealVar,RooFit
import os
import re

filenames = ['wps_2lss_p_4j_2b_ptbl.root', 'wps_2lss_p_5j_2b_ptbl.root', 'wps_2lss_p_6j_2b_ptbl.root', 'wps_2lss_p_7j_2b_ptbl.root']
master_file = '_'.join(re.split('_\dj_', filenames[0]))
master_file = master_file[:-5] + '_merge.root'
os.system('cp {} {}'.format(filenames[0], master_file))
all_vars = {}
master_file = TFile.Open(master_file, 'update')
master_w = master_file.Get('w')
master_w.allFunctions().Print()
for filename in filenames[1:]:
    fin = TFile.Open(filename)
    w = fin.Get('w')
    args = w.allFunctions()
    iter = args.createIterator()
    var = iter.Next()
    while var:
        v = var.GetName()
        if v in all_vars: continue
        if 'bin' in v:
            imp = ':'.join([filename,'w',v])
            getattr(master_w,'import')(imp, RooFit.Silence()) # import is a keyword, cannot use as a method https://root-forum.cern.ch/t/rooworkspace-roofit-not-importing-in-pyroot/9510 
            all_vars[v] = v
        var = iter.Next()
    args = w.allPdfs()
    iter = args.createIterator()
    var = iter.Next()
    while var:
        v = var.GetName()
        if v in all_vars: continue
        if 'bin' in v:
            imp = ':'.join([filename,'w',v])
            getattr(master_w,'import')(imp, RooFit.Silence())
            all_vars[v] = v
        var = iter.Next()
master_w.Write()
master_file.Close()
