import ROOT
import numpy

class ContourHelper(object):

    def __init__(self):
        self.placeholder = True

    def styleMultiGraph(self,tlist,linecolor,linewidth,linestyle):
        for item in range(0,tlist.GetSize()):
            graph = tlist.At(item)
            graph.SetLineColor(linecolor)
            graph.SetLineWidth(linewidth)
            graph.SetLineStyle(linestyle)

    def GetContour(self,hist,level):
        contourlevels = numpy.array(level)
        framed = self.FramePlot(hist)
        framed.Draw('COLZ')
        framed.SetMaximum(level)
        framed.SetContour(1,contourlevels)
        framed.Draw('CONT Z LIST')
        ROOT.gPad.Update()

        conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours")

        ret = ROOT.TList()
        if conts.GetSize() > 1:
            print "Woah, multiple contours!"
       
        contLevel = conts.At(0)
        for idy in range(0,contLevel.GetSize()):
            gr1=contLevel.At(idy)
            if(gr1.GetN() > 50):
                ret.Add(gr1.Clone())

        return ret

    def FramePlot(self, hist):

        # Find settings of contour bins
        x0 = hist.GetXaxis().GetXmin()
        x1 = hist.GetXaxis().GetXmax()
        xw = hist.GetXaxis().GetBinWidth(1)
        nx = hist.GetNbinsX()
        y0 = hist.GetYaxis().GetXmin()
        y1 = hist.GetYaxis().GetXmax()
        yw = hist.GetYaxis().GetBinWidth(1)
        ny = hist.GetNbinsY()

        xbins = []
        ybins = []
        eps = 0.1

        # Build new set of bins with 2 extra sets bins around the outside
        xbins.append(x0-1*xw-eps*xw)
        xbins.append(x0-1*xw+eps*xw)
        for xbin in range(2,nx+3):
            xbins.append(x0 + (xbin-2)*xw)
        xbins.append(x1+0.5*xw-eps*xw)
        xbins.append(x1+xw+eps*xw)

        ybins.append(y0-(1+eps)*yw)
        ybins.append(y0-(1-eps)*yw)
        for ybin in range(2,ny+3):
            ybins.append(y0 + (ybin-2)*yw)
        ybins.append(y1+0.5*yw-eps*yw)
        ybins.append(y1+yw+eps*yw)

        # Initialize new hist
        framed = ROOT.TH2D(hist.GetName()+" framed",hist.GetTitle()+" framed",nx+4,numpy.array(xbins),ny+4,numpy.array(ybins))

        # Fill in contour plot data
        for xbin in range(3,nx):
            for ybin in range(3,ny):
                framed.SetBinContent(xbin,ybin,hist.GetBinContent(xbin-2,ybin-2))

        # Set extra bins around the outside to huge values
        for xbin in range(1,nx+5):
            framed.SetBinContent(xbin,1,1000)
            framed.SetBinContent(xbin,ny+4,1000)
        for ybin in range(1,ny+5):
            framed.SetBinContent(1,ybin,1000)
            framed.SetBinContent(nx+4,ybin,1000)
        for xbin in range(2,nx+4):
            framed.SetBinContent(xbin,2,1000)
            framed.SetBinContent(xbin,ny+3,1000)
        for ybin in range(2,ny+4):
            framed.SetBinContent(2,ybin,1000)
            framed.SetBinContent(nx+3,ybin,1000)

        return framed
