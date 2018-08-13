print "Importing libraries..."
import numpy as np
import itertools
import os
import ROOT
ROOT.gSystem.Load('$CMSSW_BASE/src/EFTFit/Fitter/interface/TH1EFT_h.so')

#Dict that will hold the parameterizations of the cross-sections
fits = {}

#List of operators to extract parameterizations for
operators = ['sm']+['cptb','cpt','ctlT1','cpQ3','cpQM','ctG','cbW','cQl31','ctl1','ctp','ctlS1','ctZ','cQe1','cQlM1','cte1','ctW']

#Load file
print "Loading Root file..."
readfile = ROOT.TFile.Open(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/anatest8.root')

#Crawl through file
print "Extracting parameterizations..."
for key in readfile.GetListOfKeys():
    hist = readfile.Get(key.GetName())

    #Get categorical information
    histname = hist.GetName().split('.')
    category,systematic,process = '','',''
    if(len(histname)==3): [category,systematic,process] = histname
    if(len(histname)==2): [category,process] = histname
    #For now, treat tllq, ttll, ttlnu as tZq, ttZ, ttW
    #process = process.replace('tllq','tZq')
    #process = process.replace('ttll','ttZ')
    #process = process.replace('ttlnu','ttW')

    #Skip systematic histograms
    if systematic != '': continue

    #Only use histograms from WC samples
    if '16D' in process:
        process = process.split('_',1)[0]

        #Loop through bins and extract parameterization
        for bin in range(1,hist.GetNbinsX()):
            category_njet = 'C_{0}_{1}j'.format(category,bin)
            fit = hist.GetBinFit(1+bin)
            names = fit.getNames()
            if len(names)==0: continue
            if (process,category_njet) not in fits.keys(): fits[(process,category_njet)]={}
            for pair in itertools.combinations_with_replacement(operators,2):
                fits[(process,category_njet)][pair] = round(fit.getParameter(pair[0],pair[1])/fit.getParameter('sm','sm'),8)
            for op1 in operators:
                for op2 in operators:
                    fits[(process,category_njet)][(op1,op2)] = round(fit.getParameter(op1,op2)/fit.getParameter('sm','sm'),8)
                    #fits[(process,category_njet)][(op1,op2)] = round(fit.getParameter(op1,op2),8)

print "Saving numpy file {}...".format("16D_Parameterization.npy")
#print "Categories:",[key[1] for key in fits.keys()]
#print "Processes:",[key[0] for key in fits.keys()]
#print "Keys:",fits.keys()
np.save(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/16D_Parameterization.npy', fits)
