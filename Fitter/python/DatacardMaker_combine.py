from HistoReader import HistoReader
import ROOT as r 
import re 

def cropNegativeYields(histo):
    for bin in range(1, histo.GetNbinsX()+1):
        if histo.GetBinContent(bin)<0:
            print('[W]: Negative yields in %s: %f. Cropping to zero'%(histo.GetName(), histo.GetBinContent(bin)))
            histo.SetBinContent(bin,0)
    return histo

class DatacardMaker:
    def __init__(self):
        self.hr = HistoReader('../hist_files/anatest32_MergeLepFl.root')
        self.hr.readFromPickle('histos.pickle')
        self.eras=['2017']
        self.chan=['multilepton']
        self.outf = "EFT_MultiDim_Datacard_combine.txt"
        
    def makeCard(self):
        #tmp={'3l_mix_sfz_2b': self.hr.th1Tree['3l_mix_sfz_2b']} 
        #self.hr.th1Tree=tmp
        
        categories = [ 'bin_'+cat for cat in self.hr.th1Tree]
        cats = list(enumerate(categories))

        signalNames=self.hr.sgnl_known
        patterns=[['%s_sm'%process, '%s_lin_(?P<c1>.*)'%process, '%s_quad_(?P<c1>.*)'%process, '%s_quad_mixed_(?P<c1>.*)_(?P<c2>.*)'%process] for process in signalNames]
        patterns=[ re.compile(pattern) for patternlist in patterns for pattern in patternlist ] # :) 
        processes=[]
        for cat in self.hr.th1Tree:
            processes+= [proc for proc in self.hr.th1Tree[cat]]
        processes=list(set(processes))
        sig_procs=[]; bkg_procs=[]
        for proc in processes:
            if any( [ pat.match(proc) for pat in patterns]): 
                sig_procs.append(proc)
            elif any([proc=="%s_sm"%bkg for bkg in self.hr.bkgd_known]): 
                bkg_procs.append(proc)
            elif proc=="data_sm":
                pass
            else:
                raise RuntimeError("Process %s not identified"%proc)

 

        signalcount=0; bkgcount=0; iproc = {}
        for cat in self.hr.th1Tree:
            inputs=r.TFile.Open("ttx_multileptons-%s.root"%cat, 'recreate')
            inputs.WriteTObject( self.hr.th1Tree[cat]['data_sm'][''], "data_obs")
            allyields={'data_obs' : self.hr.th1Tree[cat]['data_sm'][''].Integral()  }
            procs=[]; systMap={}

            for proc in self.hr.th1Tree[cat]:
                if proc == 'data_sm': 
                    continue
                if self.hr.th1Tree[cat][proc][''].Integral()<1e-3: 
                    continue
                procs.append(proc)
                if proc not in iproc:
                    if proc in sig_procs:
                        signalcount=signalcount-1
                        iproc[proc]=signalcount
                    else:
                        bkgcount = bkgcount+1
                        iproc[proc]=bkgcount
                        
                

                for syst in self.hr.th1Tree[cat][proc]: 
                    self.hr.th1Tree[cat][proc][syst]=cropNegativeYields(self.hr.th1Tree[cat][proc][syst])
                    if syst=="":
                        allyields[proc]=self.hr.th1Tree[cat][proc][''].Integral()

                    if not self.hr.th1Tree[cat][proc][syst].Integral():
                        print("Warning: underflow template for %s %s %s. Will take the nominal scaled down by a factor 2" % (cat, proc, syst))
                        self.hr.th1Tree[cat][proc][syst].Add(self.hr.th1Tree[cat][proc][''])
                        self.hr.th1Tree[cat][proc][syst].Scale(0.5)
                        

                    inputs.WriteTObject( self.hr.th1Tree[cat][proc][syst], proc if syst== "" else "%s_%s"%(proc,syst.replace("UP","Up").replace("DOWN","Down")))
                    if syst == "" or "DOWN" in syst: continue
                    systName=syst.replace("UP","").replace("DOWN","")
                    if systName in systMap:
                        systMap[systName].append(proc)
                    else:
                        systMap[systName]=[proc]

                        
            inputs.Close()
            nuisances = [syst for syst in systMap]
            

            datacard = open("ttx_multileptons-%s.txt"%cat, "w"); 
            datacard.write("shapes *        * ttx_multileptons-%s.root $PROCESS $PROCESS_$SYSTEMATIC\n" % cat)
            datacard.write('##----------------------------------\n')
            datacard.write('bin         bin_%s\n' % cat)
            datacard.write('observation %s\n' % allyields['data_obs'])
            datacard.write('##----------------------------------\n')
            klen = max([7, len(cat)]+[len(p) for p in procs])
            kpatt = " %%%ds "  % klen
            fpatt = " %%%d.%df " % (klen,3)
            npatt = "%%-%ds " % max([len('process')]+list(map(len,nuisances)))
            datacard.write('##----------------------------------\n')
            datacard.write((npatt % 'bin    ')+(" "*6)+(" ".join([kpatt % ('bin_'+cat)      for p in procs]))+"\n")
            datacard.write((npatt % 'process')+(" "*6)+(" ".join([kpatt % p        for p in procs]))+"\n")
            datacard.write((npatt % 'process')+(" "*6)+(" ".join([kpatt % iproc[p] for p in procs]))+"\n")
            datacard.write((npatt % 'rate   ')+(" "*6)+(" ".join([fpatt % allyields[p] for p in procs]))+"\n")
            datacard.write('##----------------------------------\n')
            #towrite = [ report[p].raw() for p in procs ] + [ report["data_obs"].raw() ]
            for name in nuisances:
                systEff = dict((p,"1" if p in systMap[name] else "-") for p in procs)
                datacard.write(('%s %5s' % (npatt % name,'shape')) + " ".join([kpatt % systEff[p]  for p in procs]) +"\n")

if __name__ == "__main__":
    dm=DatacardMaker()
    dm.makeCard()
