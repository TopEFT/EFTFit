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
        #self.operators = ['ctW','ctZ'] # Operators to fit for
        #self.operators = ['ctW','ctZ','ctG','cQe1'] # Operators to fit for
        self.operators = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'] # Hardcoded currently...
        self.op_ranges = {  'ctW':(-6,6),   'ctZ':(-7,7),
                            'cpt':(-40,30), 'ctp':(-35,65),
                            'ctli':(-20,20),'ctlSi':(-10,10),
                            'cQl3i':(-20,20),'cptb':(-5,5),
                            'ctG':(-3,3),   'cpQM':(-30,50),  
                            'ctlTi':(-1,1),'ctei':(-20,20),
                            'cQei':(-12,12),'cQlMi':(-17,17),
                            'cpQ3':(-18,12),'cbW':(-2.6,2.6)
                         }
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
        self.procbins.extend(fits.keys())
        if len(operators_override)>0: self.operators = np.intersect1d(self.operators,operators_override)
        if len(procbin_override)>0: self.procbins = np.intersect1d(self.procbins,procbins_override)
        


    def setup(self):
        print "Setting up fits"
        fits = np.load(self.fits)[()]
        for procbin in self.procbins:
            #self.modelBuilder.out.var(procbin)
            name = 'r_{0}_{1}'.format(procbin[0],procbin[1])
            procbin_name = '_'.join(procbin)

            if not self.modelBuilder.out.function(name):
                # Initialize function pieces
                constant = '{}'.format(fits[procbin][('sm','sm')]) # constant term (should be 1)
                lin_name = procbin_name+"_L" # Name of linear function
                lin_term = [] # Linear term
                lin_args = [] # List of operators in linear term
                quartic_names = [procbin_name+"_Q"+str(idx) for idx,op in enumerate(self.operators)] # Names of quadratic functions
                quartic_terms = [[] for op in self.operators] # Quartic terms, but split into chunks
                quartic_args = [[] for op in self.operators] # List of operators in quartic terms
                fit_terms = [constant] # List of fit terms

                # Fill function pieces
                for idx,op1 in enumerate(self.operators):
                    if abs(fits[procbin][('sm',op1)]) >= 0.001:
                        lin_term.append('{0}*{1}'.format(round(fits[procbin][('sm',op1)],4),op1))
                        lin_args.append(op1)
                    for idy,op2 in enumerate(self.operators):
                        if (idy >= idx) and (abs(fits[procbin][(op1,op2)]) >= 0.001):
                            quartic_terms[idx].append('{0}*{1}*{2}'.format(round(fits[procbin][(op1,op2)],4),op1,op2))
                            quartic_args[idx].extend([op1,op2])
                #if procbin[1]=='C_2lss_m_emu_2b_5j': print lin_term, quartic_terms

                # Compile linear function for combine
                if lin_term:
                    lin_expr = "expr::{lin_name}('{lin_term}',{lin_args})".format(lin_name=lin_name,lin_term="+".join(lin_term),lin_args=",".join(lin_args))
                    lin_func = self.modelBuilder.factory_(lin_expr)
                    self.modelBuilder.out._import(lin_func)
                    fit_terms.append(lin_name)

                # Compile quartic functions separately first
                for idx,fn in enumerate(quartic_terms):
                    if not fn: continue # Skip empty quartic functions
                    quartic_expr = "expr::{quartic_names}('{quartic_terms}',{quartic_args})".format(quartic_names=quartic_names[idx],quartic_terms="+".join(fn),quartic_args=",".join(list(set(quartic_args[idx]))))
                    quartic_func = self.modelBuilder.factory_(quartic_expr)
                    self.modelBuilder.out._import(quartic_func)
                    fit_terms.append(quartic_names[idx])

                # Compile the full function
                fit_function = "expr::{name}('{fit_terms}',{fit_args})".format(name=name,fit_terms="+".join(fit_terms),fit_args=",".join(fit_terms[1:]))
                quadratic = self.modelBuilder.factory_(fit_function)

                # Export fit function
                self.modelBuilder.out._import(quadratic)
                
            #print self.coefficient,"= 0",procbin,a0
            #print self.coefficient,"= 1",procbin,a0+a1+a2
        #pprint.pprint(table,indent=1,width=100)
            

    def doParametersOfInterest(self):
        # user can call combine with `--setPhysicsModelParameterRanges` to set to sensible ranges
        for op in self.operators:
            self.modelBuilder.doVar('{0}[0, {1}, {2}]'.format(op,self.op_ranges[op][0],self.op_ranges[op][1]))
        print "Operators to fit for: "+",".join(self.operators)
        self.modelBuilder.doSet('POI', ','.join(self.operators))
        #self.modelBuilder.doSet('POI', 'ctW,ctZ')
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
