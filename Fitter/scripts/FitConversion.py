print "Importing libraries..."
import numpy as np
import os
import ROOT
ROOT.gSystem.Load('$CMSSW_BASE/src/EFTFit/Fitter/interface/TH1EFT_h.so')

#Dict that will hold the parameterizations of the cross-sections
scales = {}

#Load file
print "Loading Root file..."
readfile = ROOT.TFile.Open(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/anatest7.root')

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
#    if process.rsplit('_',1)[1] not in ['ctZ','ctW','ctp','ctl1','ctG','cQe1','cpt','cptb','cpQM','cpQ3']:
    if any(op in process for op in ['ctZ','ctW','ctp','ctl1','ctG','cQe1','cpt','cptb','cpQM','cpQ3']):
        process,operator = process.rsplit('_',1)

        #Loop through bins and extract parameterization
        for bin in range(1,hist.GetNbinsX()):
            category_njet = 'C_{0}_{1}j'.format(category,bin)
            fit = hist.GetBinFit(1+bin)
            coeffs = []
            names = fit.getNames()
            if len(names)==0: continue         
            coeffs.insert(0, round(fit.getParameter('sm','sm')/fit.getParameter('sm','sm'),8))
            coeffs.insert(1, round(fit.getParameter('sm',operator)/fit.getParameter('sm','sm'),8))
            coeffs.insert(2, round(fit.getParameter(operator,operator)/fit.getParameter('sm','sm'),8))
            #coeffs.insert(0, round(fit.getParameter('sm','sm'),8))
            #coeffs.insert(1, round(fit.getParameter('sm',operator),8))
            #coeffs.insert(2, round(fit.getParameter(operator,operator),8))
            if operator not in scales: #Check if dict key is initialized
                scales[operator] = {}
            scales[operator].update({(process,category_njet):tuple(coeffs)})

print "Saving numpy file {}...".format("scales.npy")
print "Keys:",scales.keys()
np.save(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/scales.npy', scales)
