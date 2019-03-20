print "Importing libraries..."
import numpy as np
import itertools
import os
import ROOT
ROOT.gSystem.Load('$CMSSW_BASE/src/EFTFit/Fitter/interface/TH1EFT_h.so')

#Dict that will hold the parameterizations of the cross-sections
fits = {}

#List of operators to extract parameterizations for
operators = ['sm']+['ctW','ctp','cpQM','ctZ','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
#operators = ['sm']+['ctW'] #Debug, but unnecessary

#Load file
print "Loading Root file..."
readfile = ROOT.TFile.Open(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/hist_files/anatest15.root')

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
        for bin in range(1,5): # Doesn't include bin 5
            category_njet = ''
            if "2lss" in category:
                category_njet = 'C_{0}_{1}{2}j'.format(category, 'ge' if bin==4 else '', bin+3)
            if "3l" in category:
                category_njet = 'C_{0}_{1}{2}j'.format(category, 'ge' if bin==4 else '', bin+1)
            if "4l" in category:
                category_njet = 'C_{0}_{1}{2}j'.format(category, 'ge' if bin==4 else '', bin)
            fit = hist.GetBinFit(bin)
            #if bin==4:
            #    print category_njet,fit.getCoefficient('sm','sm'),fit.getCoefficient('ctW','sm'),fit.getCoefficient('ctW','ctW')
            #print category_njet,fit.getCoefficient('sm','sm')
            names = fit.getNames()
            if len(names)!=0 and fit.getCoefficient('sm','sm')==0:
                for op1 in operators:
                    for op2 in operators:
                        if fit.getCoefficient(op1,op2)!=0:
                            print "Error! SM yield is 0, but this bin has a nonzero contribution from EFT effects! The parameterization for this bin will be ignored."
                            print "    "+process,category_njet
                            print "    "+op1,op2," ",round(fit.getCoefficient(op1,op2),8)
                
            if len(names)==0 or fit.getCoefficient('sm','sm')==0: continue
            if (process,category_njet) not in fits.keys(): fits[(process,category_njet)]={}
#            for pair in itertools.combinations_with_replacement(operators,2):
#                fits[(process,category_njet)][pair] = round(fit.getCoefficient(pair[0],pair[1])/fit.getCoefficient('sm','sm'),8)
            for op1 in operators:
                for op2 in operators:
                    #if category_njet=='C_2lss_m_ee_2b_ge7j' and op2 == 'sm' and op1 != 'sm': print process,[op1,op2],fit.getCoefficient(op1,op2)
                    #if category_njet=='C_2lss_m_ee_2b_ge7j' and op2 == 'cbW' and op1 != 'sm': print process,[op1,op2],fit.getCoefficient(op1,op2)
                    #if category_njet=='C_2lss_m_ee_2b_ge7j' and op2 == 'cbW' and op1 != 'cbW': print process,[op1,op2],fit.getCoefficient(op1,op2)
                    fits[(process,category_njet)][(op1,op2)] = round(fit.getCoefficient(op1,op2)/fit.getCoefficient('sm','sm'),8)
                    #fits[(process,category_njet)][(op1,op2)] = round(fit.getCoefficient(op1,op2),8)

#print fits
print "Saving numpy file {}...".format("16D_Parameterization.npy")
#print "Categories:",[key[1] for key in fits.keys()]
#print "Processes:",[key[0] for key in fits.keys()]
#print "Keys:",fits.keys()
np.save(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/hist_files/16D_Parameterization.npy', fits)
