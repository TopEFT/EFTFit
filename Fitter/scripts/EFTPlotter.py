import ROOT
import logging
import os
import sys
import numpy
import itertools
import subprocess as sp
import os
from EFTFit.Fitter.ContourHelper import ContourHelper
from scipy.signal import argrelextrema

class EFTPlot(object):
    def __init__(self,wc_ranges=None):
        self.logger = logging.getLogger(__name__)
        self.ContourHelper = ContourHelper()

        self.SMMus = ['mu_ttll','mu_ttlnu','mu_ttH','mu_tllq']
        self.wcs = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        self.wcs_pairs = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
        self.wcs = ['cQq13', 'cQq83', 'cQq11', 'ctq1', 'cQq81', 'ctq8', 'ctt1', 'cQQ1', 'cQt8', 'cQt1', 'ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        #self.wcs_pairs = [('ctW','ctG'),('ctZ','ctG'),('ctp','ctG'),('cpQM','ctG'),('cbW','ctG'),('cpQ3','ctG'),('cptb','ctG'),('cpt','ctG'),('cQl3i','ctG'),('cQlMi','ctG'),('cQei','ctG'),('ctli','ctG'),('ctei','ctG'),('ctlSi','ctG'),('ctlTi','ctG')]

        # Set the WC ranges (if not specified, just use some numbers that generally work for njets)
        self.wc_ranges = {
            'cQQ1' : (-4.0,4.0),
            'cQei' : (-4.0,4.0),
            'cQl3i': (-5.5,5.5),
            'cQlMi': (-4.0,4.0),
            'cQq11': (-0.7,0.7),
            'cQq13': (-0.35,0.35),
            'cQq81': (-1.7,1.5),
            'cQq83': (-0.6,0.6),
            'cQt1' : (-4.0,4.0),
            'cQt8' : (-8.0,8.0),
            'cbW'  : (-3.0,3.0),
            'cpQ3' : (-4.0,4.0),
            'cpQM' : (-10.0,17.0),
            'cpt'  : (-15.0,15.0),
            'cptb' : (-9.0,9.0),
            'ctG'  : (-0.8,0.8),
            'ctW'  : (-1.5,1.5),
            'ctZ'  : (-2.0,2.0),
            'ctei' : (-4.0,4.0),
            'ctlSi': (-5.0,5.0),
            'ctlTi': (-0.9,0.9),
            'ctli' : (-4.0,4.0),
            'ctp'  : (-11.0,35.0),
            'ctq1' : (-0.6,0.6),
            'ctq8' : (-1.4,1.4),
            'ctt1' : (-2.1,2.1),
        }
        if wc_ranges is not None:
            self.wc_ranges = wc_ranges

        self.sm_ranges = {  'mu_ttH':(0,7),   'mu_ttlnu':(0,3)
                         }
        self.histosFileName = 'Histos.root'
        self.texdic = {'ctW': '\it{c}_{\mathrm{tW}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'ctZ': '\it{c}_{\mathrm{tZ}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'ctp': '\it{c}_{\mathrm{t} \\varphi}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cpQM': '\it{c}^{-}_{\\varphi \mathrm{Q}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'ctG': '\it{c}_{\mathrm{tG}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cbW': '\it{c}_{\mathrm{bW}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cpQ3': '\it{c}^{3}_{\\varphi \mathrm{Q}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cptb': '\it{c}_{\\varphi \mathrm{tb}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cpt': '\it{c}_{\\varphi \mathrm{t}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cQl3': '\it{c}^{3(\\ell)}_{\mathrm{Q}\\ell}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cQlM': '\it{c}^{-(\\ell)}_{\mathrm{Q}\\ell}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cQe': '\it{c}^{(\\ell)}_{\mathrm{Qe}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'ctl': '\it{c}^{(\\ell)}_{\mathrm{t}\\ell}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cte': '\it{c}^{(\\ell)}_{\mathrm{te}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'ctlS': '\it{c}^{S(\\ell)}_{\mathrm{t}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'ctlT': '\it{c}^{T(\\ell)}_{\mathrm{t}}/\mathrm{\Lambda^{2} [TeV^{-2}]}', 'cQq81': '\it{c}^{81}_{\mathrm{Qq}}/\mathrm{\Lambda^{2}} [TeV^{-2}]', 'cQq11': '\it{c}^{11}_{\mathrm{Qq}}/\mathrm{\Lambda^{2}} [TeV^{-2}]', 'ctq8': '\it{c}^{8}_{\mathrm{tq}}/\mathrm{\Lambda^{2}} [TeV^{-2}]', 'ctq1': '\it{c}^{1}_{\mathrm{tq}}/\mathrm{\Lambda^{2}} [TeV^{-2}]', 'cQq13': '\it{c}^{13}_{\mathrm{Qq}}/\mathrm{\Lambda^{2}} [TeV^{-2}]', 'cQq83': '\it{c}^{83}_{\mathrm{Qq}}/\mathrm{\Lambda^{2}} [TeV^{-2}]', 'ctt1': '\it{c}^{1}_{\mathrm{tt}}/\mathrm{\Lambda^{2}} [TeV^{-2}]','cQQ1': '\it{c}^{1}_{\mathrm{QQ}}/\mathrm{\Lambda^{2}} [TeV^{-2}]','cQt8': '\it{c}^{8}_{\mathrm{Qt}}/\mathrm{\Lambda^{2}} [TeV^{-2}]','cQt1': '\it{c}^{1}_{\mathrm{Qt}}/\mathrm{\Lambda^{2}} [TeV^{-2}]'}
        self.texdicfrac = {'ctW': '\it{c}_{\mathrm{tW}}}', 'ctZ': '\it{c}_{\mathrm{tZ}}}', 'ctp': '\it{c}_{\mathrm{t} \\varphi}}', 'cpQM': '\it{c}^{-}_{\\varphi \mathrm{Q}}}', 'ctG': '\it{c}_{\mathrm{tG}}}', 'cbW': '\it{c}_{\mathrm{bW}}}', 'cpQ3': '\it{c}^{3}_{\\varphi \mathrm{Q}}}', 'cptb': '\it{c}_{\\varphi \mathrm{tb}}}', 'cpt': '\it{c}_{\\varphi \mathrm{t}}}', 'cQl3': '\it{c}^{3(\\ell)}_{\mathrm{Q}\\ell}}', 'cQlM': '\it{c}^{-(\\ell)}_{\mathrm{Q}\\ell}}', 'cQe': '\it{c}^{(\\ell)}_{\mathrm{Qe}}}', 'ctl': '\it{c}^{(\\ell)}_{\mathrm{t}\\ell}}', 'cte': '\it{c}^{(\\ell)}_{\mathrm{te}}}', 'ctlS': '\it{c}^{S(\\ell)}_{\mathrm{t}}}', 'ctlT': '\it{c}^{T(\\ell)}_{\mathrm{t}}}', 'cQq81': '\it{c}^{81}_{\mathrm{Qq}}', 'cQq11': '\it{c}^{11}_{\mathrm{Qq}}', 'ctq8': '\it{c}^{8}_{\mathrm{tq}}', 'ctq1': '\it{c}^{1}_{\mathrm{tq}}', 'cQq13': '\it{c}^{13}_{\mathrm{Qq}}', 'cQq83': '\it{c}^{83}_{\mathrm{Qq}}', 'ctt1': '\it{c}^{1}_{\mathrm{tt}}','cQQ1': '\it{c}^{1}_{\mathrm{QQ}}','cQt8': '\it{c}^{8}_{\mathrm{Qt}}','cQt1': '\it{c}^{1}_{\mathrm{Qt}}'}
        self.texdicrev = {v: k for k,v in self.texdic.items()}

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.88, 0.895, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.04)
        self.CMS_text.SetTextAlign(33)
        #self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.88, 0.865, "Preliminary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.04)
        self.CMS_extra.SetTextAlign(33)
        self.CMS_extra.SetTextFont(52)
        #self.CMS_extra.Draw('same')
        self.lumi = 137
        self.arXiv = "arXiv:2012.04120"
        self.Lumi_text = ROOT.TLatex(0.9, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.04)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        #self.Lumi_text.Draw('same')



    # Appends a given string to each item in a list of strings
    def AppendStrToItemsInLst(self,in_lst,in_str):
        out_lst = []
        for item in in_lst:
            if type(item) is not str:
                raise Exception("Error: Cannot append the str to items in this list, not all items are str")
            out_lst.append(item+in_str)
        return out_lst



    # Takes as input two lists (of x values and y values, i.e. WC values and nll values, respecitvely), returns th lists with duplicate x values removed
    # Of the y values corresponding to the duplicate x values, we keep the min y
    def GetUniqueNLL(self,graphwcs,graphnlls):

        # Check the lists for duplicate wc points
        # If there is a duplicate point, take the one with the lowest NLL
        #     - This is necessary when combining the output of multiple random starting point runs
        #     - Note that in order to combine the results from multiple runs, it is very important that the same pre-fit fit was performed in each run (i.e. no randomization)
        #     - This will ensure that the delta NLL values in the file are all relative to the same pre-fit fit point 
        graphwcs_unique = []
        graphnlls_unique = []
        if len(graphwcs) != len(graphnlls): raise Exception("Error: Something is wrong, the wc values and nll values must have the same length.")
        # Loop over the indices inthe list, check for duplicate x values (i.e. duplicate wc points)
        for idx in range(len(graphwcs)):
            wcpt = graphwcs[idx]
            nll  = graphnlls[idx]
            if wcpt not in graphwcs_unique:
                graphwcs_unique.append(graphwcs[idx])
                graphnlls_unique.append(graphnlls[idx])
            else:
                existing_element_idx = graphwcs_unique.index(wcpt)
                existing_nll = graphnlls_unique[existing_element_idx]
                if nll < existing_nll:
                    graphnlls_unique[existing_element_idx] = nll

        return [graphwcs_unique,graphnlls_unique]



    # Takes as input the name of a root file (assumed to be in ../fit_files)
    # Retruns [wc vals in the scan, delta nll vals at each point]
    # Optionally removes duplicate wc points (choosing min nll)
    def GetWCsNLLFromRoot(self,base_name_lst,wc,unique=False):

        graphwcs = []
        graphnlls = []
        for name in base_name_lst:
            if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
                logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
                return [graphwcs,graphnlls]

            # Get scan tree
            rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
            limitTree = rootFile.Get('limit')

            # Get coordinates for TGraph
            for entry in range(limitTree.GetEntries()):
                limitTree.GetEntry(entry)
                graphwcs.append(limitTree.GetLeaf(wc).GetValue(0))
                graphnlls.append(2*limitTree.GetLeaf('deltaNLL').GetValue(0))

            rootFile.Close()

        # Overwrite the lists with the new lists
        # We should now have unique x values, with y corresponding to the min of the set of different y values for this x point
        if unique:
            graphwcs, graphnlls = self.GetUniqueNLL(graphwcs, graphnlls)

        return [graphwcs,graphnlls]



    def ResetHistoFile(self, name=''):
        ROOT.TFile('Histos{}.root'.format(name),'RECREATE')
        self.histosFileName = 'Histos{}.root'.format(name)



    def LLPlot1DEFT(self, name_lst=['.test'], frozen=False, wc='', log=False):
        if not wc:
            logging.error("No WC specified!")
            return

        ROOT.gROOT.SetBatch(True)
        canvas = ROOT.TCanvas()

        graphwcs, graphnlls = self.GetWCsNLLFromRoot(name_lst,wc,unique=True)
        if graphwcs == [] or graphnlls == []:
            # Something went wrong
            print("Error, probably could not find root file")
            return

        # Rezero the y axis and make the tgraphs
        graphnlls = [val-min(graphnlls) for val in graphnlls]
        graph = ROOT.TGraph(len(graphwcs),numpy.asarray(graphwcs),numpy.asarray(graphnlls))
        graph.Draw("AP")
        del graphnlls,graphwcs

        # Squeeze X down to whatever range captures the float points
        xmin = self.wc_ranges[wc][0]
        xmax = self.wc_ranges[wc][1]
        #for idx in range(graph.GetN()):
        #    if graph.GetY()[idx] < 10 and graph.GetX()[idx] < xmin:
        #        xmin = graph.GetX()[idx]
        #    if graph.GetY()[idx] < 10 and graph.GetX()[idx] > xmax:
        #        xmax = graph.GetX()[idx]
        graph.GetXaxis().SetRangeUser(xmin,xmax)
        graph.GetYaxis().SetRangeUser(-0.1,10)

        #Change markers from invisible dots to nice triangles
        graph.SetTitle("")
        graph.SetMarkerStyle(26)
        graph.SetMarkerSize(1)
        graph.SetMinimum(-0.1)

        #Add 1-sigma and 2-sigma lines. (Vertical lines were too hard, sadly)
        canvas.SetGrid(1)

        line68 = ROOT.TLine(xmin,1,xmax,1)
        line68.Draw('same')
        line68.SetLineColor(ROOT.kYellow+1)
        line68.SetLineWidth(3)
        line68.SetLineStyle(7)

        line95 = ROOT.TLine(xmin,4,xmax,4)
        line95.Draw('same')
        line95.SetLineColor(ROOT.kCyan-2)
        line95.SetLineWidth(3)
        line95.SetLineStyle(7)

        # Labels
        Title = ROOT.TLatex(0.5, 0.95, "{} 2#DeltaNLL".format(wc))
        Title.SetNDC(1)
        Title.SetTextAlign(20)
        Title.Draw('same')
        graph.GetXaxis().SetTitle(wc)

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.17, 0.95, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.04)
        self.CMS_text.SetTextAlign(33)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.9, 0.865, "Preliminary")# Simulation")
        #self.CMS_extra = ROOT.TLatex(0.19, 0.92, "Supplementary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.03)
        #self.CMS_extra.SetTextAlign(33)
        self.CMS_extra.SetTextFont(52)
        self.CMS_extra.Draw('same')
        self.arXiv_extra = ROOT.TLatex(0.885, 0.83, "arXiv:2012.04120")# Simulation")
        self.arXiv_extra.SetNDC(1)
        self.arXiv_extra.SetTextSize(0.03)
        #self.arXiv_extra.SetTextAlign(30)
        self.arXiv_extra.SetTextFont(42)
        self.Lumi_text = ROOT.TLatex(0.34, 0.92, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.04)
        #self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        #Check log option, then save as image
        if log:
            graph.SetMinimum(0.1)
            graph.SetLogz()
            canvas.Print('{}1DNLL_log.png'.format(wc,'freeze' if frozen else 'float'),'png')
        else:
            canvas.Print('{}1DNLL.png'.format(wc,'freeze' if frozen else 'float'),'png')


    def duplicates(self, seq, item):
        start_at = -1
        locs = []
        while True:
            try:
                loc = seq.index(item,start_at+1)
            except ValueError:
                break
            else:
                locs.append(loc)
                start_at = loc
        return locs

    def clean_duplicates(self, graphwcs, graphnlls):
        dup = [self.duplicates(graphwcs, x) for x in graphwcs]
        unique_wcs = []
        unique_nlls = []
        for i,_ in enumerate(dup):
            if isinstance(dup[i], list):
               unique_wcs.append(graphwcs[dup[i][-1]])
               unique_nlls.append(graphnlls[dup[i][-1]])
            else:
                unique_wcs.append(graphwcs[dup[i]])
                unique_nlls.append(graphnlls[dup[i]])
        return [unique_wcs, unique_nlls]

    def OverlayLLPlot1DEFT(self,**kwargs):
        name1_lst = kwargs.pop('name1_lst',['.test'])
        name2_lst = kwargs.pop('name2_lst',['.test'])
        wc  = kwargs.pop('wc','')
        d1  = kwargs.pop('dir1','../fit_files')
        d2  = kwargs.pop('dir2','../fit_files')
        pf1 = kwargs.pop('pf1','')
        pf2 = kwargs.pop('pf2','')
        log = kwargs.pop('log',False)
        ceiling = kwargs.pop('log',10)
        final = kwargs.pop('final',False)
        titles = kwargs.pop('titles',['Others Profiled', 'Others Fixed to SM'])
        if not wc:
            logging.error("No wc specified!")
            return
        for name1 in name1_lst:
            if not os.path.exists('{}/higgsCombine{}.MultiDimFit{}.root'.format(d1,name1,pf1)):
                logging.error("File higgsCombine{}.MultiDimFit{}.root does not exist!".format(name1,pf1))
                return
        for name2 in name1_lst:
            if not os.path.exists('{}/higgsCombine{}.MultiDimFit{}.root'.format(d2,name2,pf2)):
                logging.error("File higgsCombine{}.MultiDimFit{}.root does not exist!".format(name2,pf2))
                return

        ROOT.gROOT.SetBatch(True)

        canvas = ROOT.TCanvas('canvas', 'canvas', 700, 530)
        p1 = ROOT.TPad('p1', 'p1', 0, 0.05, 1.0, 1.0)
        p1.Draw()
        p1.cd()

        # Get coordinates for TGraphs
        graph1wcs,graph1nlls = self.GetWCsNLLFromRoot(name1_lst,wc,unique=True)
        graph2wcs,graph2nlls = self.GetWCsNLLFromRoot(name2_lst,wc,unique=True)

        # Rezero the y axis and make the tgraphs
        #zero = graph1nlls.index(0)
        zero = 0
        for n,z in enumerate(graph1nlls):
            if abs(z) < abs(graph1nlls[zero]): zero = n
        #zero = graph1nlls.index(min(graph1nlls))
        print graph1nlls[zero], graph1wcs[zero]
        #graph1nlls[zero] = 11
        graph1nlls = [val-min(graph1nlls) for val in graph1nlls]
        graph2nlls = [val-min(graph2nlls) for val in graph2nlls]
        graph1 = ROOT.TGraph(len(graph1wcs),numpy.asarray(graph1wcs),numpy.asarray(graph1nlls))
        graph2 = ROOT.TGraph(len(graph2wcs),numpy.asarray(graph2wcs),numpy.asarray(graph2nlls))
        del graph1nlls,graph2nlls,graph1wcs,graph2wcs

        # Combine into TMultiGraph
        multigraph = ROOT.TMultiGraph()
        multigraph.Add(graph1)
        multigraph.Add(graph2)
        multigraph.Draw("AP")
        multigraph.GetXaxis().SetLabelSize(0.05)
        multigraph.GetYaxis().SetLabelSize(0.05)
        multigraph.GetXaxis().SetTitleSize(0.05)
        multigraph.GetXaxis().SetTitleOffset(0.8)
        #multigraph.GetXaxis().SetNdivisions(7)

        # Squeeze X down to whatever range captures the float points
        xmin = self.wc_ranges[wc][0]
        xmax = self.wc_ranges[wc][1]
        for idx in range(graph1.GetN()):
            if graph1.GetY()[idx] < ceiling and graph1.GetX()[idx] < xmin:
                xmin = graph1.GetX()[idx]
            if graph1.GetY()[idx] < ceiling and graph1.GetX()[idx] > xmax:
                xmax = graph1.GetX()[idx]
        multigraph.GetXaxis().SetRangeUser(xmin,xmax)
        multigraph.GetYaxis().SetRangeUser(-0.1,ceiling)
        h = ROOT.TH1F("h_overlay", "", 100, xmin, xmax)
        ROOT.gStyle.SetOptStat(0)
        h.GetXaxis().SetLabelSize(0.05)
        h.GetYaxis().SetLabelSize(0.05)
        h.GetXaxis().SetTitleSize(0.05)
        h.GetXaxis().SetTitleOffset(0.8)
        h.GetXaxis().SetRangeUser(xmin,xmax)
        h.GetYaxis().SetRangeUser(-0.1,ceiling)
        h.Draw()
        multigraph.Draw("P")

        #Change markers from invisible dots to nice triangles
        graph1.SetMarkerColor(1)
        graph1.SetMarkerStyle(26)
        graph1.SetMarkerSize(1)

        graph2.SetMarkerColor(2)
        graph2.SetMarkerStyle(32)
        graph2.SetMarkerSize(1)

        #Add 1-sigma and 2-sigma lines. (Vertical lines were too hard, sadly)
        canvas.SetGrid(1)
        p1.SetGrid(1)

        line68 = ROOT.TLine(xmin,1,xmax,1)
        line68.Draw('same')
        line68.SetLineColor(ROOT.kYellow+1)
        line68.SetLineWidth(3)
        line68.SetLineStyle(7)

        line95 = ROOT.TLine(xmin,4,xmax,4)
        line95.Draw('same')
        line95.SetLineColor(ROOT.kCyan-2)
        line95.SetLineWidth(3)
        line95.SetLineStyle(7)

        # Labels
        Title = ROOT.TLatex(0.5, 0.95, "{} 2#DeltaNLL".format(wc))
        Title.SetNDC(1)
        Title.SetTextAlign(20)
        #Title.Draw('same')
        #multigraph.GetXaxis().SetTitle(wc)
        #multigraph.GetXaxis().SetTitle(self.texdic[wc.rstrip('i')])
        XTitle = ROOT.TLatex(0.85, 0.01, self.texdic[wc.rstrip('i')])
        XTitle.SetNDC(1)
        XTitle.SetTextAlign(20)
        XTitle.SetTextFont(42)
        canvas.cd()
        XTitle.Draw('same')
        YTitle = ROOT.TLatex(0.03, 0.85, "2#DeltaNLL")
        YTitle.SetNDC(1)
        YTitle.SetTextAlign(20)
        YTitle.SetTextFont(42)
        YTitle.SetTextAngle(90)
        canvas.cd()
        YTitle.Draw('same')

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.18, 0.96, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.04)
        self.CMS_text.SetTextAlign(30)
        self.CMS_text.Draw('same')
        #self.CMS_extra = ROOT.TLatex(0.37, 0.952, "Supplementary")# Simulation")
        self.CMS_extra = ROOT.TLatex(0.37, 0.91, "Preliminary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.04)
        self.CMS_extra.SetTextAlign(30)
        self.CMS_extra.SetTextFont(52)
        self.arXiv_extra = ROOT.TLatex(0.31, 0.92, self.arXiv)# Simulation")
        self.arXiv_extra.SetNDC(1)
        self.arXiv_extra.SetTextSize(0.04)
        self.arXiv_extra.SetTextAlign(30)
        self.arXiv_extra.SetTextFont(42)
        if not final: self.CMS_extra.Draw('same')
        #if not final: self.arXiv_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.9, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.04)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        # Lgend
        legend = ROOT.TLegend(0.,0.,1,1)
        #legend = ROOT.TLegend(0.1,0.85,0.45,0.945)
        legend.AddEntry(graph1,titles[0],'p')
        legend.AddEntry(graph2,titles[1],'p')
        legend.SetTextSize(0.35)
        legend.SetBorderSize(0)
        #legend.SetTextSize(0.035)
        #legend.SetNColumns(1)
        #legend.Draw('same')

        #Check log option, then save as image
        if log:
            multigraph.SetMinimum(0.1)
            multigraph.SetLogz()
            canvas.Print('Overlay{}1DNLL_log.png'.format(wc),'png')
        else:
            if final: 
                canvas.Print('Overlay{}1DNLL_final.png'.format(wc),'png')
                canvas.Print('Overlay{}1DNLL_final.eps'.format(wc),'eps')
                os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop Overlay{}1DNLL_final.eps'.format(wc))
            else: 
                canvas.Print('Overlay{}1DNLL_prelim.png'.format(wc),'png')
                canvas.Print('Overlay{}1DNLL_prelim.eps'.format(wc),'eps')
                os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop Overlay{}1DNLL_prelim.eps'.format(wc))
        canvas = ROOT.TCanvas('canvas', 'canvas', 400, 100)
        canvas.cd()
        legend.Draw()
        canvas.Print('ext_leg_Overlay1DNLL.png'.format(wc),'png')
        canvas.Print('ext_leg_Overlay1DNLL.eps'.format(wc),'eps')
        os.system('sed -i "s/STIXGeneral-Italic/STIXXGeneral-Italic/g" ext_leg_Overlay1DNLL.eps')
        os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop ext_leg_Overlay1DNLL.eps')

    def OverlayZoomLLPlot1DEFT(self, name1='.test', name2='.test', wc='', log=False):
        if not wc:
            logging.error("No wc specified!")
            return
        if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name1)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name1))
            return
        if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name2)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name2))
            return

        ROOT.gROOT.SetBatch(True)

        canvas = ROOT.TCanvas()

        # Get scan trees
        rootFile1 = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name1))
        limitTree1 = rootFile1.Get('limit')

        rootFile2 = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name2))
        limitTree2 = rootFile2.Get('limit')

        # Get coordinates for TGraphs
        graph1wcs = []
        graph2wcs = []
        graph1nlls = []
        graph2nlls = []
        for entry in range(limitTree1.GetEntries()):
            limitTree1.GetEntry(entry)
            graph1wcs.append(limitTree1.GetLeaf(wc).GetValue(0))
            graph1nlls.append(2*limitTree1.GetLeaf('deltaNLL').GetValue(0))
        for entry in range(limitTree2.GetEntries()):
            limitTree2.GetEntry(entry)
            graph2wcs.append(limitTree2.GetLeaf(wc).GetValue(0))
            graph2nlls.append(2*limitTree2.GetLeaf('deltaNLL').GetValue(0))

        # Rezero the y axis and make the tgraphs
        graph1nlls = [val-min(graph1nlls) for val in graph1nlls]
        graph2nlls = [val-min(graph2nlls) for val in graph2nlls]
        graph1 = ROOT.TGraph(len(graph1wcs),numpy.asarray(graph1wcs),numpy.asarray(graph1nlls))
        graph2 = ROOT.TGraph(len(graph2wcs),numpy.asarray(graph2wcs),numpy.asarray(graph2nlls))
        del graph1nlls,graph2nlls,graph1wcs,graph2wcs

        # Combine into TMultiGraph
        multigraph = ROOT.TMultiGraph()
        multigraph.Add(graph1)
        multigraph.Add(graph2)
        multigraph.Draw("AP")

        # Squeeze X down to 20 pts around 0.
        width = self.wc_ranges[wc][1]-self.wc_ranges[wc][0]
        xmin = -float(width)/50
        xmax = float(width)/50
        ymax = max(graph1.Eval(xmin),graph1.Eval(xmax),graph2.Eval(xmin),graph2.Eval(xmax))
        ymin = -ymax/10
        multigraph.GetXaxis().SetRangeUser(xmin, xmax)
        multigraph.GetYaxis().SetRangeUser(ymin, ymax)

        #Change markers from invisible dots to nice triangles
        graph1.SetMarkerColor(1)
        graph1.SetMarkerStyle(26)
        graph1.SetMarkerSize(1)

        graph2.SetMarkerColor(2)
        graph2.SetMarkerStyle(26)
        graph2.SetMarkerSize(1)

        #Add 1-sigma and 2-sigma lines. (Vertical lines were too hard, sadly)
        canvas.SetGrid(1)

        line68 = ROOT.TLine(xmin,1,xmax,1)
        line68.Draw('same')
        line68.SetLineColor(ROOT.kYellow+1)
        line68.SetLineWidth(3)
        line68.SetLineStyle(7)

        line95 = ROOT.TLine(xmin,4,xmax,4)
        line95.Draw('same')
        line95.SetLineColor(ROOT.kCyan-2)
        line95.SetLineWidth(3)
        line95.SetLineStyle(7)

        # Labels
        Title = ROOT.TLatex(0.5, 0.95, "{} 2#DeltaNLL".format(wc))
        Title.SetNDC(1)
        Title.SetTextAlign(20)
        Title.Draw('same')
        multigraph.GetXaxis().SetTitle(wc)

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.9, 0.93, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.02)
        self.CMS_text.SetTextAlign(30)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.9, 0.90, "Preliminary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.02)
        self.CMS_extra.SetTextAlign(30)
        self.CMS_extra.SetTextFont(52)
        self.CMS_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.9, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.02)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        #Check log option, then save as image
        if log:
            multigraph.SetMinimum(0.1)
            multigraph.SetLogz()
            canvas.Print('OverlayZoom{}1DNLL_log.png'.format(wc),'png')
        else:
            canvas.Print('OverlayZoom{}1DNLL.png'.format(wc),'png')

        rootFile1.Close()
        rootFile2.Close()

    def BatchLLPlot1DEFT(self, basename_lst=['.test'], frozen=False, wcs=[], log=False):
        if not wcs:
            wcs = self.wcs

        ROOT.gROOT.SetBatch(True)

        for wc in wcs:
            basename_lst_with_wc_appended = self.AppendStrToItemsInLst(basename_lst,"."+wc)
            self.LLPlot1DEFT(basename_lst_with_wc_appended, frozen, wc, log)

    def BatchLLPlotNDEFT(self, basename='.test', frozen=False, wcs=[], log=False):
        if not wcs:
            wcs = self.wcs

        ROOT.gROOT.SetBatch(True)

        #wcs.remove('ctG')
        for pair in zip(wcs[::2], wcs[1::2]):
            self.LLPlot2DEFT(basename, wcs=pair, log=log, ceiling=300)

    def BatchOverlayLLPlot1DEFT(self, basename1_lst=['.EFT.SM.Float'], basename2_lst=['.EFT.SM.Freeze'], wcs=[], log=False, final=False, titles=['Others Profiled', 'Others Fixed to SM']):
        if (type(basename1_lst) is not list) or (type(basename2_lst) is not list): raise Exception("Error: Pass the name of the file as a list (even if it's just of length 1)")
        if not wcs:
            wcs = self.wcs

        ROOT.gROOT.SetBatch(True)

        for wc in wcs:
            print(wc)
            basename1_lst_with_wc_appended = self.AppendStrToItemsInLst(basename1_lst,"."+wc)
            basename2_lst_with_wc_appended = self.AppendStrToItemsInLst(basename2_lst,"."+wc)
            self.OverlayLLPlot1DEFT(name1_lst=basename1_lst_with_wc_appended, name2_lst=basename2_lst_with_wc_appended, wc=wc, log=log, final=final, titles=titles)

    def BatchOverlayZoomLLPlot1DEFT(self, basename1='.EFT.SM.Float', basename2='.EFT.SM.Freeze', wcs=[], log=False):
        if not wcs:
            wcs = self.wcs

        ROOT.gROOT.SetBatch(True)

        for wc in wcs:
            self.OverlayZoomLLPlot1DEFT(basename1+'.'+wc, basename2+'.'+wc, wc, log)

    def LLPlot2DEFT(self, name='.test', wcs=[], ceiling=1, log=False, final=False):
        if len(wcs)!=2:
            logging.error("Function 'LLPlot2D' requires exactly two wcs!")
            return
        if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
            return

        ROOT.gROOT.SetBatch(True)

        canvas = ROOT.TCanvas('c','c',800,800)

        # Open file and draw 2D histogram
        # wcs[0] is y-axis variable, wcs[1] is x-axis variable
        rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        limitTree = rootFile.Get('limit')
        hname = '{}{}less{}'.format(wcs[0],wcs[1],ceiling)
        if log:
            hname += "_log"
        minZ = limitTree.GetMinimum('deltaNLL')

        hist = ROOT.TH3F(hname, hname, 100, self.wc_ranges[wcs[1]][0], self.wc_ranges[wcs[1]][1], 100, self.wc_ranges[wcs[0]][0], self.wc_ranges[wcs[0]][1], 100, 0, ceiling)
        limitTree.Project(hname, '2*(deltaNLL-{}):{}:{}'.format(minZ,wcs[0],wcs[1]), '')
        hist = hist.Project3DProfile()
        limitTree.Draw('2*(deltaNLL-{}):{}:{}>>hist(100,{},{},100,{},{})'.format(minZ,wcs[1],wcs[0],self.wc_ranges[wcs[1]][0],self.wc_ranges[wcs[1]][1],self.wc_ranges[wcs[0]][0],self.wc_ranges[wcs[0]][1]), '2*deltaNLL<{}'.format(ceiling), 'prof colz')
        hist.Draw('colz')
        hist.SetTitle(';{};{}'.format(wcs[0],wcs[1]))

        # Change plot formats
        if log:
            canvas.SetLogz()
        hist.GetYaxis().SetTitle(self.texdic[wcs[1].rstrip('i')])
        hist.GetXaxis().SetTitle(self.texdic[wcs[0].rstrip('i')])
        hist.SetTitle('')#"2*deltaNLL < {}".format(ceiling))
        hist.SetStats(0)

        ROOT.gStyle.SetOptStat(0)

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.1, 0.945, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.04)
        self.CMS_text.SetTextAlign(13)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.2, 0.945, "Preliminary")# Simulation")
        #self.CMS_extra = ROOT.TLatex(0.2, 0.945, "Supplementary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.04)
        self.CMS_extra.SetTextAlign(13)
        self.CMS_extra.SetTextFont(52)
        if not final: self.CMS_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.9, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.04)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        # Save plot
        canvas.Print(hname+".png",'png')
        canvas.Print(hname+".eps",'eps')
        os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop {}.eps {}.pdf'.format(hname,hname))

        # Save to root file
        # Log settings don't save to the histogram, so redundant to save those
        if not log:
            outfile = ROOT.TFile(self.histosFileName,'UPDATE')
            hist.Write()
            outfile.Close()

    def ContourPlotEFT(self, name='.test', wcs=[], final=False):
        if len(wcs)!=2:
            logging.error("Function 'ContourPlot' requires exactly two wcs!")
            return
        if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
            return

        best2DeltaNLL = 1000000
        ROOT.gROOT.SetBatch(True)
        canvas = ROOT.TCanvas('c','c',800,800)

        # Get Grid scan and copy to h_contour
        # wcs[0] is y-axis variable, wcs[1] is x-axis variable
        gridFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        gridTree = gridFile.Get('limit')
        minZ = gridTree.GetMinimum('deltaNLL')
        gridTree.Draw('2*(deltaNLL-{}):{}:{}>>grid(100,{},{},100,{},{})'.format(minZ,wcs[1],wcs[0],self.wc_ranges[wcs[0]][0],self.wc_ranges[wcs[0]][1],self.wc_ranges[wcs[1]][0],self.wc_ranges[wcs[1]][1]), '', 'prof colz')
        #canvas.Print('{}{}2D.png'.format(wcs[0],wcs[1]),'png')
        original = ROOT.TProfile2D(canvas.GetPrimitive('grid'))
        h_contour = ROOT.TProfile2D('h_contour','h_contour',100,self.wc_ranges[wcs[1]][0],self.wc_ranges[wcs[1]][1],100,self.wc_ranges[wcs[0]][0],self.wc_ranges[wcs[0]][1])
        h_contour = original.Clone('h_conotour')
        #original.Copy(h_contour)

        # Adjust scale so that the best bin has content 0
        best2DeltaNLL = original.GetMinimum()
        for xbin in range(original.GetNbinsX()):
            xcoord = original.GetXaxis().GetBinCenter(xbin)
            for ybin in range(original.GetNbinsY()):
                ycoord = original.GetYaxis().GetBinCenter(ybin)
                if original.GetBinContent(1+xbin,1+ybin)==0:
                    h_contour.Fill(xcoord,ycoord,1000)
                if original.GetBinContent(1+xbin,1+ybin)!=0:
                    h_contour.Fill(xcoord,ycoord,original.GetBinContent(1+xbin,1+ybin)-best2DeltaNLL)
                #h_contour.SetBinContent(1+xbin,1+ybin,original.GetBinContent(1+xbin,1+ybin)-best2DeltaNLL)

        # Exclude data outside of the contours
        #h_contour.SetMaximum(11.83)
        #h_contour.SetContour(200)
        #h_contour.GetZaxis().SetRangeUser(0,21);
        h_contour.GetXaxis().SetRange(1,h_contour.GetNbinsX()-3)
        h_contour.GetYaxis().SetRange(1,h_contour.GetNbinsY()-3)

        # Set Contours
        c68 = self.ContourHelper.GetContour(h_contour,2.30)
        c95 = self.ContourHelper.GetContour(h_contour,6.18)
        c997 = self.ContourHelper.GetContour(h_contour,11.83)
        c681D = self.ContourHelper.GetContour(h_contour,1.00)
        c951D = self.ContourHelper.GetContour(h_contour,4.00)
        c9971D = self.ContourHelper.GetContour(h_contour,9.00)
        self.ContourHelper.styleMultiGraph(c68,ROOT.kYellow+1,4,1)
        self.ContourHelper.styleMultiGraph(c95,ROOT.kCyan-2,4,6)
        self.ContourHelper.styleMultiGraph(c997,ROOT.kBlue,4,3)
        #place holders for the legend, since TLine is weird
        hc68 = ROOT.TH1F('c68', 'c68', 1, 0, 1)
        hc95 = ROOT.TH1F('c95', 'c68', 1, 0, 1)
        hc997 = ROOT.TH1F('c997', 'c68', 1, 0, 1)
        hc68.SetLineColor(ROOT.kYellow+1)
        hc95.SetLineColor(ROOT.kCyan-2)
        hc997.SetLineColor(ROOT.kBlue)
        hc68.SetLineStyle(1)
        hc95.SetLineStyle(6)
        hc997.SetLineStyle(3)
        hc68.SetLineWidth(5)
        hc95.SetLineWidth(5)
        hc997.SetLineWidth(5)
        self.ContourHelper.styleMultiGraph(c681D,ROOT.kYellow+1,1,3)
        self.ContourHelper.styleMultiGraph(c951D,ROOT.kCyan-2,1,3)
        self.ContourHelper.styleMultiGraph(c9971D,ROOT.kGreen-2,1,3)

        # Marker for SM point
        marker_1 = ROOT.TMarker()
        marker_1.SetMarkerSize(3.0)
        marker_1.SetMarkerColor(97)
        marker_1.SetMarkerStyle(33)
        marker_2 = ROOT.TMarker()
        marker_2.SetMarkerSize(1.8)
        marker_2.SetMarkerColor(89)
        marker_2.SetMarkerStyle(33)
        hSM = ROOT.TH1F('SM', 'SM', 1, 0, 1)
        hSM.SetMarkerStyle(33)
        hSM.SetMarkerColor(97)
        hSM.SetMarkerSize(2)
 
        # Change format of plot
        h_contour.SetStats(0)
        #h_contour.SetTitle("Significance Contours")
        h_contour.SetTitle("")
        h_contour.GetYaxis().SetTitle(self.texdic[wcs[1].rstrip('i')])
        h_contour.GetXaxis().SetTitle(self.texdic[wcs[0].rstrip('i')])

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.1, 0.945, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.04)
        self.CMS_text.SetTextAlign(13)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.2, 0.945, "Preliminary")# Simulation")
        #self.CMS_extra = ROOT.TLatex(0.2, 0.945, "Supplementary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.04)
        self.CMS_extra.SetTextAlign(13)
        self.CMS_extra.SetTextFont(52)
        if not final: self.CMS_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.9, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.04)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        # Draw and save plot
        h_contour.GetXaxis().SetTitleOffset(1.1)
        h_contour.GetXaxis().SetTitleSize(0.04)
        h_contour.GetXaxis().SetLabelSize(0.04)
        h_contour.GetYaxis().SetTitleOffset(1.1)
        h_contour.GetYaxis().SetTitleSize(0.04)
        h_contour.GetXaxis().SetLabelSize(0.04)
        #h_contour.GetYaxis().SetNdivisions(7)
        h_contour.Draw('AXIS')
        #canvas.Print('contour.png','png')
        c68.Draw('L SAME')
        c95.Draw('L SAME')
        c997.Draw('L SAME')
        #C681D.Draw('L SAME')
        #C951D.Draw('L SAME')
        #C9971D.Draw('L SAME')
        marker_1.DrawMarker(0,0)
        marker_2.DrawMarker(0,0)

        #c = [2.3, 6.18, 11.83]
        #original.SetContourLevel(0, c[0])
        #original.SetContourLevel(1, c[1])
        #original.SetContourLevel(2, c[2])
        #import numpy
        #original.SetContour(3, numpy.array(c))
        #original.SetMaximum(3)
        #ROOT.gStyle.SetOptStat(0)
        #original.Draw("cont1z")
        #marker_1.DrawMarker(0,0)
        #marker_2.DrawMarker(0,0)


        legend = ROOT.TLegend(0.12,0.7,0.3,0.895)
        # Bob Cousins stated 2+D should always be percentages, since e.g. "1 sigma" is not actually 68 for a 2D contour
        # https://hypernews.cern.ch/HyperNews/CMS/get/statistics/764/1.html
        legend.AddEntry(hc68,"68.27%",'l')
        legend.AddEntry(hc95,"95.45%",'l')
        legend.AddEntry(hc997,"99.73%",'l')
        legend.AddEntry(hSM,"SM value",'p')
        legend.SetTextSize(0.035)
        #legend.SetTextSize(0.025)
        #legend.SetNColumns(4)
        legend.Draw('same')
        self.CMS_text.Draw('same')
        if not final: self.CMS_extra.Draw('same')
        self.Lumi_text.Draw('same')
        canvas.SetGrid()
        if final: canvas.Print('{}{}contour_final.png'.format(wcs[0],wcs[1]),'png')
        else:
            canvas.Print('{}{}contour.png'.format(wcs[0],wcs[1]),'png')
            canvas.Print('{}{}contour.eps'.format(wcs[0],wcs[1]),'eps')
            os.system('sed -i "s/STIXGeneral-Italic/STIXXGeneral-Italic/g" {}{}contour.eps'.format(wcs[0],wcs[1],wcs[0],wcs[1]))
            os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop {}{}contour.eps {}{}contour.pdf'.format(wcs[0],wcs[1],wcs[0],wcs[1]))
        if final: 
            #canvas.Print('{}{}contour_final.pdf'.format(wcs[0],wcs[1]),'pdf')
            canvas.Print('{}{}contour_final.png'.format(wcs[0],wcs[1]),'png')
            canvas.Print('{}{}contour_final.eps'.format(wcs[0],wcs[1]),'eps')
            #convert EPS to PDF to preserve \ell
            os.system('sed -i "s/STIXGeneral-Italic/STIXXGeneral-Italic/g" {}{}contour_final.eps'.format(wcs[0],wcs[1],wcs[0],wcs[1]))
            os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop {}{}contour_final.eps {}{}contour_final.pdf'.format(wcs[0],wcs[1],wcs[0],wcs[1]))
        else: 
            #canvas.Print('{}{}contour.pdf'.format(wcs[0],wcs[1]),'pdf')
            canvas.Print('{}{}contour_prelim.png'.format(wcs[0],wcs[1]),'png')
            canvas.Print('{}{}contour_prelim.eps'.format(wcs[0],wcs[1]),'eps')
            os.system('sed -i "s/STIXGeneral-Italic/STIXXGeneral-Italic/g" {}{}contour_prelim.eps'.format(wcs[0],wcs[1],wcs[0],wcs[1]))
            os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop {}{}contour_prelim.eps {}{}contour_prelim.pdf'.format(wcs[0],wcs[1],wcs[0],wcs[1]))

        # Save contour to histogram file
        outfile = ROOT.TFile(self.histosFileName,'UPDATE')
        h_contour.Write()
        outfile.Close()

        ROOT.gStyle.SetPalette(57)
        
    def LLPlot1DSM(self, name='.test', param='', log=False):
        if not param:
            logging.error("No parameter specified!")
            return
        if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
            return

        ROOT.gROOT.SetBatch(True)
        canvas = ROOT.TCanvas('c','c',800,800)

        # Get scan tree
        rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        limitTree = rootFile.Get('limit')

        # Get coordinates for TGraph
        graphparamvals = []
        graphnlls = []
        for entry in range(limitTree.GetEntries()):
            limitTree.GetEntry(entry)
            graphparamvals.append(limitTree.GetLeaf(param).GetValue(0))
            graphnlls.append(2*limitTree.GetLeaf('deltaNLL').GetValue(0))

        # Rezero the y axis and make the tgraphs
        graphnlls = [val-min(graphnlls) for val in graphnlls]
        graph = ROOT.TGraph(len(graphparamvals),numpy.asarray(graphparamvals),numpy.asarray(graphnlls))
        graph.Draw("AP")
        del graphnlls,graphparamvals

        # Squeeze X down to whatever range captures the float points
        xmin = limitTree.GetMinimum(param)
        xmax = limitTree.GetMaximum(param)
        #for idx in range(graph.GetN()):
        #    if graph.GetY()[idx] < 10 and graph.GetX()[idx] < xmin:
        #        xmin = graph.GetX()[idx]
        #    if graph.GetY()[idx] < 10 and graph.GetX()[idx] > xmax:
        #        xmax = graph.GetX()[idx]
        graph.GetXaxis().SetRangeUser(xmin,xmax)
        graph.GetYaxis().SetRangeUser(-0.1,10)

        #Change markers from invisible dots to nice triangles
        graph.SetTitle("")
        graph.SetMarkerStyle(26)
        graph.SetMarkerSize(1)
        graph.SetMinimum(-0.1)

        #Add 1-sigma and 2-sigma lines. (Vertical lines were too hard, sadly)
        canvas.SetGrid(1)

        line68 = ROOT.TLine(xmin,1,xmax,1)
        line68.Draw('same')
        line68.SetLineColor(ROOT.kYellow+1)
        line68.SetLineWidth(3)
        line68.SetLineStyle(7)

        line95 = ROOT.TLine(xmin,4,xmax,4)
        line95.Draw('same')
        line95.SetLineColor(ROOT.kCyan-2)
        line95.SetLineWidth(3)
        line95.SetLineStyle(7)

        # Labels
        Title = ROOT.TLatex(0.5, 0.95, "{} 2#DeltaNLL".format(param))
        Title.SetNDC(1)
        Title.SetTextAlign(20)
        Title.Draw('same')
        graph.GetXaxis().SetTitle(param)

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.665, 0.93, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.02)
        self.CMS_text.SetTextAlign(30)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.9, 0.90, "Preliminary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.02)
        self.CMS_extra.SetTextAlign(30)
        self.CMS_extra.SetTextFont(52)
        self.CMS_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.7, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.02)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        #Check log option, then save as image
        if log:
            graph.SetMinimum(0.1)
            graph.SetLogz()
            canvas.Print('{}{}_1DNLL_log.png'.format(param,name),'png')
        else:
            canvas.Print('{}{}_1DNLL.png'.format(param,name),'png')

        rootFile.Close()
        
    def BatchLLPlot1DSM(self, basename='.test', frozen=False, scan_params=[], log=False):
        if not scan_params:
            scan_params = self.SMMus

        ROOT.gROOT.SetBatch(True)

        for param in scan_params:
            self.LLPlot1DSM(basename+'.'+param, param, log)

    def LLPlot2DSM(self, name='.test', params=[], ceiling=1, log=False):
        if len(params)!=2:
            logging.error("Function 'LLPlot2D' requires exactly two parameters!")
            return
        if not os.path.exists('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name)):
            logging.error("File higgsCombine{}.MultiDimFit.root does not exist!".format(name))
            return

        ROOT.gROOT.SetBatch(True)

        canvas = ROOT.TCanvas('c','c',800,800)

        # Open file and draw 2D histogram
        rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        limitTree = rootFile.Get('limit')
        hname = '{}{}_{}_less{}'.format(params[0],params[1],name,ceiling)
        if log:
            hname += "_log"
        minZ = limitTree.GetMinimum('deltaNLL')
        ymin = limitTree.GetMinimum(params[0])
        ymax = limitTree.GetMaximum(params[0])
        xmin = limitTree.GetMinimum(params[1])
        xmax = limitTree.GetMaximum(params[1])

        #limitTree.Draw('2*(deltaNLL-{}):{}:{}>>{}(200,0,15,200,0,15)'.format(minZ,params[0],params[1],hname), '2*deltaNLL<{}'.format(ceiling), 'prof colz')
        limitTree.Draw('2*(deltaNLL-{}):{}:{}>>{}(200,{},{},200,{},{})'.format(minZ,params[0],params[1],hname,xmin,xmax,ymin,ymax), '2*deltaNLL<{}'.format(ceiling), 'prof colz')        

        hist = canvas.GetPrimitive(hname)

        # Draw best fit point from grid scan
        #limit.Draw(params[0]+":"+params[1],'quantileExpected==-1','p same') # Best fit point from grid scan
        #best_fit = canvas.FindObject('Graph')
        #best_fit.SetMarkerSize(1)
        #best_fit.SetMarkerStyle(34)
        #best_fit.Draw("p same")

        # Change plot formats
        #hist.GetXaxis().SetRangeUser(0,5)
        #hist.GetYaxis().SetRangeUser(0,3)
        #hist.GetXaxis().SetRangeUser(-5,5)
        #hist.GetYaxis().SetRangeUser(-5,5)
        if log:
            canvas.SetLogz()
        hist.GetYaxis().SetTitle(params[0])
        hist.GetXaxis().SetTitle(params[1])
        hist.SetTitle("2*deltaNLL < {}".format(ceiling))
        hist.SetStats(0)

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.665, 0.93, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.02)
        self.CMS_text.SetTextAlign(30)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.9, 0.90, "Preliminary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.02)
        self.CMS_extra.SetTextAlign(30)
        self.CMS_extra.SetTextFont(52)
        self.CMS_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.7, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.02)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        # Save plot
        canvas.Print(hname+".png",'png')

        # Save to root file
        # Log settings don't save to the histogram, so redundant to save those
        if not log:
            outfile = ROOT.TFile(self.histosFileName,'UPDATE')
            hist.Write()
            outfile.Close()

    def ContourPlotSM(self, name='.test', params=[]):
        if len(params)!=2:
            logging.error("Function 'ContourPlot' requires exactly two parameters!")
            return
            
        best2DeltaNLL = 1000000
        ROOT.gROOT.SetBatch(True)
        canvas = ROOT.TCanvas('c','c',800,800)

        # Get Grid scan and copy to h_contour
        # params[0] is y-axis variable, params[1] is x-axis variable
        gridFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        gridTree = gridFile.Get('limit')
        minZ = gridTree.GetMinimum('deltaNLL')
        #gridTree.Draw('2*(deltaNLL-{}):{}:{}>>grid(200,0,15,200,0,15)'.format(minZ,params[0],params[1]), '', 'prof colz')
        gridTree.Draw('2*(deltaNLL-{}):{}:{}>>grid(100,{},{},100,{},{})'.format(minZ,params[0],params[1],self.sm_ranges[params[1]][0],self.sm_ranges[params[1]][1],self.sm_ranges[params[0]][0],self.sm_ranges[params[0]][1]), '', 'prof colz')
        #gridTree.Draw('2*deltaNLL:{}:{}>>grid(50,0,30,50,0,30)'.format(params[0],params[1]), '', 'prof colz')
        original = ROOT.TProfile2D(canvas.GetPrimitive('grid'))
        h_contour = ROOT.TProfile2D('h_contour','h_contour',100,self.sm_ranges[params[1]][0],self.sm_ranges[params[1]][1],100,self.sm_ranges[params[0]][0],self.sm_ranges[params[0]][1])

        # Adjust scale so that the best bin has content 0
        best2DeltaNLL = original.GetMinimum()
        for xbin in range(original.GetNbinsX()):
            xcoord = original.GetXaxis().GetBinCenter(xbin)
            for ybin in range(original.GetNbinsY()):
                ycoord = original.GetYaxis().GetBinCenter(ybin)
                if original.GetBinContent(1+xbin,1+ybin)==0:
                    h_contour.Fill(xcoord,ycoord,1000)
                if original.GetBinContent(1+xbin,1+ybin)!=0:
                    h_contour.Fill(xcoord,ycoord,original.GetBinContent(1+xbin,1+ybin)-best2DeltaNLL)
                #h_contour.SetBinContent(1+xbin,1+ybin,original.GetBinContent(1+xbin,1+ybin)-best2DeltaNLL)

        # Exclude data outside of the contours
        #h_contour.SetMaximum(11.83)
        #h_contour.SetContour(200)
        #h_contour.GetZaxis().SetRangeUser(0,21);
        #h_contour.GetXaxis().SetRangeUser(0,6); # ttH
        #h_contour.GetXaxis().SetRangeUser(0,4); # tllq
        #h_contour.GetYaxis().SetRangeUser(0,3); # tll, tllnu
        #h_contour.GetXaxis().SetRange(1,h_contour.GetNbinsX()-3)
        #h_contour.GetYaxis().SetRange(1,h_contour.GetNbinsY()-3)

        # Set Contours
        c68 = self.ContourHelper.GetContour(h_contour,2.30)
        c95 = self.ContourHelper.GetContour(h_contour,6.18)
        c997 = self.ContourHelper.GetContour(h_contour,11.83)
        self.ContourHelper.styleMultiGraph(c68,ROOT.kYellow+1,3,1)
        self.ContourHelper.styleMultiGraph(c95,ROOT.kCyan-2,3,1)
        self.ContourHelper.styleMultiGraph(c997,ROOT.kGreen-2,3,1)

        # Marker for SM point
        marker_1 = ROOT.TMarker()
        marker_1.SetMarkerSize(2.0)
        marker_1.SetMarkerColor(97)
        marker_1.SetMarkerStyle(33)
        marker_2 = ROOT.TMarker()
        marker_2.SetMarkerSize(1.2)
        marker_2.SetMarkerColor(89)
        marker_2.SetMarkerStyle(33)
        
        # Misc Markers -- use as needed
        # Simultaneous Fit Marker -- use as needed
        #simulFit = ROOT.TMarker(0.96,1.11,20) # tllq,ttll
        simulFit = ROOT.TMarker(2.58,0.70,20) # ttH,ttlnu
        # Central Fit Marker -- use as needed
        centralFit = ROOT.TGraphAsymmErrors(1)
        #centralFit.SetPoint(0,0.58,1.24) # tllq,ttll
        #centralFit.SetPointError(0,0.54,0.61,0.24,0.31) # tllq,ttll
        centralFit.SetPoint(0,2.56,0.84) # ttH,ttlnu
        centralFit.SetPointError(0,0.72,0.87,0.36,0.43) # ttH,ttlnu
        centralFit.SetMarkerSize(2)
        centralFit.SetMarkerStyle(6)
        centralFit.SetLineColor(2)
        # Dedicated Fit Marker -- use as needed
        dedicatedFit = ROOT.TGraphAsymmErrors(1)
        #dedicatedFit.SetPoint(0,1.01,1.28) # tZq,ttZ
        #dedicatedFit.SetPointError(0,0.21,0.23,0.13,0.14) # tZq,ttZ
        dedicatedFit.SetPoint(0,0.75,1.23) # ttH,ttW
        dedicatedFit.SetPointError(0,0.43,0.46,0.28,0.31) # ttH,ttW
        dedicatedFit.SetMarkerSize(2)
        dedicatedFit.SetMarkerStyle(6)
        dedicatedFit.SetLineColor(8)

        # Change format of plot
        h_contour.SetStats(0)
        h_contour.SetTitle("Significance Contours")
        h_contour.GetYaxis().SetTitle(params[0])
        h_contour.GetXaxis().SetTitle(params[1])

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.9, 0.93, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.02)
        self.CMS_text.SetTextAlign(30)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.9, 0.90, "Preliminary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.02)
        self.CMS_extra.SetTextAlign(30)
        self.CMS_extra.SetTextFont(52)
        self.CMS_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.9, 0.91, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.02)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        # Draw and save plot
        h_contour.Draw('AXIS')
        c68.Draw('L SAME')
        c95.Draw('L SAME')
        c997.Draw('L SAME')
        #marker_1.DrawMarker(1,1)
        #marker_2.DrawMarker(1,1)
        simulFit.Draw('same')
        centralFit.Draw('same')
        dedicatedFit.Draw('same')

        self.CMS_text.Draw('same')
        if not final: self.CMS_extra.Draw('same')
        self.Lumi_text.Draw('same')
        if final: canvas.Print('{}{}contour_final.png'.format(params[0],params[1]),'png')
        else: canvas.Print('{}{}contour.png'.format(params[0],params[1]),'png')

        # Save contour to histogram file
        outfile = ROOT.TFile(self.histosFileName,'UPDATE')
        h_contour.Write()
        outfile.Close()

        ROOT.gStyle.SetPalette(57)

    def CorrelationMatrix(self, name='', nuisances=False, SMfit=True, freeze=False):

        ROOT.gROOT.SetBatch(True)
        canvas = ROOT.TCanvas()

        # Get rooFit object
        rooFitFile = ROOT.TFile.Open('../fit_files/multidimfit{}.root'.format(name))
        rooFit = rooFitFile.Get('fit_mdf')

        # Get correlation matrix
        rooFit.correlationHist().Draw('colz')
        matrix = canvas.GetPrimitive('correlation_matrix')

        # Decide whether or not to keep the nuisance parameters in
        # If not, the number of bins (parameters) varies on whether the scan froze the others
        if nuisances:
            matrix.SetName("corrMatrix")
        else:
            if SMfit:
                SMmu = ['mu_ttH','mu_ttlnu','mu_ttll','mu_tllq']
                muBinsX, muBinsY = [], []
                for idx,label in enumerate(matrix.GetXaxis().GetLabels()):
                    if label in SMmu: muBinsX.append(1+idx)
                for idy,label in enumerate(matrix.GetYaxis().GetLabels()):
                    if label in SMmu: muBinsY.append(1+idy)
                newmatrix = ROOT.TH2D("Correlation Matrix","Correlation Matrix",4,0,4,4,0,4)
                for idx,binx in enumerate(muBinsX):
                    for idy,biny in enumerate(muBinsY):
                        newmatrix.SetBinContent(1+idx,4-idy,matrix.GetBinContent(binx,matrix.GetNbinsY()-biny+1))
                    newmatrix.GetXaxis().SetBinLabel(1+idx,matrix.GetXaxis().GetBinLabel(binx))
                for idy,biny in enumerate(muBinsY):
                    newmatrix.GetYaxis().SetBinLabel(4-idy,matrix.GetYaxis().GetBinLabel(matrix.GetNbinsY()-biny+1))

                # Change format of plot
                newmatrix.SetMaximum(1)
                newmatrix.SetMinimum(-1.)
                newmatrix.SetStats(0)
                newmatrix.SetName("corrMatrixSM")
                newmatrix.SetTitle("Correlation Matrix")

                canvas.Clear()
                newmatrix.Draw('colz')
                ROOT.gStyle.SetPaintTextFormat('.2f')

                # Save the plot
                canvas.Print(newmatrix.GetName()+'.png','png')
                newmatrix.Draw('same text')
                canvas.Print(newmatrix.GetName()+'text.png','png')

                # Save the plot to the histogram file
                outfile = ROOT.TFile(self.histosFileName,'UPDATE')
                newmatrix.Write()
                outfile.Close()
                    
            else:
                matrix.SetName("corrMatrix_noNuisances")
                nbins = matrix.GetNbinsX()
                if freeze:
                    matrix.GetYaxis().SetRange(1,2)
                    matrix.GetXaxis().SetRange(nbins-1,nbins)
                else:
                    nwcs = len(self.wcs)
                    matrix.GetYaxis().SetRange(1,nwcs)
                    matrix.GetXaxis().SetRange(nbins-(nwcs-1),nbins)
                    matrix.GetXaxis().LabelsOption("v")
                    #matrix.GetYaxis().SetRangeUser(12,12+nwcs)
                    #matrix.GetXaxis().SetRangeUser(52,52+nwcs)

                # Change format of plot
                matrix.SetStats(0)
                matrix.SetTitle("Correlation Matrix")

                # Save the plot
                canvas.Print(matrix.GetName()+'.png','png')
                canvas.Print(matrix.GetName()+'.eps','eps')
                os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop {}.eps {}.pdf'.format(matrix.GetName(), matrix.GetName()))

                # Save the plot to the histogram file
                outfile = ROOT.TFile(self.histosFileName,'UPDATE')
                matrix.Write()
                outfile.Close()

    def grid2DWC(self, name='', wc='', fits=[]):

        ROOT.gROOT.SetBatch(True)
        canvas = ROOT.TCanvas()

        # Get limit tree
        fit_file = ROOT.TFile.Open('../fit_files/higgsCombine{}.{}.MultiDimFit.root'.format(name,wc))
        limit_tree = fit_file.Get('limit')

        def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
            return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

        # Fined event with minimum NLL
        min_val = 0
        wc_values = []
        for entry in range(limit_tree.GetEntries()):
            limit_tree.GetEntry(entry)
            #min_values.append((entry,2*limit_tree.GetLeaf('deltaNLL').GetValue(0)))
            if limit_tree.GetLeaf(wc).GetValue(0) == fits[wc]: min_val = entry

        # Load other 15 WCs in the minimum entry
        best_vals = []
        for w in self.wcs:
            limit_tree.GetEntry(min_val)
            if w == wc:
                best_vals.append([w, str(limit_tree.GetLeaf(w).GetValue(0))])
            else:
                best_vals.append([w, str(limit_tree.GetLeaf('trackedParam_' + w).GetValue(0))])

        # Close files
        fit_file.Close()
        return best_vals

    def batchGrid2DWC(self, name=''):
        best = []

        fits_float = self.getIntervalFits(basename=name)
        fits = {lst[0] : lst[1] for lst in fits_float}

        for wc in self.wcs:
            best.append(self.grid2DWC(name, wc, fits))

        j=0
        for i in range(0, len(self.wcs)):
            if i ==0: print '  '.join(self.wcs)
            lst = [str(round(float(w[1]), 3)) for w in best[i]]
            print best[i][j][0], ' '.join(lst)
            j = j + 1

    def Batch2DPlotsEFT(self, gridScanName='.EFT.SM.Float.gridScan.ctZctW', wcs=['ctZ','ctW'], final=False):
        ROOT.gROOT.SetBatch(True)
        print gridScanName
        self.ResetHistoFile(gridScanName)

        #self.LLPlot2DEFT(gridScanName,wcs,1,False)
        self.LLPlot2DEFT(gridScanName,wcs,10,False)
        self.LLPlot2DEFT(gridScanName,wcs,30,False)
        self.LLPlot2DEFT(gridScanName,wcs,100000,False)
        # Log Plots
        #self.LLPlot2DEFT(gridScanName,wcs,1,True)
        #self.LLPlot2DEFT(gridScanName,wcs,10,True)
        #self.LLPlot2DEFT(gridScanName,wcs,100,True)

        #self.CorrelationMatrix(postScanName,False,False,freeze)
        #self.CorrelationMatrix(postScanName,True,False,freeze)

        self.ContourPlotEFT(gridScanName,wcs,final)

    def BatchBatch2DPlotsEFT(self, basenamegrid='.EFT.Float.gridScan.Jan01', allpairs=False, final=False, wcs=[]):
        ROOT.gROOT.SetBatch(True)
        
        wcs_pairs = self.wcs_pairs
        if allpairs:
            wcs_pairs = itertools.combinations(self.wcs,2)
        else:
            wcs_pairs = [('ctW','ctG'),('ctZ','ctG'),('ctp','ctG'),('cpQM','ctG'),('cbW','ctG'),('cpQ3','ctG'),('cptb','ctG'),('cpt','ctG'),('cQl3i','ctG'),('cQlMi','ctG'),('cQei','ctG'),('ctli','ctG'),('ctei','ctG'),('ctlSi','ctG'),('ctlTi','ctG')]
            #pairs from AN
            wcs_pairs = [('cQlMi','cQei'),('cpQ3','cbW'),('cptb','cQl3i'),('ctG','cpQM'),('ctZ','ctW'),('ctei','ctlTi'),('ctlSi','ctli'),('ctp','cpt')]
            wcs_pairs = [('ctW','ctZ'),('ctG','ctZ'),('ctp','ctZ'),('cpQM','ctZ'),('cbW','ctZ'),('cpQ3','ctZ'),('cptb','ctZ'),('cpt','ctZ'),('cQl3i','ctZ'),('cQlMi','ctZ'),('cQei','ctZ'),('ctli','ctZ'),('ctei','ctZ'),('ctlSi','ctZ'),('ctlTi','ctZ')]
            wcs_pairs = [('ctp','cpt'), ('ctp','cQq11'), ('ctp','ctq1'), ('ctp','cQq81'), ('ctp','ctq8')]
            wcs_pairs = [('cQei',w) for w in self.wcs if w is not 'cQei']
            wcs_pairs = [('cQq83',w) for w in self.wcs if w is not 'cQq83']
            wcs_pairs = [('cQlMi',w) for w in self.wcs if w is not 'cQlMi']
	    wcs_pairs = [('cQei','ctZ'), ('cQl3i','ctZ'), ('cpQM','ctZ'), ('cptb','ctZ'), ('cpt','ctZ'), ('ctei','ctZ'), ('ctlSi','ctZ'), ('ctli','ctZ')]
            # Pairs from `ptz-lj0pt_fullR2_anatest10v01_withSys.root` where abs(correlation) > 0.4
            wcs_pairs = [('cpt', 'cpQM'), ('ctlSi', 'ctlTi'), ('cQlMi', 'ctei'), ('cbW', 'cpQ3'), ('cQq81', 'cbW'), ('cbW', 'cptb'), ('cptb', 'cpQ3'), ('cQt1', 'ctt1'), ('ctp', 'ctG'), ('cQq81', 'cpQ3')]
            wcs_pairs = [('ctW','ctZ'),('ctG','ctZ'),('ctp','ctZ'),('cpQM','ctZ'),('cbW','ctZ'),('cpQ3','ctZ'),('cptb','ctZ'),('cpt','ctZ'),('cQl3i','ctZ'),('cQlMi','ctZ'),('cQei','ctZ'),('ctli','ctZ'),('ctei','ctZ'),('ctlSi','ctZ'),('ctlTi','ctZ')]
            if len(wcs) > 0:
                wcs_pairs = []
                if isinstance(wcs, str): wcs = [wcs]
                for wc in wcs:
                    if isinstance(wc, tuple): continue
                    wcs_pairs = wcs_pairs + [(wc, other_wc) for other_wc in self.wcs if wc != other_wc]

        for pair in wcs_pairs:
            # pair[0] is y-axis variable, pair[1] is x-axis variable
            #self.Batch2DPlots('{}.{}{}'.format(histosFileName,pair[0],pair[1]), '{}.{}{}'.format(basenamegrid,pair[0],pair[1]), '{}.{}{}'.format(basenamefit,pair[0],pair[1]), operators=pair, freeze=freeze)
            self.Batch2DPlotsEFT('{}.{}{}'.format(basenamegrid,pair[0],pair[1]), wcs=pair, final=final)

            if not os.path.isdir('Histos{}'.format(basenamegrid)):
                sp.call(['mkdir', 'Histos{}'.format(basenamegrid)])
                print 'Created directory Histos{}'.format(basenamegrid)
            sp.call(['mv', 'Histos{}.{}{}.root'.format(basenamegrid,pair[0],pair[1]), 'Histos{}/'.format(basenamegrid)])

            for filename in os.listdir('.'):
                if filename.endswith('contour.png') or filename.endswith('contour_final.png') or ('less' in filename and filename.endswith('.png')):            
                    sp.call(['mv', filename, 'Histos{}/'.format(basenamegrid)])
                if filename.endswith('contour.pdf') or filename.endswith('contour_final.pdf') or ('less' in filename and filename.endswith('.pdf')):            
                    sp.call(['mv', filename, 'Histos{}/'.format(basenamegrid)])
                if filename.endswith('contour.eps') or filename.endswith('contour_final.eps') or ('less' in filename and filename.endswith('.eps')) or filename.endswith('contour_prelim.eps'):            
                    sp.call(['mv', filename, 'Histos{}/'.format(basenamegrid)])

    def getIntervalFits(self,**kwargs):
        basename    = kwargs.pop('basename','.EFT.SM.Float')
        params      = kwargs.pop('params',[])
        siginterval = kwargs.pop('siginterval',2)
        dir_path    = kwargs.pop('dir_path','../fit_files')
        postfix     = kwargs.pop('postfix','')
        ### Return a table of parameters, their best fits, and their uncertainties ###
        ### Use 1D scans instead of regular MultiDimFit ###
        if not params:
            params = self.wcs
            

        ROOT.gROOT.SetBatch(True)

        fit_array = [] # List of [WC, WC value of minimum, [2sig lowedges], [2sig highedges]]

        for param in params:

            # Get scan TTree
            logging.debug("Obtaining result of scan: higgsCombine{}.{}.MultiDimFit{}.root".format(basename,param,postfix))
            fit_file = ROOT.TFile.Open('{}/higgsCombine{}.{}.MultiDimFit{}.root'.format(dir_path,basename,param,postfix))
            # This is mostly used to compare TOP-19-001 to Run II, it will skip the 10 WCs not in TOP-19-001 only and set them to +/- 999
            try:
                limit_tree = fit_file.Get('limit')
            except:
                fit_array.append([param,0,[-999 ],[999]])
                continue

            # Extract points
            wc_values = []
            nll_values = []
            for entry in range(limit_tree.GetEntries()):
                limit_tree.GetEntry(entry)
                wc_values.append(limit_tree.GetLeaf(param).GetValue(0))
                nll_values.append(2*limit_tree.GetLeaf('deltaNLL').GetValue(0))

            # Rezero deltanll values
            bestNLL = min(nll_values)
            logging.debug("Best nll value is {}".format(bestNLL))
            logging.debug("nll_values:")
            logging.debug(nll_values)
            nll_values = [oldValue-bestNLL for oldValue in nll_values]

            # Sort values just in case
            coords = zip(wc_values,nll_values)
            coords.sort(key = lambda t: t[0])
            wc_values, nll_values = zip(*coords)
            wc_values = numpy.asarray(wc_values)
            nll_values = numpy.asarray(nll_values)

            # Prep a spline to get the exact crossings of the 1,2 sigma levels
            graph = ROOT.TGraph()
            graph = ROOT.TGraph(len(coords), wc_values, nll_values)
            spline = ROOT.TSpline3("spline3", graph)
            
            #f1 = ROOT.TF1('f1','poln')
            #graph.Fit('poln','N')
            #fitfunc = graph.GetFunction('poln')

            # Extract 2-sig certainty intervals and save WC value of minumum
            lowedges=[]
            l1sigma=[]
            highedges=[]
            h1sigma=[]
            true_minimum = -1000
            prevnll = 1000
            prevnll1 = 1000
            for idx,coord in enumerate(coords):
                wc,nll = coord[0],coord[1]
                # Did we cross a low edge?
                if prevnll>4 and 4>nll:
                    #cross = fitfunc.GetX(4, graph.GetX()[idx-1], graph.GetX()[idx])
                    interval = prevnll-nll
                    linPctInterp = (prevnll-4)/interval
                    if idx == 0:
                        print 'Range not found, setting to infinity'
                        lowedges.append(-999)
                        highedges.append(999)
                    else:
                        cross = graph.GetX()[idx-1]+(graph.GetX()[idx]-graph.GetX()[idx-1])*linPctInterp
                        lowedges.append(cross)
                # Did we cross a high edge?
                if prevnll<4 and 4<nll:
                    #cross = fitfunc.GetX(4, graph.GetX()[idx-1], graph.GetX()[idx])
                    interval = nll-prevnll
                    linPctInterp = (4-prevnll)/interval
                    cross = graph.GetX()[idx-1]+(graph.GetX()[idx]-graph.GetX()[idx-1])*linPctInterp
                    highedges.append(cross)
                # Is this the best fit?
                if prevnll>1 and 1>nll:
                    #cross = fitfunc.GetX(2, graph.GetX()[idx-1], graph.GetX()[idx])
                    interval = prevnll-nll
                    linPctInterp = (prevnll-1)/interval
                    if idx == 0:
                        print 'Range not found, setting to infinity'
                        l1sigma.append(-999)
                        h1sigma.append(999)
                    else:
                        cross = graph.GetX()[idx-1]+(graph.GetX()[idx]-graph.GetX()[idx-1])*linPctInterp
                        l1sigma.append(cross)
                # Did we cross a high edge?
                if prevnll<1 and 1<nll:
                    #cross = fitfunc.GetX(2, graph.GetX()[idx-1], graph.GetX()[idx])
                    interval = nll-prevnll
                    linPctInterp = (1-prevnll)/interval
                    cross = graph.GetX()[idx-1]+(graph.GetX()[idx]-graph.GetX()[idx-1])*linPctInterp
                    h1sigma.append(cross)
                # Is this the best fit?
                if nll == min(nll_values):
                    true_minimum = wc
                # Continue
                prevnll = nll
            if not len(lowedges) == len(highedges):
                logging.error("Something is strange! Interval is missing endpoint!")
            if not len(l1sigma) == len(h1sigma):
                logging.error("Something is strange! Interval is missing endpoint!")
            if len(l1sigma) == 0:
                l1sigma.append(-999)
            if len(lowedges) == 0:
                lowedges.append(-999)
            if len(h1sigma) == 0:
                h1sigma.append(999)
            if len(highedges) == 0:
                highedges.append(999)
            ## uncomment for 2 decimal place printing for AN
            #true_minimum = '%.2f' % float(true_minimum)
            #lowedges = ['%.2f' % elem for elem in lowedges]
            #highedges = ['%.2f' % elem for elem in highedges]
            if siginterval==2: fit_array.append([param,true_minimum,lowedges,highedges])
            elif siginterval==1: fit_array.append([param,true_minimum,l1sigma,h1sigma])
            else: fit_array.append([param,true_minimum,lowedges,highedges])

        for line in fit_array:
            pline = line[:]
            if pline[0][-1] == 'i': pline[0] = pline[0][:-1] 
            pline[0] = '\\' + pline[0] + '$/\\Lambda^{2}$'
            pline[0] = pline[0].replace('3','a')
            #print line
            best = pline[1]
            best = round(float(best), 2)
            one = pline[2]
            one = ['%.2f' % elem for elem in one]
            two = pline[3]
            two = ['%.2f' % elem for elem in two]
            s = pline[0] + ' & '
            minima = []
            if len(one)==2:
                tmp = one[1]
                one[1] = two[0]
                two[0] = tmp
                ''' Find all local minima '''
                minima = numpy.where(nll_values<4)
                dx = numpy.diff(nll_values[minima])
                idx = dx[1:] * dx[:-1] < 0
                minima = wc_values[minima][numpy.append(numpy.logical_and(numpy.append(idx, [False]), dx<0), [False])]
                ''' All local minima found '''
                one = ', '.join(one)
                two = ', '.join(two)
                #s += '[' + str(one) + ']' + ' and [' + str(two) + ']'
                s += str(best) + ' (' + ', '.join([str(round(x,2)) for x in minima]) + ') ' + '& [' + str(one) + ']' + ' and [' + str(two) + ']' #uncomment to show best fit
                line.append([x for x in minima])
            else:
                #s += '[' + str(one[0]) + ', ' + str(two[0]) + ']'
                s += str(best) + '& [' + str(one[0]) + ', ' + str(two[0]) + ']' #uncomment to show best fit
            print s

        return fit_array

    def BestScanPlot(self, basename_float='', basename_freeze='', final=False, titles = ['\mathrm{Others\;Profiled}', '\mathrm{Others\;Fixed\;to\;SM}'], filename='', wcs=[], printFOM=False):

        # Colors to use for the plots
        clr_float = 1 # Black
        clr_freeze = 2 # Red

        if wcs != []: self.wcs = wcs
        ### Plot the best fit points/intervals for 1D scans others frozen and 1D scan others floating ###
        ROOT.gROOT.SetBatch(True)

        if not basename_float: basename_float='.EFT.SM.Float.Mar8'
        if not basename_freeze: basename_freeze='.EFT.SM.Freeze.Mar8'

        # Retrieve WC, Best Fit Value, Interval Lower Values, Interval Higher Values
        print 'two sigma'
        print 'float'
        fits_float = self.getIntervalFits(basename=basename_float)
        print 'freeze'
        fits_freeze = self.getIntervalFits(basename=basename_freeze)
        if printFOM:
            print('\n\nFoM (<1 is better)\nWC\tFoM')
            print('`(CI_({} high) - CI_({} low)) / (CI_({} high) - CI_({} low))`'.format(basename_freeze, basename_freeze, basename_float, basename_float))
            print('\n'.join([' '.join([lim[0][0], str(round(round(lim[1][2][0] - lim[1][3][0],3) / round(lim[0][2][0] - lim[0][3][0], 3),3))]) for lim in zip(fits_float, fits_freeze) if len(lim[0][2])==len(lim[1][2])==1 and len(lim[0][3])==len(lim[1][3])==1]))
        print '\n'
        print 'one sigma'
        print 'float'
        fits_float1sigma = self.getIntervalFits(basename=basename_float,siginterval=1)
        print 'freeze'
        fits_freeze1sigma = self.getIntervalFits(basename=basename_freeze,siginterval=1)

        for idx,line in enumerate(fits_float):
            if line[0]=='ctG':
                line[0] = 'ctG#times4'
                line[1] = line[1]*4
                line[2] = [val*2 for val in line[2]]
                line[3] = [val*2 for val in line[3]]
            if line[0]=='cQq13':
                line[0] = 'cQq13#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='ctq1':
                line[0] = 'ctq1#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq11':
                line[0] = 'cQq11#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq83':
                line[0] = 'cQq83#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            #if line[0]=='ctp':
            #    line[0] = 'ctp#divide5'
            #    line[1] = line[1]/5
            #    line[2] = [val/5 for val in line[2]]
            #    line[3] = [val/5 for val in line[3]]
            #if line[0]=='cpt':
            #    line[0] = 'cpt#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]
            #if line[0]=='cpQM':
            #    line[0] = 'cpQM#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]

        for idx,line in enumerate(fits_freeze):
            if line[0]=='ctG':
                line[0] = 'ctG#times4'
                line[1] = line[1]*4
                line[2] = [val*2 for val in line[2]]
                line[3] = [val*2 for val in line[3]]
            if line[0]=='cQq13':
                line[0] = 'cQq13#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='ctq1':
                line[0] = 'ctq1#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq11':
                line[0] = 'cQq11#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq83':
                line[0] = 'cQq83#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            #if line[0]=='ctp':
            #    line[0] = 'ctp#divide5'
            #    line[1] = line[1]/5
            #    line[2] = [val/5 for val in line[2]]
            #    line[3] = [val/5 for val in line[3]]
            #if line[0]=='cpt':
            #    line[0] = 'cpt#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]
            #if line[0]=='cpQM':
            #    line[0] = 'cpQM#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]

        for idx,line in enumerate(fits_float1sigma):
            if line[0]=='ctG':
                line[0] = 'ctG#times4'
                line[1] = line[1]*4
                line[2] = [val*2 for val in line[2]]
                line[3] = [val*2 for val in line[3]]
            if line[0]=='cQq13':
                line[0] = 'cQq13#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='ctq1':
                line[0] = 'ctq1#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq11':
                line[0] = 'cQq11#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq83':
                line[0] = 'cQq83#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            #if line[0]=='ctp':
            #    line[0] = 'ctp#divide5'
            #    line[1] = line[1]/5
            #    line[2] = [val/5 for val in line[2]]
            #    line[3] = [val/5 for val in line[3]]
            #if line[0]=='cpt':
            #    line[0] = 'cpt#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]
            #if line[0]=='cpQM':
            #    line[0] = 'cpQM#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]

        for idx,line in enumerate(fits_freeze1sigma):
            if line[0]=='ctG':
                line[0] = 'ctG#times4'
                line[1] = line[1]*4
                line[2] = [val*2 for val in line[2]]
                line[3] = [val*2 for val in line[3]]
            if line[0]=='cQq13':
                line[0] = 'cQq13#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='ctq1':
                line[0] = 'ctq1#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq11':
                line[0] = 'cQq11#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            if line[0]=='cQq83':
                line[0] = 'cQq83#times5'
                line[1] = line[1]*5
                line[2] = [val*5 for val in line[2]]
                line[3] = [val*5 for val in line[3]]
            #if line[0]=='ctp':
            #    line[0] = 'ctp#divide5'
            #    line[1] = line[1]/5
            #    line[2] = [val/5 for val in line[2]]
            #    line[3] = [val/5 for val in line[3]]
            #if line[0]=='cpt':
            #    line[0] = 'cpt#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]
            #if line[0]=='cpQM':
            #    line[0] = 'cpQM#divide2'
            #    line[1] = line[1]/2
            #    line[2] = [val/2 for val in line[2]]
            #    line[3] = [val/2 for val in line[3]]

        # Set y-coordinates for points and lines
        numWC=len(self.wcs)
        if '28redo' in basename_float:
            numWC=15
        y_float = [n*4+3 for n in range(0,numWC)]
        y_freeze = [n*4+2 for n in range(0,numWC)]

        # Set up the pad and axes
        canvas = ROOT.TCanvas('canvas','Summary Plot (SM Expectation)',500,800)
        if 'Asimov' not in basename_float:
            canvas = ROOT.TCanvas('canvas','Summary Plot',500,800)
        canvas.SetGrid(1)
        h_fit = ROOT.TH2F('h_fit','Summary Plot (SM Expectation)', 1, -10, 10, 4*numWC+1, 0, 4*numWC)
        if 'Asimov' not in basename_float:
            h_fit = ROOT.TH2F('h_fit','Summary Plot', 1, -10, 10, 4*numWC+1, 0, 4*numWC)
        h_fit.Draw()
        h_fit.SetStats(0)
        h_fit.GetYaxis().SetTickLength(0)
        h_fit.GetYaxis().SetNdivisions(numWC,False)
        h_fit.GetYaxis().SetLabelSize(0)
        h_fit.SetTitle('')
        h_fit.GetXaxis().SetLabelSize(0.04)

        # Add y-axis labels
        y_labels = []
        for idy,yval in enumerate(y_float):
            tex = fits_float[idy][0].rstrip('i')
            scale = ''
            if 'divide' in tex:
                scale = tex[tex.find('#divide'):]
                tex = tex[0:tex.find('#divide')]
                scale = scale.replace('#divide', '\\div')
            if 'times' in tex:
                scale = tex[tex.find('#times'):]
                scale = scale.replace('#times', '\\times')
                tex = tex[0:tex.find('#times')]
            tex = self.texdicfrac[tex]
            y_labels.append(ROOT.TLatex(h_fit.GetXaxis().GetXmin()*1.16,yval-1,tex+scale))
            #y_labels.append(ROOT.TLatex(h_fit.GetXaxis().GetXmin()*1.125,yval-1,tex+scale))
            y_labels[idy].SetTextAlign(22)
            y_labels[idy].SetTextSize(0.03)
            #if fits_float[idy][0]=='cpQM\\div2': y_labels[idy].SetTextSize(0.025)

        # Set the best fit points
        graph_float = ROOT.TGraph()
        graph_float = ROOT.TGraph(numWC, numpy.array([fittuple[1] for fittuple in fits_float], dtype='float'), numpy.array(y_float, dtype='float'))
        graph_float.SetMarkerStyle(20)
        graph_float.SetMarkerSize(0.5)
        graph_float.SetMarkerColor(clr_float)
        graph_float.SetLineColor(clr_float)

        graph_freeze = ROOT.TGraph()
        graph_freeze = ROOT.TGraph(numWC, numpy.array([fittuple[1] for fittuple in fits_freeze], dtype='float'), numpy.array(y_freeze, dtype='float'))
        graph_freeze.SetMarkerStyle(3)
        graph_freeze.SetMarkerSize(0.5)
        graph_freeze.SetMarkerColor(clr_freeze)
        graph_freeze.SetLineColor(clr_freeze)
        graph_freeze.SetLineStyle(3)

        # Add lines for the errors, but print the value if line would go off the pad
        lines_labels = []

        lines_float = []
        for idx,fittuple in enumerate(fits_float):
            for imin,imax in zip(fittuple[2],fittuple[3]):
                xmin = imin
                xmax = imax
                # If a segment ends below the left edge
                if xmax < h_fit.GetXaxis().GetXmin():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmin(),y_float[idx],3)
                    outside_label.SetMarkerColor(clr_float)
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins above the right edge
                if xmin > h_fit.GetXaxis().GetXmax():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmax(),y_float[idx],3)
                    outside_label.SetMarkerColor(clr_float)
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins below the left edge
                if xmin < h_fit.GetXaxis().GetXmin():
                    min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_float[idx],str(round(xmin,1)))
                    min_label.SetTextSize(0.03)
                    min_label.SetTextColor(clr_float)
                    lines_labels.append(min_label)
                    xmin = h_fit.GetXaxis().GetXmin()
                # If a segment ends above the right edge
                if xmax > h_fit.GetXaxis().GetXmax():
                    max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_float[idx],str(round(xmax,1)))
                    max_label.SetTextSize(0.03)
                    max_label.SetTextColor(clr_float)
                    max_label.SetTextAlign(30)
                    lines_labels.append(max_label)
                    xmax = h_fit.GetXaxis().GetXmax()
                lines_float.append(ROOT.TLine(xmin,y_float[idx],xmax,y_float[idx]))
                lines_float[-1].SetLineColor(clr_float)
        lines_float_1sigma = []
        for idx,fittuple in enumerate(fits_float1sigma):
            for imin,imax in zip(fittuple[2],fittuple[3]):
                xmin = imin
                xmax = imax
                # If a segment ends below the left edge
                if xmax < h_fit.GetXaxis().GetXmin():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmin(),y_float[idx],3)
                    outside_label.SetMarkerColor(clr_float)
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins above the right edge
                if xmin > h_fit.GetXaxis().GetXmax():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmax(),y_float[idx],3)
                    outside_label.SetMarkerColor(clr_float)
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins below the left edge
                if xmin < h_fit.GetXaxis().GetXmin():
                    min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_float[idx],str(round(xmin,1)))
                    min_label.SetTextSize(0.03)
                    min_label.SetTextColor(clr_float)
                    lines_labels.append(min_label)
                    xmin = h_fit.GetXaxis().GetXmin()
                # If a segment ends above the right edge
                if xmax > h_fit.GetXaxis().GetXmax():
                    max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_float[idx],str(round(xmax,1)))
                    max_label.SetTextSize(0.03)
                    max_label.SetTextColor(clr_float)
                    max_label.SetTextAlign(30)
                    lines_labels.append(max_label)
                    xmax = h_fit.GetXaxis().GetXmax()
                lines_float_1sigma.append(ROOT.TLine(xmin,y_float[idx],xmax,y_float[idx]))
                lines_float_1sigma[-1].SetLineColor(clr_float)
                lines_float_1sigma[-1].SetLineWidth(3)


        lines_freeze = []
        for idx,fittuple in enumerate(fits_freeze):
            for imin,imax in zip(fittuple[2],fittuple[3]):
                xmin = imin
                xmax = imax
                # If a segment ends below the left edge
                if xmax < h_fit.GetXaxis().GetXmin():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmin(),y_freeze[idx],3)
                    outside_label.SetMarkerColor(clr_freeze)  
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins above the right edge
                if xmin > h_fit.GetXaxis().GetXmax():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmax(),y_freeze[idx],3)
                    outside_label.SetMarkerColor(clr_freeze)
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins below the left edge
                if xmin < h_fit.GetXaxis().GetXmin():
                    min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_freeze[idx],str(round(xmin,1)))
                    min_label.SetTextSize(0.03)
                    min_label.SetTextColor(clr_freeze)
                    lines_labels.append(min_label)
                    xmin = h_fit.GetXaxis().GetXmin()
                # If a segment ends above the right edge
                if xmax > h_fit.GetXaxis().GetXmax():
                    max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_freeze[idx],str(round(xmax,1)))
                    max_label.SetTextSize(0.03)
                    max_label.SetTextColor(clr_freeze)
                    max_label.SetTextAlign(30)
                    lines_labels.append(max_label)
                    xmax = h_fit.GetXaxis().GetXmax()
                lines_freeze.append(ROOT.TLine(xmin,y_freeze[idx],xmax,y_freeze[idx]))
                lines_freeze[-1].SetLineColor(clr_freeze)
                lines_freeze[-1].SetLineStyle(3)
        lines_freeze_1sigma = []
        for idx,fittuple in enumerate(fits_freeze1sigma):
            for imin,imax in zip(fittuple[2],fittuple[3]):
                xmin = imin
                xmax = imax
                # If a segment ends below the left edge
                if xmax < h_fit.GetXaxis().GetXmin():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmin(),y_freeze[idx],3)
                    outside_label.SetMarkerColor(clr_freeze)
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins above the right edge
                if xmin > h_fit.GetXaxis().GetXmax():
                    outside_label = ROOT.TMarker(h_fit.GetXaxis().GetXmax(),y_freeze[idx],3)
                    outside_label.SetMarkerColor(clr_freeze)
                    outside_label.SetMarkerSize(2)
                    lines_labels.append(outside_label)
                    continue # Don't attempt to draw the line!
                # If a segment begins below the left edge
                if xmin < h_fit.GetXaxis().GetXmin():
                    min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_freeze[idx],str(round(xmin,1)))
                    min_label.SetTextSize(0.03)
                    min_label.SetTextColor(clr_freeze)
                    lines_labels.append(min_label)
                    xmin = h_fit.GetXaxis().GetXmin()
                # If a segment ends above the right edge
                if xmax > h_fit.GetXaxis().GetXmax():
                    max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_freeze[idx],str(round(xmax,1)))
                    max_label.SetTextSize(0.03)
                    max_label.SetTextColor(clr_freeze)
                    max_label.SetTextAlign(30)
                    lines_labels.append(max_label)
                    xmax = h_fit.GetXaxis().GetXmax()
                lines_freeze_1sigma.append(ROOT.TLine(xmin,y_freeze[idx],xmax,y_freeze[idx]))
                lines_freeze_1sigma[-1].SetLineColor(clr_freeze)
                lines_freeze_1sigma[-1].SetLineWidth(3)
                lines_freeze_1sigma[-1].SetLineStyle(3)

        # Add legend
        legend = ROOT.TLegend(0.1,0.9,0.45,0.995)
        if len(titles[0])>10 or len(titles[1])>10:
            legend = ROOT.TLegend(0.1,0.9,0.6,0.995)
        graph_float_1sigma = graph_float.Clone("graph_float_1sigma")
        graph_freeze_1sigma = graph_freeze.Clone("graph_freeze_1sigma")
        graph_float_1sigma.SetLineWidth(3)
        graph_freeze_1sigma.SetLineWidth(3)
        legend.AddEntry(graph_float,titles[0]+"\,(2\sigma)",'l')
        legend.AddEntry(graph_float_1sigma,titles[0]+"\,(1\sigma)",'l')
        legend.AddEntry(graph_freeze,titles[1]+"\,(2\sigma)",'l')
        legend.AddEntry(graph_freeze_1sigma,titles[1]+"\,(1\sigma)",'l')
        legend.SetTextSize(0.025)

        # Draw everything
        h_fit.GetXaxis().SetTitle("Wilson coefficient CI / #Lambda^{2} [TeV^{-2}]");
        h_fit.Draw()
        #graph_float.Draw('P same')
        #graph_freeze.Draw('P same')
        for line in lines_float:
            line.Draw('same')
        for line in lines_freeze:
            line.Draw('same')
        for line in lines_float_1sigma:
            line.Draw('same')
        for line in lines_freeze_1sigma:
            line.Draw('same')
        for label in lines_labels:
            label.Draw('same')
        for label in y_labels:
            label.Draw('same')
        legend.Draw('same')
        self.CMS_text = ROOT.TLatex(0.88, 0.94, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.04)
        self.CMS_text.SetTextAlign(33)
        self.CMS_text.Draw('same')
        #self.CMS_extra = ROOT.TLatex(0.9, 0.865, "Preliminary")# Simulation")
        self.CMS_extra = ROOT.TLatex(0.885, 0.92, "Supplementary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.03)
        self.CMS_extra.SetTextAlign(33)
        self.CMS_extra.SetTextFont(52)
        self.arXiv_extra = ROOT.TLatex(0.885, 0.90, self.arXiv)# Simulation")
        self.arXiv_extra.SetNDC(1)
        self.arXiv_extra.SetTextSize(0.03)
        self.arXiv_extra.SetTextAlign(30)
        self.arXiv_extra.SetTextFont(42)
        if not final: self.CMS_extra.Draw('same')
        #if not final: self.arXiv_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.9, 0.96, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.04)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        if final:
            canvas.Print('BestScanPlot_final.png','png')
            canvas.Print('BestScanPlot_final.eps','eps')
            os.system('sed -i "s/STIXGeneral-Italic/STIXXGeneral-Italic/g" BestScanPlot_final.eps')
            os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop BestScanPlot_final.eps BestScanPlot_final.pdf')
        else:
            canvas.Print('BestScanPlot{}.png'.format(filename),'png')
            canvas.Print('BestScanPlot{}.eps'.format(filename),'eps')
            os.system('sed -i "s/STIXGeneral-Italic/STIXXGeneral-Italic/g" BestScanPlot{}.eps'.format(filename))
            os.system('ps2pdf -dPDFSETTINGS=/prepress -dEPSCrop BestScanPlot{}.eps BestScanPlot{}.pdf'.format(filename,filename))

    def BestFitPlot(self):
        ### Plot the best fit results for 1D scans (others frozen) and 16D scan (simultaneous) ###
        ### Preferably this is not used in favor of the BestScanPlot, as we do not necessarily trust the simultaneous fit ###
        ROOT.gROOT.SetBatch(True)

        # WC, Best Fit Value, Symmetric Error, Lower Asymm Error, Higher Asymm Error
        fits_float = [
            ('ctW', 0.007932, 5.156692, -2.895143, 2.755763),
            ('ctZ', 0.001943, 10.497099, -3.072483, 3.093559),
            ('ctp', 0.000558, 2.153222, -2.153222, 2.153222),
            ('cpQM', 0.000139, 1.147733, -1.147733, 1.147733),
            ('ctG#times2', -4.3e-04, 01.49153, -01.49153, 01.49153),
            ('cbW', 0.0, 13.188208, -13.188208, 13.188208),
            ('cpQ3', -0.000237, 1.284475, -1.284475, 1.284475),
            ('cptb', 0.0, 53.786793, -53.786793, 53.786793),
            ('cpt', -0.000212, 1.581645, -1.581645, 1.581645),
            ('cQl3i', -0.007703, 29.297121, -29.297121, 29.297121),
            ('cQlMi', 0.001014, 7.825636, -7.825636, 7.825636),
            ('cQei', 0.005143, 20.504546, -20.504546, 20.504546),
            ('ctli', 0.003213, 29.193768, -29.193768, 29.193768),
            ('ctei', 0.001447, 10.075829, -10.075829, 10.075829),
            ('ctlSi', -0.116819, 25.739623, -25.739623, 25.739623),
            ('ctlTi', -2.4e-05, 5.846176, -5.846176, 5.846176)
        ]

        fits_freeze = [
            ('ctW', 0.002676, 1.945568, -1.375712, 1.285933),
            ('ctZ', 0.001882, 2.732047, -1.259174, 1.26976),
            ('ctp', 0.010915, 2.809417, -3.5235, 4.18801),
            ('cpQM', 0.003549, 1.386955, -1.779072, 1.688684),
            ('ctG#times2', 00.00868, 01.72676, -04.75713, 02.8743),
            ('cbW', -0.00522, 3.477419, -2.071278, 2.081717),
            ('cpQ3', 0.003113, 1.42997, -2.489773, 1.473674),
            ('cptb', -0.012994, 14.945221, -8.696135, 8.672515),
            ('cpt', 0.005012, 1.907986, -2.605411, 2.353756),
            ('cQl3i', 0.007081, 8.233226, -4.48008, 4.104843),
            ('cQlMi', 0.006358, 8.553002, -2.936935, 4.129151),
            ('cQei', 0.008352, 5.435639, -3.378824, 3.576448),
            ('ctli', 0.006025, 7.421842, -3.342865, 3.763873),
            ('ctei', 0.006285, 7.846579, -3.100699, 4.042864),
            ('ctlSi', 0.000755, 8.584274, -4.936348, 4.937865),
            ('ctlTi', 0.000268, 0.996374, -0.662427, 0.662461)
        ]

        # Set y-coordinates for points and lines
        numWC=len(self.wcs)
        y_float = [n*4+3 for n in range(0,numWC)]
        y_freeze = [n*4+2 for n in range(0,numWC)]

        # Set up the pad and axes
        canvas = ROOT.TCanvas('canvas','Best Fit Result (SM Expectation)',500,800)
        canvas.SetGrid(1)
        h_fit = ROOT.TH2F('h_fit','Best Fit Result (SM Expectation)', 1, -20, 20, 65, 0, 64)
        h_fit.Draw()
        h_fit.SetStats(0)
        #h_fit.GetXaxis().SetTickLength(0.1)
        h_fit.GetYaxis().SetTickLength(0)
        h_fit.GetYaxis().SetNdivisions(26,False)
        h_fit.GetYaxis().SetLabelSize(0)

        # Add y-axis labels
        y_labels = []
        for idy,yval in enumerate(y_float):
            y_labels.append(ROOT.TLatex(h_fit.GetXaxis().GetXmin()*1.125,yval-1,fits_float[idy][0].rstrip('i')))
            y_labels[idy].SetTextAlign(20)
            y_labels[idy].SetTextSize(0.03)

        # Set the best fit points
        graph_float = ROOT.TGraph(26, numpy.array([fittuple[1] for fittuple in fits_float], dtype='float'), numpy.array(y_float, dtype='float'))
        graph_float.SetMarkerStyle(20)
        graph_float.SetMarkerSize(0.5)
        graph_float.SetMarkerColor(2)

        graph_freeze = ROOT.TGraph(26, numpy.array([fittuple[1] for fittuple in fits_freeze], dtype='float'), numpy.array(y_freeze, dtype='float'))
        graph_freeze.SetMarkerStyle(20)
        graph_freeze.SetMarkerSize(0.5)
        graph_freeze.SetMarkerColor(4)

        # Add lines for the errors, but print the value if line would go off the pad
        lines_labels = []

        lines_float = []
        for idx,fittuple in enumerate(fits_float):
            xmin = fittuple[1]+fittuple[3]
            xmax = fittuple[1]+fittuple[4]
            if xmin < h_fit.GetXaxis().GetXmin():
                min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_float[idx],str(round(xmin,1)))
                min_label.SetTextSize(0.03)
                min_label.SetTextColor(2)
                lines_labels.append(min_label)
                xmin = h_fit.GetXaxis().GetXmin()
            if xmax > h_fit.GetXaxis().GetXmax():
                max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_float[idx],str(round(xmax,1)))
                max_label.SetTextSize(0.03)
                max_label.SetTextColor(2)
                max_label.SetTextAlign(30)
                lines_labels.append(max_label)
                xmax = h_fit.GetXaxis().GetXmax()
            lines_float.append(ROOT.TLine(xmin,y_float[idx],xmax,y_float[idx]))
            lines_float[idx].SetLineColor(2)

        lines_freeze = []
        for idx,fittuple in enumerate(fits_freeze):
            xmin = fittuple[1]+fittuple[3]
            xmax = fittuple[1]+fittuple[4]
            if xmin < h_fit.GetXaxis().GetXmin():
                min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_freeze[idx],str(round(xmin,1)))
                min_label.SetTextSize(0.03)
                min_label.SetTextColor(4)
                lines_labels.append(min_label)
                xmin = h_fit.GetXaxis().GetXmin()
            if xmax > h_fit.GetXaxis().GetXmax():
                max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_freeze[idx],str(round(xmax,1)))
                max_label.SetTextSize(0.03)
                max_label.SetTextColor(4)
                max_label.SetTextAlign(30)
                lines_labels.append(max_label)
                xmax = h_fit.GetXaxis().GetXmax()
            lines_freeze.append(ROOT.TLine(xmin,y_freeze[idx],xmax,y_freeze[idx]))
            lines_freeze[idx].SetLineColor(4)

        # Add legend
        legend = ROOT.TLegend(0.1,0.9,0.45,0.945)
        legend.AddEntry(graph_float,"Others Floating",'p')
        legend.AddEntry(graph_freeze,"Others Frozen to SM",'p')
        legend.SetTextSize(0.025)

        # CMS-required text
        self.CMS_text = ROOT.TLatex(0.9, 0.925, "CMS")# Simulation")
        self.CMS_text.SetNDC(1)
        self.CMS_text.SetTextSize(0.03)
        self.CMS_text.SetTextAlign(30)
        self.CMS_text.Draw('same')
        self.CMS_extra = ROOT.TLatex(0.9, 0.91, "Preliminary")# Simulation")
        self.CMS_extra.SetNDC(1)
        self.CMS_extra.SetTextSize(0.03)
        self.CMS_extra.SetTextAlign(30)
        self.CMS_extra.SetTextFont(52)
        self.CMS_extra.Draw('same')
        self.Lumi_text = ROOT.TLatex(0.9, 0.9, str(self.lumi) + " fb^{-1} (13 TeV)")
        self.Lumi_text.SetNDC(1)
        self.Lumi_text.SetTextSize(0.03)
        self.Lumi_text.SetTextAlign(30)
        self.Lumi_text.SetTextFont(42)
        self.Lumi_text.Draw('same')

        # Draw everything
        h_fit.Draw()
        graph_float.Draw('P same')
        graph_freeze.Draw('P same')
        for line in lines_float:
            line.Draw('same')
        for line in lines_freeze:
            line.Draw('same')
        for label in lines_labels:
            label.Draw('same')
        for label in y_labels:
            label.Draw('same')
        legend.Draw('same')
        self.CMS_text.Draw('same')
        self.Lumi_text.Draw('same')

        canvas.Print('BestFitPlot.png','png')


if __name__ == "__main__":
    log_file = 'EFTFit_out.log'

    FORMAT1 = '%(message)s'
    FORMAT2 = '[%(levelname)s] %(message)s'
    FORMAT3 = '[%(levelname)s][%(name)s] %(message)s'

    frmt1 = logging.Formatter(FORMAT1)
    frmt2 = logging.Formatter(FORMAT2)
    frmt3 = logging.Formatter(FORMAT3)

    logging.basicConfig(
        level=logging.DEBUG,
        format=FORMAT2,
        filename=log_file,
        filemode='w'
    )

    # Configure logging to also output to stdout
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(frmt2)
    logging.getLogger('').addHandler(console)

    plotter = EFTPlot()
    #plotter.ContourQuick()
    #plotter.Batch2DPlots('.EFT.SM.Float.ctWctZ','.EFT.SM.Float.ctWctZ','.EFT.SM.Float.postScan')
    #plotter.LLPlot1D('.EFT.SM.Float.ctW','ctW')
    #plotter.OverlayLLPlot1D('.EFT.SM.Float.ctW','.EFT.SM.Freeze.ctW','ctW')
    #plotter.BatchOverlayLLPlot1D()
        
