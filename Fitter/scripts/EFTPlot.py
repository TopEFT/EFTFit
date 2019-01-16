import ROOT
import logging
import os
import sys
import numpy
import itertools
import subprocess as sp

class EFTPlot(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.operators = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
        self.histosFileName = 'Histos.root'

    def ResetHistoFile(self, name=''):
        ROOT.TFile('Histos{}.root'.format(name),'RECREATE')
        self.histosFileName = 'Histos{}.root'.format(name)

    def LLPlot1D(self, name='.test', operator='', log=False):
        if not operator:
            logging.error("No operator specified!")
            sys.exit()

        canvas = ROOT.TCanvas()

        #Draw 1D likelihood histogram from tree. Set to 50 bins from -5 to 5.
        rootFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        limitTree = rootFile.Get('limit')
        limitTree.Draw('2*deltaNLL:{}>>{}1DNLL(50,-5,5)'.format(operator,operator),'2*deltaNLL>-1')

        #Fix the axis range since it messes up.
        th2 = canvas.GetPrimitive('{}1DNLL'.format(operator))
        th2.GetXaxis().SetRangeUser(-5.,5.)

        #Change markers from invisible dots to nice triangles
        graph = canvas.GetPrimitive('Graph')
        graph.SetTitle(operator)
        graph.SetMarkerStyle(26)
        graph.SetMarkerSize(1)
        graph.SetMinimum(-0.1)

        #Add 1-sigma and 2-sigma lines. (Vertical lines were too hard, sadly)
        canvas.SetGrid(1)

        line68 = ROOT.TLine(-5,1,5,1)
        line68.Draw("same")
        line68.SetLineColor(3)

        line95 = ROOT.TLine(-5,4,5,4)
        line95.Draw("same")
        line95.SetLineColor(4)

        #Check log option, then save as image
        if log:
            graph.SetMinimum(0.1)
            graph.SetLogz()
            canvas.Print('{}1DNLL_log.png'.format(operator),'png')
        else:
            canvas.Print('{}1DNLL.png'.format(operator),'png')

        rootFile.Close()

    def OverlayLLPlot1D(self, name1='.test', name2='.test', operator='', log=False):
        if not operator:
            logging.error("No operator specified!")
            sys.exit()

        canvas = ROOT.TCanvas()

        #Draw 1D likelihood histograms from trees. Set to 50 bins from -5 to 5.
        rootFile1 = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name1))
        limitTree1 = rootFile1.Get('limit')
        limitTree1.Draw('2*deltaNLL:{}>>{}1DNLL(50,-5,5)'.format(operator,operator),'2*deltaNLL>-1')
        graph1 = canvas.GetPrimitive('Graph')
        graph1.SetName("Graph1")

        rootFile2 = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name2))
        limitTree2 = rootFile2.Get('limit')
        limitTree2.Draw('2*deltaNLL:{}>>{}1DNLL(50,-5,5)'.format(operator,operator),'2*deltaNLL>-1','same')
        graph2 = canvas.GetPrimitive('Graph')
        graph2.SetName("Graph2")

        #Fix the axis range since it messes up.
        th2 = canvas.GetPrimitive('{}1DNLL'.format(operator))
        th2.GetXaxis().SetRangeUser(-5.,5.)

        #Change markers from invisible dots to nice triangles
        graph1.SetTitle(operator)
        graph1.SetMarkerStyle(26)
        graph1.SetMarkerSize(1)
        graph1.SetMinimum(-0.1)

        graph2.SetTitle(operator)
        graph2.SetMarkerColor(2)
        graph2.SetMarkerStyle(26)
        graph2.SetMarkerSize(1)
        graph2.SetMinimum(-0.1)

        #Add 1-sigma and 2-sigma lines. (Vertical lines were too hard, sadly)
        canvas.SetGrid(1)

        line68 = ROOT.TLine(-5,1,5,1)
        line68.Draw("same")
        line68.SetLineColor(3)

        line95 = ROOT.TLine(-5,4,5,4)
        line95.Draw("same")
        line95.SetLineColor(4)

        #Check log option, then save as image
        if log:
            graph1.SetMinimum(0.1)
            graph1.SetLogz()
            canvas.Print('Overlay{}1DNLL_log.png'.format(operator),'png')
        else:
            canvas.Print('Overlay{}1DNLL.png'.format(operator),'png')

        rootFile1.Close()
        rootFile2.Close()

    def BatchLLPlot1D(self, basename='.test', operators=[], log=False):
        if not operators:
            operators = self.operators

        for op in operators:
            self.LLPlot1D(basename+'.'+op, op, log)

    def BatchOverlayLLPlot1D(self, basename1='.EFT.SM.Float', basename2='.EFT.SM.Freeze', operators=[], log=False):
        if not operators:
            operators = self.operators

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
        hname = '{}{}less{}'.format(operators[0],operators[1],ceiling)
        if log:
            hname += "_log"
        limitTree.Draw('2*deltaNLL:{}:{}>>{}(50,-5,5)'.format(operators[0],operators[1],hname), '2*deltaNLL<{}'.format(ceiling), 'prof colz')
        hist = canvas.GetPrimitive(hname)

        # Draw best fit point from grid scan
        #limit.Draw(operators[0]+":"+operators[1],'quantileExpected==-1','p same') # Best fit point from grid scan
        #best_fit = canvas.FindObject('Graph')
        #best_fit.SetMarkerSize(1)
        #best_fit.SetMarkerStyle(34)
        #best_fit.Draw("p same")

        # Change plot formats
        hist.GetXaxis().SetRangeUser(-5.,5.)
        hist.GetYaxis().SetRangeUser(-4.95,4.95)
        if log:
            canvas.SetLogz()

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

        bestDeltaNLL = 1000000
        canvas = ROOT.TCanvas()

        # Get Grid scan and copy to h_contour
        gridFile = ROOT.TFile.Open('../fit_files/higgsCombine{}.MultiDimFit.root'.format(name))
        gridTree = gridFile.Get('limit')
        gridTree.Draw('2*deltaNLL:{}:{}>>grid(50,-5,5,50,-5,5)'.format(operators[0],operators[1]), '2*deltaNLL<100', 'prof colz')
        original = ROOT.TProfile2D(canvas.GetPrimitive('grid'))
        h_contour = ROOT.TProfile2D()
        original.Copy(h_contour)

        # Find bin with bestDeltaNLL
        for entry in range(gridTree.GetEntries()):
            gridTree.GetEntry(entry)
            if bestDeltaNLL > 2*gridTree.GetLeaf('deltaNLL').GetValue(0):
                bestDeltaNLL = 2*gridTree.GetLeaf('deltaNLL').GetValue(0)

        # Adjust scale so that the smallest bin is 0
        for bin in range(original.GetSize()):
            if original.GetBinContent(bin)!=0:
                h_contour.SetBinEntries(bin,1)
                h_contour.SetBinContent(bin,original.GetBinContent(bin)-bestDeltaNLL)

        # Exclude data outside of the contours
        h_contour.SetMaximum(11.83)

        # Set contours
        colors = numpy.array([ROOT.kYellow,ROOT.kCyan-2,ROOT.kBlue-2,ROOT.kWhite], dtype='int32')
        ROOT.gStyle.SetPalette(4,colors)

        levels = numpy.array([0,2.30,5.99,11.83])
        h_contour.SetContour(4,levels)

        # Change format of plot
        h_contour.SetStats(0)
        h_contour.SetTitle("Significance Contours")
        h_contour.GetYaxis().SetTitle(operators[0])
        h_contour.GetXaxis().SetTitle(operators[1])

        # Draw and save plot
        h_contour.Draw('prof colz')
        canvas.Print('contour.png','png')

        # Save contour to histogram file
        outfile = ROOT.TFile(self.histosFileName,'UPDATE')
        h_contour.Write()
        outfile.Close()

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

        self.CorrelationMatrix(postScanName,False,freeze)
        self.CorrelationMatrix(postScanName,True,freeze)

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
    #plotter.Batch2DPlots('.EFT.SM.Float.ctWctZ','.EFT.SM.Float.ctWctZ','.EFT.SM.Float.postScan')
    #plotter.LLPlot1D('.EFT.SM.Float.ctW','ctW')
    #plotter.OverlayLLPlot1D('.EFT.SM.Float.ctW','.EFT.SM.Freeze.ctW','ctW')
    #plotter.BatchOverlayLLPlot1D()
