import ROOT
import logging
import os
import sys
import numpy
import itertools
import subprocess as sp
from EFTFit.Fitter.ContourHelper import ContourHelper

class EFTPlot(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ContourHelper = ContourHelper()

        self.operators = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        self.op_ranges = {  'ctW':(-6,6),   'ctZ':(-7,7),
                            'cpt':(-40,30), 'ctp':(-35,65),
                            'ctli':(-20,20),'ctlSi':(-22,22),
                            'cQl3i':(-20,20),'cptb':(-40,40),
                            'ctG':(-3,3),   'cpQM':(-30,50),  
                            'ctlTi':(-4,4),'ctei':(-20,20),
                            'cQei':(-16,16),'cQlMi':(-17,17),
                            'cpQ3':(-20,12),'cbW':(-10,10)
                         }
        self.histosFileName = 'Histos.root'

    def ResetHistoFile(self, name=''):
        ROOT.TFile('Histos{}.root'.format(name),'RECREATE')
        self.histosFileName = 'Histos{}.root'.format(name)

    def LLPlot1D(self, name='.test', frozen=False, operator='', log=False):
        if not operator:
            logging.error("No operator specified!")
            sys.exit()

        canvas = ROOT.TCanvas()

        #Draw 1D likelihood histogram from tree. Set to 50 bins.
        rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        limitTree = rootFile.Get('limit')
        limitTree.Draw('2*deltaNLL:{}>>{}1DNLL(50,{},{})'.format(operator,operator,self.op_ranges[operator][0],self.op_ranges[operator][1]),'2*deltaNLL>-1')

        #Fix the axis range since it messes up.
        th2 = canvas.GetPrimitive('{}1DNLL'.format(operator))
        th2.GetXaxis().SetRangeUser(self.op_ranges[operator][0],self.op_ranges[operator][1])

        #Change markers from invisible dots to nice triangles
        graph = canvas.GetPrimitive('Graph')
        graph.SetTitle(operator.rstrip('i'))
        graph.SetMarkerStyle(26)
        graph.SetMarkerSize(1)
        graph.SetMinimum(-0.1)

        #Add 1-sigma and 2-sigma lines. (Vertical lines were too hard, sadly)
        canvas.SetGrid(1)

        line68 = ROOT.TLine(self.op_ranges[operator][0],1,self.op_ranges[operator][1],1)
        line68.Draw('same')
        line68.SetLineColor(3)

        line95 = ROOT.TLine(self.op_ranges[operator][0],4,self.op_ranges[operator][1],4)
        line95.Draw('same')
        line95.SetLineColor(4)

        # CMS-required text
        CMS_text = ROOT.TLatex(0.665, 0.93, "CMS Preliminary Simulation")
        CMS_text.SetNDC(1)
        CMS_text.SetTextSize(0.02)
        CMS_text.Draw('same')
        Lumi_text = ROOT.TLatex(0.7, 0.91, "Luminosity = 41.29 fb^{-1}")
        Lumi_text.SetNDC(1)
        Lumi_text.SetTextSize(0.02)
        Lumi_text.Draw('same')

        #Check log option, then save as image
        if log:
            graph.SetMinimum(0.1)
            graph.SetLogz()
            canvas.Print('{}1DNLL_log.png'.format(operator,'freeze' if frozen else 'float'),'png')
        else:
            canvas.Print('{}1DNLL.png'.format(operator,'freeze' if frozen else 'float'),'png')

        rootFile.Close()

    def OverlayLLPlot1D(self, name1='.test', name2='.test', operator='', log=False):
        if not operator:
            logging.error("No operator specified!")
            sys.exit()

        canvas = ROOT.TCanvas()

        #Draw 1D likelihood histograms from trees. Set to 50 bins.
        rootFile1 = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name1))
        limitTree1 = rootFile1.Get('limit')
        limitTree1.Draw('2*deltaNLL:{}>>{}Black1DNLL(50,{},{})'.format(operator,operator,self.op_ranges[operator][0],self.op_ranges[operator][1]),'2*deltaNLL>-1')
        graph1 = canvas.GetPrimitive('Graph')
        graph1.SetName("Graph1")
        #graph1.SetMaximum(20)

        rootFile2 = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name2))
        limitTree2 = rootFile2.Get('limit')
        limitTree2.Draw('2*deltaNLL:{}>>{}Red1DNLL(50,{},{})'.format(operator,operator,self.op_ranges[operator][0],self.op_ranges[operator][1]),'2*deltaNLL>-1','same')
        graph2 = canvas.GetPrimitive('Graph')
        graph2.SetName("Graph2")
        #graph2.SetMaximum(20)

        # Change the axis range. Cap out Y at 10 (just above 3 sigma)
        th2Black = canvas.GetPrimitive('{}Black1DNLL'.format(operator))
        th2Black.GetYaxis().SetRangeUser(-0.5,10)

        # Squeeze X down to whatever range captures the float points
        graph1.Sort()
        xmin = self.op_ranges[operator][1]
        xmax = self.op_ranges[operator][0]
        for idx in range(graph1.GetN()):
            if graph1.GetY()[idx] < 10 and graph1.GetX()[idx] < xmin:
                xmin = graph1.GetX()[idx]
            if graph1.GetY()[idx] < 10 and graph1.GetX()[idx] > xmax:
                xmax = graph1.GetX()[idx]
        
        th2Black.GetXaxis().SetRangeUser(xmin,xmax)


        #Change markers from invisible dots to nice triangles
        graph1.SetTitle(operator.rstrip('i'))
        graph1.SetMarkerColor(1)
        graph1.SetMarkerStyle(26)
        graph1.SetMarkerSize(1)
        graph1.SetMinimum(-0.1)

        graph2.SetTitle(operator.rstrip('i'))
        graph2.SetMarkerColor(2)
        graph2.SetMarkerStyle(26)
        graph2.SetMarkerSize(1)
        graph2.SetMinimum(-0.1)

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
        Title = ROOT.TLatex(0.5, 0.95, "{} 2#DeltaNLL".format(operator))
        Title.SetNDC(1)
        Title.SetTextAlign(20)
        Title.Draw('same')
        th2Black.SetTitle("")
        th2Black.GetXaxis().SetTitle(operator)

        # CMS-required text
        CMS_text = ROOT.TLatex(0.9, 0.93, "CMS Preliminary Simulation")
        CMS_text.SetNDC(1)
        CMS_text.SetTextSize(0.02)
        CMS_text.SetTextAlign(30)
        CMS_text.Draw('same')
        Lumi_text = ROOT.TLatex(0.9, 0.91, "Luminosity = 41.29 fb^{-1}")
        Lumi_text.SetNDC(1)
        Lumi_text.SetTextSize(0.02)
        Lumi_text.SetTextAlign(30)
        Lumi_text.Draw('same')

        #Check log option, then save as image
        if log:
            graph1.SetMinimum(0.1)
            graph1.SetLogz()
            canvas.Print('Overlay{}1DNLL_log.png'.format(operator),'png')
        else:
            canvas.Print('Overlay{}1DNLL.png'.format(operator),'png')

        rootFile1.Close()
        rootFile2.Close()

    def BatchLLPlot1D(self, basename='.test', frozen=False, operators=[], log=False):
        if not operators:
            operators = self.operators

        ROOT.gROOT.SetBatch(True)

        for op in operators:
            self.LLPlot1D(basename+'.'+op, frozen, op, log)

    def BatchOverlayLLPlot1D(self, basename1='.EFT.SM.Float', basename2='.EFT.SM.Freeze', operators=[], log=False):
        if not operators:
            operators = self.operators

        ROOT.gROOT.SetBatch(True)

        for op in operators:
            self.OverlayLLPlot1D(basename1+'.'+op, basename2+'.'+op, op, log)

    def LLPlot2D(self, name='.test', operators=[], ceiling=1, log=False):
        if len(operators)!=2:
            logging.error("Function 'LLPlot2D' requires exactly two operators!")
            sys.exit()

        canvas = ROOT.TCanvas()

        # Open file and draw 2D histogram
        rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        limitTree = rootFile.Get('limit')
        hname = '{}{}less{}'.format(operators[1],operators[0],ceiling)
        if log:
            hname += "_log"

        limitTree.Draw('2*deltaNLL:{}:{}>>{}(200,{},{},200,{},{})'.format(operators[1],operators[0],hname,self.op_ranges[operators[0]][0],self.op_ranges[operators[0]][1],self.op_ranges[operators[1]][0],self.op_ranges[operators[1]][1]), '2*deltaNLL<{}'.format(ceiling), 'prof colz')
        
        hist = canvas.GetPrimitive(hname)

        # Draw best fit point from grid scan
        #limit.Draw(operators[0]+":"+operators[1],'quantileExpected==-1','p same') # Best fit point from grid scan
        #best_fit = canvas.FindObject('Graph')
        #best_fit.SetMarkerSize(1)
        #best_fit.SetMarkerStyle(34)
        #best_fit.Draw("p same")

        # Change plot formats
        hist.GetXaxis().SetRangeUser(self.op_ranges[operators[0]][0],self.op_ranges[operators[0]][1])
        hist.GetYaxis().SetRangeUser(self.op_ranges[operators[1]][0],self.op_ranges[operators[1]][1])
        if log:
            canvas.SetLogz()
        hist.GetYaxis().SetTitle(operators[1].rstrip('i'))
        hist.GetXaxis().SetTitle(operators[0].rstrip('i'))
        hist.SetTitle("2*deltaNLL < {}".format(operators[1],operators[0],ceiling))
        hist.SetStats(0)

        # CMS-required text
        CMS_text = ROOT.TLatex(0.665, 0.93, "CMS Preliminary Simulation")
        CMS_text.SetNDC(1)
        CMS_text.SetTextSize(0.02)
        CMS_text.Draw('same')
        Lumi_text = ROOT.TLatex(0.7, 0.91, "Luminosity = 41.29 fb^{-1}")
        Lumi_text.SetNDC(1)
        Lumi_text.SetTextSize(0.02)
        Lumi_text.Draw('same')

        # Save plot
        canvas.Print(hname+".png",'png')

        # Save to root file
        # Log settings don't save to the histogram, so redundant to save those
        if not log:
            outfile = ROOT.TFile(self.histosFileName,'UPDATE')
            hist.Write()
            outfile.Close()

    def ContourPlot(self, name='.test', operators=[]):
        if len(operators)!=2:
            logging.error("Function 'ContourPlot' requires exactly two operators!")
            sys.exit()

        best2DeltaNLL = 1000000
        canvas = ROOT.TCanvas('c','c',800,800)

        # Get Grid scan and copy to h_contour
        gridFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        gridTree = gridFile.Get('limit')
        #gridTree.Draw('2*deltaNLL:{}:{}>>grid(200,{},{},200,{},{})'.format(operators[1],operators[0],self.op_ranges[operators[0]][0],self.op_ranges[operators[0]][1],self.op_ranges[operators[1]][0],self.op_ranges[operators[1]][1]), '2*deltaNLL<100', 'prof colz')
        gridTree.Draw('2*deltaNLL:{}:{}>>grid(200,{},{},200,{},{})'.format(operators[1],operators[0],self.op_ranges[operators[0]][0],self.op_ranges[operators[0]][1],self.op_ranges[operators[1]][0],self.op_ranges[operators[1]][1]), '', 'prof colz')
        original = ROOT.TProfile2D(canvas.GetPrimitive('grid'))
        h_contour = ROOT.TProfile2D('h_contour','h_contour',200,self.op_ranges[operators[0]][0],self.op_ranges[operators[0]][1],200,self.op_ranges[operators[1]][0],self.op_ranges[operators[1]][1])
        #original.Copy(h_contour)

        # Find bin with best likelihood value
        # Bins run from 1->nbins, not 0->nbins-1
        for xbin in range(original.GetNbinsX()):
            for ybin in range(original.GetNbinsY()):
                if best2DeltaNLL > original.GetBinContent(original.GetBin(1+xbin,1+ybin)):
                    best2DeltaNLL = original.GetBinContent(original.GetBin(1+xbin,1+ybin))
                    #print "New best bin:",best2DeltaNLL
                
        #for bin in range(original.GetNbinsX()*original.GetNbinsY()):
        #    if best2DeltaNLL > original.GetBinContent(1+bin):
        #        best2DeltaNLL = original.GetBinContent(1+bin)
        #        print "New best bin:",best2DeltaNLL

        # Adjust scale so that the best bin has content 0
        #for bin in range(original.GetSize()):
            #if original.GetBinContent(bin)!=0:
                #h_contour.SetBinEntries(bin,1)
            # 0th bin is underflow, so skip
        #    h_contour.SetBinContent(1+bin,original.GetBinContent(1+bin)-best2DeltaNLL)

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

        # Set contours
        #colors = numpy.array([ROOT.kYellow+1,ROOT.kCyan-2,ROOT.kBlue-2,ROOT.kWhite], dtype='int32')
        #ROOT.gStyle.SetPalette(4,colors)

        #levels = numpy.array([0,2.30,5.99,11.83])
        #h_contour.SetContour(4,levels)

        # Change to lines
        #h_contour.Draw('CONT Z LIST')
        #canvas.Update()
        #contours_lines = [ROOT.TList(),ROOT.TList(),ROOT.TList()]
        #for item in ROOT.gROOT.GetListOfSpecials():
        #    print item
        #contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
        #for idx,contour in enumerate(contours):
        #    for contour_level in contour:
        #        if contour_level.GetN() > 20:
        #            contours_lines[idx].Add(contour_level.Clone())
        #self.styleMultiGraph(contours_lines[0],1,3,1)
        #self.styleMultiGraph(contours_lines[1],1,3,9)
        #self.styleMultiGraph(contours_lines[2],1,3,2)
        #for contour_line in contours_lines:
        #    contour_line.Draw('L same')

        c68 = self.ContourHelper.GetContour(h_contour,2.30)
        c95 = self.ContourHelper.GetContour(h_contour,4.99)
        c997 = self.ContourHelper.GetContour(h_contour,11.83)
        self.ContourHelper.styleMultiGraph(c68,ROOT.kYellow+1,3,1)
        self.ContourHelper.styleMultiGraph(c95,ROOT.kCyan-2,3,1)
        self.ContourHelper.styleMultiGraph(c997,ROOT.kBlue-2,3,1)
        #self.ContourHelper.styleMultiGraph(c68,1,3,1)
        #self.ContourHelper.styleMultiGraph(c95,1,3,9)
        #self.ContourHelper.styleMultiGraph(c997,1,3,2)

        # Marker for SM point
        marker_1 = ROOT.TMarker()
        marker_1.SetMarkerSize(2.0)
        marker_1.SetMarkerColor(97)
        marker_1.SetMarkerStyle(33)
        marker_2 = ROOT.TMarker()
        marker_2.SetMarkerSize(1.2)
        marker_2.SetMarkerColor(89)
        marker_2.SetMarkerStyle(33)


        # Change format of plot
        h_contour.SetStats(0)
        h_contour.SetTitle("Significance Contours")
        h_contour.GetYaxis().SetTitle(operators[1].rstrip('i'))
        h_contour.GetXaxis().SetTitle(operators[0].rstrip('i'))

        # CMS-required text
        CMS_text = ROOT.TLatex(0.9, 0.93, "CMS Preliminary Simulation")
        CMS_text.SetNDC(1)
        CMS_text.SetTextSize(0.02)
        CMS_text.SetTextAlign(30)
        Lumi_text = ROOT.TLatex(0.9, 0.91, "Luminosity = 41.29 fb^{-1}")
        Lumi_text.SetNDC(1)
        Lumi_text.SetTextSize(0.02)
        Lumi_text.SetTextAlign(30)

        # Draw and save plot
        h_contour.Draw('AXIS')
        c68.Draw('L SAME')
        c95.Draw('L SAME')
        c997.Draw('L SAME')
        marker_1.DrawMarker(0,0)
        marker_2.DrawMarker(0,0)

        CMS_text.Draw('same')
        Lumi_text.Draw('same')
        canvas.Print('{}{}contour.png'.format(operators[1],operators[0]),'png')

        # Save contour to histogram file
        outfile = ROOT.TFile(self.histosFileName,'UPDATE')
        h_contour.Write()
        outfile.Close()

        ROOT.gStyle.SetPalette(57)

    def CorrelationMatrix(self, name='', nuisances=True, freeze=True):

        canvas = ROOT.TCanvas()

        # Get rooFit object
        rooFitFile = ROOT.TFile.Open('../fit_files/multidimfit{}.root'.format(name))
        rooFit = rooFitFile.Get('fit_mdf')

        # Get correlation matrix
        rooFit.correlationHist().Draw('colz')
        matrix = canvas.GetPrimitive('correlation_matrix')

        # Change format of plot
        matrix.SetStats(0)
        matrix.SetTitle("Correlation Matrix")

        # Decide whether or not to keep the nuisance parameters in
        # If not, the number of bins (operators) varies on whether the scan froze the other 14
        if nuisances:
            matrix.SetName("corrMatrix")
        else:
            matrix.SetName("corrMatrix_noNuisances")
            nbins = matrix.GetNbinsX()
            if freeze:
                matrix.GetYaxis().SetRange(1,2)
                matrix.GetXaxis().SetRange(nbins-1,nbins)
            else:
                matrix.GetYaxis().SetRange(1,16)
                matrix.GetXaxis().SetRange(nbins-15,nbins)

        # Save the plot
        canvas.Print(matrix.GetName()+'.png','png')

        # Save the plot to the histogram file
        outfile = ROOT.TFile(self.histosFileName,'UPDATE')
        matrix.Write()
        outfile.Close()

    def Batch2DPlots(self, histosFileName='.EFT.SM.Float', gridScanName='.EFT.SM.Float.gridScan.ctWctZ', postScanName='.EFT.SM.Float.postScan', operators=['ctW','ctZ'], freeze=False):
        ROOT.gROOT.SetBatch(True)
        self.ResetHistoFile(histosFileName)

        self.LLPlot2D(gridScanName,operators,1,False)
        self.LLPlot2D(gridScanName,operators,10,False)
        self.LLPlot2D(gridScanName,operators,100,False)
        self.LLPlot2D(gridScanName,operators,1,True)
        self.LLPlot2D(gridScanName,operators,10,True)
        self.LLPlot2D(gridScanName,operators,100,True)

        #self.CorrelationMatrix(postScanName,False,freeze)
        #self.CorrelationMatrix(postScanName,True,freeze)

        self.ContourPlot(gridScanName,operators)

    def BatchBatch2DPlots(self, histosFileName='.EFT.SM.Float', basenamegrid='.EFT.SM.Float.gridScan', basenamefit='.EFT.SM.Float.postScanFit', operators=[], freeze=False):
        if not operators:
            operators = self.operators

        ROOT.gROOT.SetBatch(True)

        for pois in itertools.combinations(operators,2):
            self.Batch2DPlots('{}.{}{}'.format(histosFileName,pois[0],pois[1]), '{}.{}{}'.format(basenamegrid,pois[0],pois[1]), '{}.{}{}'.format(basenamefit,pois[0],pois[1]), operators=pois, freeze=freeze)

            if not os.path.isdir('Histos{}.{}{}'.format(histosFileName,pois[0],pois[1])):
                sp.call(['mkdir', 'Histos{}.{}{}'.format(histosFileName,pois[0],pois[1])])
            sp.call(['mv', 'Histos{}.{}{}.root'.format(histosFileName,pois[0],pois[1]), 'Histos{}.{}{}/'.format(histosFileName,pois[0],pois[1])])

            for filename in os.listdir('.'):
                if filename.endswith('.png'):            
                    sp.call(['mv', filename, 'Histos{}.{}{}/'.format(histosFileName,pois[0],pois[1])])

    def Batch2DStudyPlots(self, histosFileName='.EFT.SM.Float', gridScanName='.EFT.SM.Float.gridScan.ctWctZ', operators=['ctW','ctZ']):
        ROOT.gROOT.SetBatch(True)
        self.ResetHistoFile(histosFileName)

        #self.LLPlot2D(gridScanName,operators,1,False)
        #self.LLPlot2D(gridScanName,operators,10,False)
        self.LLPlot2D(gridScanName,operators,100,False)
        self.LLPlot2D(gridScanName,operators,1000000000,False)

        self.ContourPlot(gridScanName,operators)

    def BatchBatchStudy2DPlots(self, histosFileName='.EFT.SM.Float.Jan20', basenamegrid='.EFT.SM.Float.Jan20'):
        operators_POI = [('ctZ','ctW'),('ctp','cpt'),('ctlSi','ctli'),('cptb','cQl3i'),('ctG','cpQM'),('ctei','ctlTi'),('cQlMi','cQei'),('cpQ3','cbW')]
        #operators_POI = [('ctW','ctZ'),('cpt','ctp'),('ctli','ctlSi'),('cQl3i','cptb'),('ctG','cpQM'),('ctlTi','ctei'),('cQei','cQlMi'),('cpQ3','cbW')]
        ROOT.gROOT.SetBatch(True)

        for pois in operators_POI:
            self.Batch2DStudyPlots('{}.{}{}'.format(histosFileName,pois[0],pois[1]), '{}.{}{}'.format(basenamegrid,pois[0],pois[1]), operators=pois)

    def getIntervalFits(self, basename='.EFT.SM.Float', operators=[]):
        ### Return a table of operators, their best fits, and their uncertainties ###
        ### Use 1D scans instead of regular MultiDimFit ###
        if not operators:
            operators = self.operators

        ROOT.gROOT.SetBatch(True)

        fit_array = []

        canvas = ROOT.TCanvas()
        for op in operators:

            canvas.Clear()

            logging.debug("Obtaining result of scan: higgsCombine{}.{}.MultiDimFit.root".format(basename,op))
            fit_file = ROOT.TFile.Open('../fit_files/higgsCombine{}.{}.MultiDimFit.root'.format(basename,op))
            limit_tree = fit_file.Get('limit')

            limit_tree.Draw('2*deltaNLL:{}>>{}1DNLL(50,{},{})'.format(op,op,self.op_ranges[op][0],self.op_ranges[op][1]),'2*deltaNLL>-1','same')
            graph = canvas.GetPrimitive('Graph')
            #graph.SetName("Graph")

            graph.Sort()

            lowedges=[]
            highedges=[]
            minimums=[]
            true_minimum = [-1000,1000]
            prev = 1000
            for idx in range(graph.GetN()):
                y_val = graph.GetY()[idx]
                if prev>4 and 4>y_val:
                    lowedges.append((graph.GetX()[idx-1]+graph.GetX()[idx+1])/2)
                if prev<4 and 4<y_val:
                    highedges.append((graph.GetX()[idx-1]+graph.GetX()[idx+1])/2)
                if y_val < true_minimum[1]:
                    true_minimum = [graph.GetX()[idx],y_val]
                if y_val<prev and y_val<graph.GetY()[idx+1]:
                    minimums.append((graph.GetX()[idx],y_val))
                prev = y_val
            if not len(lowedges) == len(highedges):
                logging.error("Something is strange! Interval is missing endpoint!")

            #for interval in zip(lowedges,highedges):
            #    true_min = [-1000,1000]
            #    for minimum in minimums:
            #        if minimum[1]<true_min[1] and interval[0]<minimum[0] and minimum[0]<interval[1]:
            #            true_min = minimum
            #    true_minimums.append(true_min[0])

            #fit_array.append([op,[list(l) for l in zip(true_minimums,lowedges,highedges)]])
            fit_array.append([op,true_minimum[0],lowedges,highedges])

        for line in fit_array:
            print line

        return fit_array

    def BestScanPlot(self):
        ### Plot the best fit points/intervals for 1D scans others frozen and 1D scan others floating ###
        ROOT.gROOT.SetBatch(True)

        # WC, Best Fit Value, Symmetric Error, Lower Asymm Error, Higher Asymm Error
        fits_float = self.getIntervalFits('.EFT.SM.Float.Jan27.500')
        fits_freeze = self.getIntervalFits('.EFT.SM.Freeze.Jan27.500')

        for idx,line in enumerate(fits_float):
            if line[0]=='ctG':
                line[0] = 'ctG#times10'
                line[1] = line[1]*10
                line[2] = [val*10 for val in line[2]]
                line[3] = [val*10 for val in line[3]]
            if line[0]=='ctp':
                line[0] = 'ctp#divide5'
                line[1] = line[1]/5
                line[2] = [val/5 for val in line[2]]
                line[3] = [val/5 for val in line[3]]
            if line[0]=='cpt':
                line[0] = 'cpt#divide2'
                line[1] = line[1]/2
                line[2] = [val/2 for val in line[2]]
                line[3] = [val/2 for val in line[3]]

        for idx,line in enumerate(fits_freeze):
            if line[0]=='ctG':
                line[0] = 'ctG#times10'
                line[1] = line[1]*10
                line[2] = [val*10 for val in line[2]]
                line[3] = [val*10 for val in line[3]]
            if line[0]=='ctp':
                line[0] = 'ctp#divide5'
                line[1] = line[1]/5
                line[2] = [val/5 for val in line[2]]
                line[3] = [val/5 for val in line[3]]
            if line[0]=='cpt':
                line[0] = 'cpt#divide2'
                line[1] = line[1]/2
                line[2] = [val/2 for val in line[2]]
                line[3] = [val/2 for val in line[3]]

        # Set y-coordinates for points and lines
        y_float = [n*4+3 for n in range(0,16)]
        y_freeze = [n*4+2 for n in range(0,16)]

        # Set up the pad and axes
        canvas = ROOT.TCanvas('canvas','Summary Plot (SM Expectation)',500,800)
        canvas.SetGrid(1)
        h_fit = ROOT.TH2F('h_fit','Summary Plot (SM Expectation)', 1, -20, 20, 65, 0, 64)
        h_fit.Draw()
        h_fit.SetStats(0)
        #h_fit.GetXaxis().SetTickLength(0.1)
        h_fit.GetYaxis().SetTickLength(0)
        h_fit.GetYaxis().SetNdivisions(16,False)
        h_fit.GetYaxis().SetLabelSize(0)

        # Add y-axis labels
        y_labels = []
        for idy,yval in enumerate(y_float):
            y_labels.append(ROOT.TLatex(h_fit.GetXaxis().GetXmin()*1.125,yval-1,fits_float[idy][0].rstrip('i')))
            y_labels[idy].SetTextAlign(20)
            y_labels[idy].SetTextSize(0.03)

        # Set the best fit points
        graph_float = ROOT.TGraph()
        #for idx,fittuple in enumerate(fits_float):
        #    graph_float.SetPoint(graph_float.GetN(),fittuple[idx][1],y_float[idx])
        graph_float = ROOT.TGraph(16, numpy.array([fittuple[1] for fittuple in fits_float], dtype='float'), numpy.array(y_float, dtype='float'))
        graph_float.SetMarkerStyle(20)
        graph_float.SetMarkerSize(0.5)
        graph_float.SetMarkerColor(1)

        graph_freeze = ROOT.TGraph()
        #for idx,fittuple in enumerate(fits_freeze):
        #    for xval in fittuple[1]:
        #        graph_freeze.SetPoint(graph_freeze.GetN(),xval,y_freeze[idx])
        graph_freeze = ROOT.TGraph(16, numpy.array([fittuple[1] for fittuple in fits_freeze], dtype='float'), numpy.array(y_freeze, dtype='float'))
        graph_freeze.SetMarkerStyle(20)
        graph_freeze.SetMarkerSize(0.5)
        graph_freeze.SetMarkerColor(2)

        # Add lines for the errors, but print the value if line would go off the pad
        lines_labels = []

        lines_float = []
        for idx,fittuple in enumerate(fits_float):
            for imin,imax in zip(fittuple[2],fittuple[3]):
                xmin = imin
                xmax = imax
                if xmin < h_fit.GetXaxis().GetXmin():
                    min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_float[idx],str(round(xmin,1)))
                    min_label.SetTextSize(0.03)
                    min_label.SetTextColor(1)
                    lines_labels.append(min_label)
                    xmin = h_fit.GetXaxis().GetXmin()
                if xmax > h_fit.GetXaxis().GetXmax():
                    max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_float[idx],str(round(xmax,1)))
                    max_label.SetTextSize(0.03)
                    max_label.SetTextColor(1)
                    max_label.SetTextAlign(30)
                    lines_labels.append(max_label)
                    xmax = h_fit.GetXaxis().GetXmax()
                lines_float.append(ROOT.TLine(xmin,y_float[idx],xmax,y_float[idx]))
                lines_float[-1].SetLineColor(1)


        lines_freeze = []
        for idx,fittuple in enumerate(fits_freeze):
            for imin,imax in zip(fittuple[2],fittuple[3]):
                xmin = imin
                xmax = imax
                if xmin < h_fit.GetXaxis().GetXmin():
                    min_label = ROOT.TLatex(h_fit.GetXaxis().GetXmin(),y_freeze[idx],str(round(xmin,1)))
                    min_label.SetTextSize(0.03)
                    min_label.SetTextColor(2)
                    lines_labels.append(min_label)
                    xmin = h_fit.GetXaxis().GetXmin()
                if xmax > h_fit.GetXaxis().GetXmax():
                    max_label = ROOT.TLatex(h_fit.GetXaxis().GetXmax(),y_freeze[idx],str(round(xmax,1)))
                    max_label.SetTextSize(0.03)
                    max_label.SetTextColor(2)
                    max_label.SetTextAlign(30)
                    lines_labels.append(max_label)
                    xmax = h_fit.GetXaxis().GetXmax()
                lines_freeze.append(ROOT.TLine(xmin,y_freeze[idx],xmax,y_freeze[idx]))
                lines_freeze[-1].SetLineColor(2)

        # Add legend
        legend = ROOT.TLegend(0.1,0.9,0.45,0.945)
        legend.AddEntry(graph_float,"Others Floating",'p')
        legend.AddEntry(graph_freeze,"Others Frozen to SM",'p')
        legend.SetTextSize(0.025)

        # CMS-required text
        CMS_text = ROOT.TLatex(0.9, 0.925, "CMS Preliminary Simulation")
        CMS_text.SetNDC(1)
        CMS_text.SetTextAlign(30)
        CMS_text.SetTextSize(0.03)
        Lumi_text = ROOT.TLatex(0.9, 0.9, "Luminosity = 41.29 fb^{-1}")
        Lumi_text.SetNDC(1)
        Lumi_text.SetTextAlign(30)
        Lumi_text.SetTextSize(0.03)

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
        CMS_text.Draw('same')
        Lumi_text.Draw('same')

        canvas.Print('BestScanPlot.png','png')

    def BestFitPlot(self):
        ### Plot the best fit results for 1D scans (others frozen) and 16D scan (simultaneous) ###
        ROOT.gROOT.SetBatch(True)

        # WC, Best Fit Value, Symmetric Error, Lower Asymm Error, Higher Asymm Error
        fits_float = [
            ('ctW', 0.007932, 5.156692, -2.895143, 2.755763),
            ('ctZ', 0.001943, 10.497099, -3.072483, 3.093559),
            ('ctp', 0.000558, 2.153222, -2.153222, 2.153222),
            ('cpQM', 0.000139, 1.147733, -1.147733, 1.147733),
            ('ctG#times10', -4.3e-04, 01.49153, -01.49153, 01.49153),
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
            ('ctG#times10', 00.00868, 01.72676, -04.75713, 02.8743),
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
        y_float = [n*4+3 for n in range(0,16)]
        y_freeze = [n*4+2 for n in range(0,16)]

        # Set up the pad and axes
        canvas = ROOT.TCanvas('canvas','Best Fit Result (SM Expectation)',500,800)
        canvas.SetGrid(1)
        h_fit = ROOT.TH2F('h_fit','Best Fit Result (SM Expectation)', 1, -20, 20, 65, 0, 64)
        h_fit.Draw()
        h_fit.SetStats(0)
        #h_fit.GetXaxis().SetTickLength(0.1)
        h_fit.GetYaxis().SetTickLength(0)
        h_fit.GetYaxis().SetNdivisions(16,False)
        h_fit.GetYaxis().SetLabelSize(0)

        # Add y-axis labels
        y_labels = []
        for idy,yval in enumerate(y_float):
            y_labels.append(ROOT.TLatex(h_fit.GetXaxis().GetXmin()*1.125,yval-1,fits_float[idy][0].rstrip('i')))
            y_labels[idy].SetTextAlign(20)
            y_labels[idy].SetTextSize(0.03)

        # Set the best fit points
        graph_float = ROOT.TGraph(16, numpy.array([fittuple[1] for fittuple in fits_float], dtype='float'), numpy.array(y_float, dtype='float'))
        graph_float.SetMarkerStyle(20)
        graph_float.SetMarkerSize(0.5)
        graph_float.SetMarkerColor(2)

        graph_freeze = ROOT.TGraph(16, numpy.array([fittuple[1] for fittuple in fits_freeze], dtype='float'), numpy.array(y_freeze, dtype='float'))
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
        CMS_text = ROOT.TLatex(0.9, 0.925, "CMS Preliminary Simulation")
        CMS_text.SetNDC(1)
        CMS_text.SetTextAlign(30)
        CMS_text.SetTextSize(0.03)
        Lumi_text = ROOT.TLatex(0.9, 0.9, "Luminosity = 41.29 fb^{-1}")
        Lumi_text.SetNDC(1)
        Lumi_text.SetTextAlign(30)
        Lumi_text.SetTextSize(0.03)

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
        CMS_text.Draw('same')
        Lumi_text.Draw('same')

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
