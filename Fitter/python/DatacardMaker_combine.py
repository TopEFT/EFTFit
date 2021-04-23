import CombineHarvester.CombineTools.ch as ch
from HistoReader import HistoReader
import ROOT as r 
import re 

def cropNegativeYields(histo):
    for bin in range(1, histo.GetNbinsX()+1):
        if histo.GetBinContent(bin)<0:
            print '[W]: Negative yields in %s: %f. Cropping to zero'%(histo.GetName(), histo.GetBinContent(bin))
            histo.SetBinContent(bin,0)
    return histo

class DatacardMaker:
    def __init__(self):
        self.hr = HistoReader('../hist_files/anatest32_MergeLepFl.root')
        self.hr.readFromPickle('histos.pickle')
        self.cb = ch.CombineHarvester()
        self.cb.SetVerbosity(0)
        self.eras=['2017']
        self.chan=['multilepton']
        self.outf = "EFT_MultiDim_Datacard_combine.txt"
        
    def makeCard(self):
        #tmp={'3l_mix_sfz_2b': self.hr.th1Tree['3l_mix_sfz_2b']} 
        #self.hr.th1Tree=tmp
        
        categories = [ 'bin_'+cat for cat in self.hr.th1Tree]
        cats = list(enumerate(categories))

        self.cb.AddObservations( ['*'], ['Top_EFT'], self.eras, self.chan, cats )
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

 

        # create file to store inputs
        inputs=r.TFile.Open("ttx_multileptons-inputs.root", 'recreate')
        for cat in self.hr.th1Tree:
            inputs.mkdir('bin_'+cat)
            subdir=inputs.Get('bin_'+cat)
            subdir.WriteTObject( self.hr.th1Tree[cat]['data_sm'][''], "data_obs")
            for proc in self.hr.th1Tree[cat]:
                print 'Processing', proc
                if proc == 'data_sm': 
                    continue
                if self.hr.th1Tree[cat][proc][''].Integral()<1e-3: 
                    continue
                self.cb.AddProcesses( ['*'], ['Top_EFT'], self.eras, self.chan, [proc], [x for x in cats if 'bin_'+cat==x[1]], bool(proc in sig_procs))
                for syst in self.hr.th1Tree[cat][proc]: 
                    self.hr.th1Tree[cat][proc][syst]=cropNegativeYields(self.hr.th1Tree[cat][proc][syst])
                    subdir.WriteTObject( self.hr.th1Tree[cat][proc][syst], proc if syst== "" else "%s_%s"%(proc,syst))
                    #self.cb.cp().process([proc]).AddSyst(self.cb, syst, "shape", ch.SystMap()(1.00))
        print 'Done'
        inputs.Close()
                
        self.cb.cp().backgrounds().ExtractShapes(
            "ttx_multileptons-inputs.root",
            "$BIN/$PROCESS",
            "$BIN/$PROCESS_$SYSTEMATIC");
               
        self.cb.cp().signals().ExtractShapes(
            "ttx_multileptons-inputs.root",
            "$BIN/$PROCESS",
            "$BIN/$PROCESS_$SYSTEMATIC");

        output=r.TFile.Open(self.outf.replace('.txt','.root'),"recreate")
        self.cb.WriteDatacard(self.outf, output)
        output.Close()


if __name__ == "__main__":
    dm=DatacardMaker()
    dm.makeCard()
