import numpy as np
import ROOT
import pprint
ROOT.gSystem.Load('$CMSSW_BASE/src/EFTFit/Fitter/interface/TH1EFT_h.so')


from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel
#Based on 'Quadratic' model from HiggsAnalysis.CombinedLimit.QuadraticScaling

class EFT1DModel(PhysicsModel):
    """Apply process scaling due to EFT operators.

    This class takes a dictionary of quadratic fits describing how processes are
    scaled as a function of an EFT operator's Wilson operator and adds it to
    the workspace. For an example operator x, dictionary values should have
    the form `(a, b, c)` where `xsec_NP(x) / xsec_SM = a + bx + cx^2`.

    To produce an example dictionary, for operator `cuW`:
    >>> import numpy as np
    >>> scales = {'cuW': {'ttZ': (1, 0.322778, 653.371), 'ttW': (1, 1.20998, 205.528)}}
    >>> np.save('scales.npy', scales)

    Example for running:
    text2workspace.py ttV.txt -P HiggsAnalysis.CombinedLimit.EFT:quad --PO scaling=scales.npy --PO process=ttZ --PO process=ttW --PO operator=cuW -o cuW.root
    combine -M MultiDimFit cuW.root --setParameterRanges=-4,4
    """

    def setPhysicsOptions(self, options):
        self.fits = None # File containing WC parameterizations of each process+bin *with events*!
        self.operator = None # operator to fit for
        self.procbins = [] # Process+bin combinations (tuple) that we have events for
        procbin_override = [] # Process+bin combinations (tuple) specified by arguments

        for option, value in [x.split('=') for x in options]:
            if option == 'fits':
                self.fits = value
            elif option == 'operator':
                if self.operator is not None:
                    raise NotImplementedError("Only one operator currently supported")
                self.operator = value
            elif option == 'procbins':
                procbin_override = value.split(',')
            else:
                print("Unknown option",option)

        #If procbins are specified, only use subset that we have fits for.
        #Otherwise, use all of the process+bin combinations that we have fits for.
        fits = np.load(self.fits)[()]
        self.procbins = list(fits[self.operator].keys())
        if len(procbin_override)>0: self.procbins = np.intersect1d(self.procbins,procbins_override)


    def setup(self):
        print("Setting up fits")
        fits = np.load(self.fits)[()]
        #print fits
        #print self.operator
        #table = {}
        for procbin in self.procbins:
            #self.modelBuilder.out.var(procbin)
            name = 'r_{0}_{1}'.format(procbin[0],procbin[1])
            if not self.modelBuilder.out.function(name):
                template = "expr::{name}('{a0}+{a1}*{c}+{a2}*{c}*{c}',{c})"
                a0, a1, a2 = fits[self.operator][procbin]
                print(template.format(name=name, a0=a0, a1=a1, a2=a2, c=self.operator))
                quadratic = self.modelBuilder.factory_(template.format(name=name, a0=a0, a1=a1, a2=a2, c=self.operator))
                #print 'Quadratic:',template.format(name=name, a0=a0, a1=a1, a2=a2, c=self.operator)
                self.modelBuilder.out._import(quadratic)
            #if a0>0:
                #categories = ["C_2lss_p_ee_1b_4j","C_2lss_p_ee_1b_5j","C_2lss_p_ee_1b_6j","C_2lss_p_ee_1b_7j","C_3l_ppp_1b_2j","C_3l_ppp_1b_3j","C_3l_ppp_1b_4j","C_3l_ppp_1b_5j","C_3l_ppp_1b_6j","C_3l_ppp_1b_7j","C_3l_ppp_1b_8j"]
                #if procbin[1] in categories: table[procbin] = (a0,round((a0+a1+a2)/a0,8))
            #print self.operator,"= 0",procbin,a0
            #print self.operator,"= 1",procbin,a0+a1+a2
        #pprint.pprint(table,indent=1,width=100)
            

    def doParametersOfInterest(self):
        # user should call combine with `--setPhysicsModelParameterRanges` set to sensible ranges
        self.modelBuilder.doVar('{0}[0, -inf, inf]'.format(self.operator))
        self.modelBuilder.doSet('POI', self.operator)
        self.setup()

    def getYieldScale(self, bin, process):
        if (process,bin) not in self.procbins:
            return 1
        else:
            #print 'scaling {0}, {1}'.format(process, bin)
            fits = np.load(self.fits)[()]
            #print self.operator,process,bin,fits[self.operator][(process,bin)]
            name = 'r_{0}_{1}'.format(process,bin)
            return name


eft1D = EFT1DModel()
