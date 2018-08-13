import numpy as np
import ROOT
import pprint
ROOT.gSystem.Load('$CMSSW_BASE/src/EFTFit/Fitter/interface/TH1EFT_h.so')


from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel
#Based on 'Quadratic' model from HiggsAnalysis.CombinedLimit.QuadraticScaling

class EFT16DModel(PhysicsModel):
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
        #self.operators = [] # Operators to fit for
        self.operators = ['cptb','cpt','ctlT1','cpQ3','cpQM','ctG','cbW','cQl31','ctl1','ctp','ctlS1','ctZ','cQe1','cQlM1','cte1','ctW'] # Hardcoded currently...
        operators_override = [] # Operators specified by arguments
        self.procbins = [] # Process+bin combinations (tuple) that we have events for
        procbin_override = [] # Process+bin combinations (tuple) specified by arguments

        for option, value in [x.split('=') for x in options]:
            if option == 'fits':
                self.fits = value
            elif option == 'operators':
                operators_override = value.split(',')
            elif option == 'procbins':
                procbin_override = value.split(',')
            else:
                print "Unknown option",option

        #If procbins are specified, only use subset that we have fits for.
        #Otherwise, use all of the process+bin combinations that we have fits for.
        fits = np.load(self.fits)[()]
        #self.operators.extend(fits[0].keys()) # This could lead to problems if not all operators are in every procbin
        self.procbins.extend(fits.keys())
        if len(operators_override)>0: self.operators = np.intersect1d(self.operators,operators_override)
        if len(procbin_override)>0: self.procbins = np.intersect1d(self.procbins,procbins_override)
        


    def setup(self):
        print "Setting up fits"
        fits = np.load(self.fits)[()]
        for procbin in self.procbins:
            #self.modelBuilder.out.var(procbin)
            name = 'r_{0}_{1}'.format(procbin[0],procbin[1])

            if not self.modelBuilder.out.function(name):
                constant = '{}'.format(fits[procbin][('sm','sm')])
                linear = ''
                quartic = ''
                op_list = ''
                for idx,op1 in enumerate(self.operators):
                    if abs(fits[procbin][('sm',op1)]) >= 0.001:
                        linear += '+{0}*{1}'.format(round(fits[procbin][('sm',op1)],4),op1)
                    op_list += ',{}'.format(op1)
                    for idy,op2 in enumerate(self.operators):
                        if abs(fits[procbin][(op1,op2)]) >= 0.001:
                            quartic += '+{0}*{1}*{2}'.format(round(fits[procbin][(op1,op2)],4),op1,op2)
                #print len(quartic)
                template = "expr::"+name+"('"+constant+linear+quartic+"'"+op_list+")"
                #print template

                # Export fit function
                quadratic = self.modelBuilder.factory_(template)
                #print 'Quadratic:',template.format(name=name, a0=a0, a1=a1, a2=a2, c=self.coefficient)
                self.modelBuilder.out._import(quadratic)

                # Factory method
                #print "Making workspace..."
                #wk = ROOT.RooWorkspace()
                #x = wk.factory('x[5]')
                #y = wk.factory('y[5]')
                #print "Making functions..."
                #testFunc1 = wk.factory("expr::testFunc1('1+x',{x})")
                #testFunc2 = wk.factory("expr::testFunc2('y+x*y',{x,y})")
                #print "Combining functions..."
                #testFunc3 = wk.factory("expr::testFunc3('testFunc1+testFunc2',{testFunc1,testFunc2})")
                #wk.Print('TV')
                #print "Done"
                
            #if a0>0:
                #categories = ["C_2lss_p_ee_1b_4j","C_2lss_p_ee_1b_5j","C_2lss_p_ee_1b_6j","C_2lss_p_ee_1b_7j","C_3l_ppp_1b_2j","C_3l_ppp_1b_3j","C_3l_ppp_1b_4j","C_3l_ppp_1b_5j","C_3l_ppp_1b_6j","C_3l_ppp_1b_7j","C_3l_ppp_1b_8j"]
                #if procbin[1] in categories: table[procbin] = (a0,round((a0+a1+a2)/a0,8))
            #print self.coefficient,"= 0",procbin,a0
            #print self.coefficient,"= 1",procbin,a0+a1+a2
        #pprint.pprint(table,indent=1,width=100)
            

    def doParametersOfInterest(self):
        # user should call combine with `--setPhysicsModelParameterRanges` set to sensible ranges
        for op in self.operators:
            self.modelBuilder.doVar('{0}[0, -inf, inf]'.format(op))
            self.modelBuilder.doSet('POI', op)
        self.setup()

    def getYieldScale(self, bin, process):
        if (process,bin) not in self.procbins:
            return 1
        else:
            #print 'scaling {0}, {1}'.format(process, bin)
            #fits = np.load(self.fits)[()]
            #print self.coefficient,process,bin,fits[self.coefficient][(process,bin)]
            name = 'r_{0}_{1}'.format(process,bin)
            return name


eft16D = EFT16DModel()
