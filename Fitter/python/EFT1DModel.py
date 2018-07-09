import numpy as np
import ROOT
ROOT.gSystem.Load('$CMSSW_BASE/src/EFTFit/Fitter/interface/TH1EFT_h.so')


from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel
#Based on 'Quadratic' model from HiggsAnalysis.CombinedLimit.QuadraticScaling

class EFT1DModel(PhysicsModel):
    """Apply process scaling due to EFT operators.

    This class takes a dictionary of quadratic fits describing how processes are
    scaled as a function of an EFT operator's Wilson coefficient and adds it to
    the workspace. For an example coefficient x, dictionary values should have
    the form `(a, b, c)` where `xsec_NP(x) / xsec_SM = a + bx + cx^2`.

    To produce an example dictionary, for coefficient `cuW`:
    >>> import numpy as np
    >>> scales = {'cuW': {'ttZ': (1, 0.322778, 653.371), 'ttW': (1, 1.20998, 205.528)}}
    >>> np.save('scales.npy', scales)

    Example for running:
    text2workspace.py ttV.txt -P HiggsAnalysis.CombinedLimit.EFT:quad --PO scaling=scales.npy --PO process=ttZ --PO process=ttW --PO coefficient=cuW -o cuW.root
    combine -M MultiDimFit cuW.root --setParameterRanges=-4,4
    """

    def setPhysicsOptions(self, options):
        self.fits = None # File containing WC parameterizations of each process+bin *with events*!
        self.coefficient = None # Coefficient to fit for
        self.procbins = [] # Process+bin combinations (tuple) that we have events for
        procbin_override = [] # Process+bin combinations (tuple) specified by arguments

        for option, value in [x.split('=') for x in options]:
            if option == 'fits':
                self.fits = value
            elif option == 'coefficient':
                if self.coefficient is not None:
                    raise NotImplementedError("Only one coefficient currently supported")
                self.coefficient = value
            elif option == 'procbin':
                procbin_override.append(value)
            else:
                print "Unknown option",option

        #If procbins are specified, only use subset that we have fits for.
        #Otherwise, use all of the process+bin combinations that we have fits for.
        fits = np.load(self.fits)[()]
        if len(procbin_override)>0:
            self.procbins.extend(np.intersect1d(procbins,procbins_override))
        else:
            self.procbins.extend(fits[self.coefficient].keys())


    def setup(self):
        print "Setting up fits"
        fits = np.load(self.fits)[()]
        for procbin in self.procbins:
            #self.modelBuilder.out.var(procbin)
            name = 'r_{0}_{1}'.format(procbin[0],procbin[1])
            if not self.modelBuilder.out.function(name):
                template = "expr::{name}('{a0} + ({a1} * {c}) + ({a2} * {c} * {c})', {c})"
                a0, a1, a2 = fits[self.coefficient][procbin]
                quadratic = self.modelBuilder.factory_(template.format(name=name, a0=a0, a1=a1, a2=a2, c=self.coefficient))
                #print 'Quadratic:',template.format(name=name, a0=a0, a1=a1, a2=a2, c=self.coefficient)
                self.modelBuilder.out._import(quadratic)

    def doParametersOfInterest(self):
        # user should call combine with `--setPhysicsModelParameterRanges` set to sensible ranges
        self.modelBuilder.doVar('{0}[0, -inf, inf]'.format(self.coefficient))
        self.modelBuilder.doSet('POI', self.coefficient)
        self.setup()

    def getYieldScale(self, bin, process):
        if (process,bin) not in self.procbins:
            return 1
        else:
            #print 'scaling {0}, {1}'.format(process, bin)
            fits = np.load(self.fits)[()]
            #print self.coefficient,process,bin,fits[self.coefficient][(process,bin)]
            name = 'r_{0}_{1}'.format(process,bin)

            return name


eft1D = EFT1DModel()
