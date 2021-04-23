import ROOT as r 
import copy
from array import array
import pickle 


r.gSystem.Load('$CMSSW_BASE/lib/$SCRAM_ARCH/libEFTGenReaderEFTHelperUtilities.so')

def addProcessToDict(dic, process, systematic, histo):
    if  process not in dic :
        dic[process]={}
    dic[process][systematic]=histo

def getHistAtPoint( point, th1eft, name):
    binning=array('d', [th1eft.GetBinLowEdge(1)]+[th1eft.GetBinLowEdge(i)+th1eft.GetBinWidth(i) for i in range(1, th1eft.GetNbinsX()+1)])
    outh=r.TH1D(name,'', len(binning)-1, binning)
    for bin in range(1, outh.GetXaxis().GetNbins()+1):
        outh.SetBinContent(bin, th1eft.GetBinContent( bin, point))
        # To do SetBinError (things to be fixed downstream as well)
    return outh
        
        


class HistoReader(object):
    def __init__(self, infile='', fakeData=False, pointForFakeData=None, central=False):


        self.sgnl_known = ['ttH','tllq','ttll','ttlnu','tHq']
        self.sgnl_histnames = [sgnl + '_' + '16D' for sgnl in self.sgnl_known] if not central else ['ttH','tllq','ttll','ttlnu','tHq_16D']
        self.bkgd_known = ['charge_flips','fakes','Diboson','Triboson','convs']
        self.data_known = ['data'] 
        self.coefs = ["cptb", "ctlSi", "cpt", "ctei", "cpQ3", "ctli", "ctW", "ctlTi", "cpQM", "cQei", "cQl3i", "ctp", "ctZ", "cQlMi", "cbW", "ctG"]
        

        self.fakeData=fakeData # to do 
        self.pointForFakeData=pointForFakeData if pointForFakeData else r.WCPoint() # None for SM
        
        self.readfile = r.TFile.Open(infile)
        if not self.readfile:
            raise RuntimeError("Failed to open file %s ! "%infile)

        self.processList=[]
        self.eftTree={} 
        self.th1Tree={} 
        self.categories=[]

    def read(self):
        
        for key in self.readfile.GetListOfKeys():
            hist=key.ReadObj()
            histname = hist.GetName().split('.')
            category,systematic,process = '','',''
            if(len(histname)==3): [category,systematic,process] = histname
            if(len(histname)==2): [category,process] = histname

            # For accurate naming of backgrounds:
            process = process.replace('ttGJets','convs')
            process = process.replace('WZ','Diboson')
            process = process.replace('WWW','Triboson')
            
            if process not in self.sgnl_histnames+self.bkgd_known+self.data_known: 
                continue

            process = process.replace('tZq','tllq')
            process = process.replace('ttZ','ttll')
            process = process.replace('ttW','ttlnu')
            process = process.replace("_16D","")


            # For accurate naming of systematics:
            systematic = systematic.replace('FR','FR_FF') # Don't touch this without changing below!


            if process not in self.processList:
                self.processList.append(process)
                self.eftTree[process]={}
            
            if category not in self.eftTree[process]:
                self.eftTree[process][category]={}
                
            if systematic in self.eftTree[process][category]:
                raise RuntimeError("Systematic %s for process %s in category %s already added "%(systematic, process, category))

            self.eftTree[process][category][systematic]=hist

    
    def convertToTH1(self):
        for process in self.eftTree:
            print 'Processing', process

            for category in self.eftTree[process]:
                if category not in self.th1Tree:
                    self.th1Tree[category]={}
                                        
                for systematic in self.eftTree[process][category]:
                    
                    th1eft=self.eftTree[process][category][systematic]
                    point_sm=r.WCPoint()
                    th1_sm=getHistAtPoint( point_sm, th1eft, "%s.%s.%s.sm"%(process,category,systematic))                     
                    currentWCs = list(set([ x for bin in range(1, th1eft.GetNbinsX()+1) for x in th1eft.GetBinFit(bin).getNames()])) # WC in this th1eft

                    addProcessToDict( self.th1Tree[category], '%s_sm'%process,  systematic, th1_sm)

                    if process not in self.sgnl_known:
                        continue
                    print process
                    for i1, wc1 in enumerate(self.coefs):
                        
                        if wc1 in currentWCs:
                            point_wc=r.WCPoint(); point_wc.setStrength(wc1, 1)
                            th1_lin=getHistAtPoint( point_wc, th1eft, "%s.%s.%s.lin_%s"%(process,category,systematic, wc1))
                            addProcessToDict( self.th1Tree[category], '%s_lin_%s'%(process,wc1), systematic, th1_lin)
                            
                            point_wc=r.WCPoint(); point_wc.setStrength(wc1, 2)
                            th1_quad=getHistAtPoint( point_wc, th1eft, "%s.%s.%s.quad_%s"%(process,category,systematic, wc1))
                            th1_quad.Add(th1_lin, -2)
                            th1_quad.Add(th1_sm)
                            r.TH1D.Scale(th1_quad,0.5)
                            addProcessToDict( self.th1Tree[category], '%s_quad_%s'%(process,wc1), systematic, th1_quad)
                            
                            for i2,wc2 in enumerate(self.coefs): 
                                if i1>=i2: continue
                                if wc2 in currentWCs:
                                    point_wc=r.WCPoint(); point_wc.setStrength(wc1, 1); point_wc.setStrength(wc2,1)
                                    th1_quad_mixed=getHistAtPoint( point_wc, th1eft, "%s.%s.%s.quad_mixed_%s_%s"%(process,category,systematic, wc1, wc2))
                                    addProcessToDict( self.th1Tree[category], '%s_quad_mixed_%s_%s'%(process,wc1,wc2), systematic, th1_quad_mixed)
                                else: 
                                    # if wc2 is not there then this term is S+L_1+Q_1
                                    point_wc=r.WCPoint(); point_wc.setStrength(wc1, 1)
                                    th1_quad_mixed=getHistAtPoint( point_wc, th1eft, "%s.%s.%s.quad_mixed_%s_%s"%(process,category,systematic, wc1, wc2))
                                    addProcessToDict( self.th1Tree[category], '%s_quad_mixed_%s_%s'%(process,wc1,wc2), systematic, th1_quad_mixed)
                                    
                        else:
                            print 'Coefficient %s does not exist!'%wc1
                            # if the wc does not exist (the dependence is zero) the linear term is that of the sm 
                            th1_lin=th1_sm.Clone( "%s.%s.%s.lin_%s"%(process,category,systematic, wc1))
                            addProcessToDict( self.th1Tree[category], '%s_lin_%s'%(process,wc1), systematic, th1_lin)

                            # the quadratic is zero
                            th1_quad=th1_sm.Clone( "%s.%s.%s.lin_%s"%(process,category,systematic, wc1))
                            th1_quad.Reset()
                            addProcessToDict( self.th1Tree[category], '%s_quad_%s'%(process,wc1), systematic, th1_quad)
                            for i2,wc2 in enumerate(self.coefs): 
                                if i1>=i2: continue
                                if wc2 not in currentWCs:
                                    # if wc2 is not there either, this is just the SM 
                                    th1_quad_mixed=th1_sm.Clone("%s.%s.%s.quad_mixed_%s_%s"%(process,category,systematic, wc1, wc2))
                                    addProcessToDict( self.th1Tree[category], '%s_quad_mixed_%s_%s'%(process,wc1,wc2), systematic, th1_quad_mixed)
                                else:
                                    # if it is there then it is S+L_2+Q_2
                                    point_wc=r.WCPoint(); point_wc.setStrength(wc2, 1)
                                    th1_quad_mixed=getHistAtPoint( point_wc, th1eft, "%s.%s.%s.quad_mixed_%s_%s"%(process,category,systematic, wc1, wc2))
                                    addProcessToDict( self.th1Tree[category], '%s_quad_mixed_%s_%s'%(process,wc1,wc2), systematic, th1_quad_mixed)

                                    

                            
        with open('histos.pickle', 'wb') as handle:
            pickle.dump(self.th1Tree, handle, protocol=pickle.HIGHEST_PROTOCOL)                            
        
    def readFromPickle(self,pk):
        f = open(pk, 'rb')
        self.th1Tree=pickle.load(f)


if __name__ == "__main__":
    hr=HistoReader('../hist_files/anatest32_MergeLepFl.root')
    hr.read()
    hr.convertToTH1()
