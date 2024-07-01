import numpy as np
import ROOT
import pprint
ROOT.gSystem.Load('$CMSSW_BASE/src/EFTFit/Fitter/interface/TH1EFT_h.so')


from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel
#Based on 'Quadratic' model from HiggsAnalysis.CombinedLimit.QuadraticScaling

class EFTModel(PhysicsModel):
    """Apply process scaling due to EFT Wilson Coefficients (WCs).

    This class takes a dictionary of quadratic fits describing how processes are
    scaled as a function of an EFT operator's Wilson coefficient and adds it to
    the workspace. For an example coefficient x, dictionary values should have
    the form `(a, b, c)` where `xsec_NP(x) / xsec_SM = a + bx + cx^2`.

    To produce an example dictionary, for coefficient `ctW`:
    >>> import numpy as np
    >>> scales = {('ttZ','C_2lss_m_2b_4j'): {(ctW,ctW): 653.371, (ctW,sm): 0.322778, (sm,sm): 1.0}}
    >>> np.save('scales.npy', scales)

    Oversimplified example for running with override options:
    text2workspace.py EFT_MultiDim_Datacard.txt -P EFTFit.Fitter.EFTModel:eftmodel --PO fits=EFT_Parameterization.npy --PI wcs=ctW,ctZ -o 16D.root
    combine -M MultiDimFit 16D.root
    """

    def setPhysicsOptions(self, options):
        self.fits = None # File containing WC parameterizations of each process+bin *with events*!
        self.linear_only = False    # Physics Option flag to determine if the quadratic terms should be dropped from the workspace
        self.wcs = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi'] # Hardcoded currently...
        self.wc_ranges = {  'ctW':(-6,6),    'ctZ':(-7,7),
                            'cpt':(-40,30),  'ctp':(-35,65),
                            'ctli':(-20,20), 'ctlSi':(-22,22),
                            'cQl3i':(-20,20),'cptb':(-40,40),
                            'ctG':(-3,3),    'cpQM':(-30,50),
                            'ctlTi':(-4,4),  'ctei':(-20,20),
                            'cQei':(-16,16), 'cQlMi':(-17,17),
                            'cpQ3':(-20,12), 'cbW':(-10,10)
                        }
        wcs_override = [] # WCs specified by arguments
        self.procbins = [] # Process+bin combinations (tuple) that we have events for
        procbin_override = [] # Process+bin combinations (tuple) specified by arguments

        for option, value in [x.split('=') for x in options]:
            if option == 'fits': # .npy fit file created with FitConversion16D.py
                self.fits = value
            elif option == 'wcs': # Override to fit only a subset of WCs
                wcs_override = value.split(',')
            elif option == 'procbins': # Override to fit only a subset of proc+category combinations
                procbin_override = value.split(',')
            elif option == 'linear-only':
                self.linear_only = True
                # Alternate ranges for linear-term only parameterizations
                self.wc_ranges = {
                    'cQei':  ( -999, 999),
                    'cQl3i': ( -300, 300),
                    'cQlMi': (-9999, 999),
                    'cbW':   ( -999, 999),
                    'cpQ3':  (  -99,  99),
                    'cpQM':  (-9999, 999),
                    'cpt':   (-9999, 999),
                    'cptb':  (-9999,9999),
                    'ctG':   ( -999,  99),
                    'ctW':   (  -99,  99),
                    'ctZ':   (  -99,  99),
                    'ctei':  (-9999, 300),
                    'ctlTi': (-9999,9999),
                    'ctlSi': (  -22,  22),
                    'ctli':  ( -999, 999),
                    'ctp':   (-9999,  99),
                }
            else:
                print("Unknown option",option)

        #If procbins are specified, only use subset that we have fits for.
        #Otherwise, use all of the process+bin combinations that we have fits for.
        fits = np.load(self.fits)[()]
        self.procbins.extend(list(fits.keys()))
        if len(wcs_override)>0: self.wcs = np.intersect1d(self.wcs,wcs_override)
        if len(procbin_override)>0: self.procbins = np.intersect1d(self.procbins,procbins_override)

    def setup(self):
        print("Setting up fits")
        fits = np.load(self.fits)[()]
        for i,procbin in enumerate(sorted(self.procbins)):
            #self.modelBuilder.out.var(procbin)
            name = 'r_{proc}_{cat}'.format(proc=procbin[0],cat=procbin[1])
            procbin_name = '_'.join(procbin)

            if not self.modelBuilder.out.function(name):
                # Initialize function pieces
                constant = '{}'.format(fits[procbin][('sm','sm')]) # constant term (should be 1)
                lin_name = procbin_name+"_L" # Name of linear function
                lin_term = [] # Linear term
                lin_args = [] # List of wcs in linear term
                quartic_names = [procbin_name+"_Q"+str(idx) for idx,wc in enumerate(self.wcs)] # Names of quadratic functions
                quartic_terms = [[] for wc in self.wcs] # Quartic terms, but split into chunks
                quartic_args = [[] for wc in self.wcs] # List of wcs in quartic terms
                fit_terms = [constant] # List of fit terms

                # Fill function pieces
                for idx,wc1 in enumerate(self.wcs):
                    if abs(fits[procbin][('sm',wc1)]) >= 0.001:
                        if fits[procbin][('sm',wc1)] < 0.0:
                            lin_term.append('({0})*{1}'.format(round(fits[procbin][('sm',wc1)],4),wc1))
                        else:
                            lin_term.append('{0}*{1}'.format(round(fits[procbin][('sm',wc1)],4),wc1))
                        lin_args.append(wc1)
                    for idy,wc2 in enumerate(self.wcs):
                        if self.linear_only: continue
                        if (idy >= idx) and (abs(fits[procbin][(wc1,wc2)]) >= 0.001):
                            quartic_terms[idx].append('{0}*{1}*{2}'.format(round(fits[procbin][(wc1,wc2)],4),wc1,wc2))
                            quartic_args[idx].extend([wc1,wc2])
                # Compile linear function for combine
                if lin_term:
                    lin_expr = "expr::{lin_name}('{lin_term}',{lin_args})".format(lin_name=lin_name,lin_term="+".join(lin_term),lin_args=",".join(lin_args))
                    lin_func = self.modelBuilder.factory_(lin_expr)
                    self.modelBuilder.out._import(lin_func)
                    fit_terms.append(lin_name)
                # Compile quartic functions separately first
                for idx,fn in enumerate(quartic_terms):
                    if not fn: continue # Skip empty quartic functions
                    quartic_expr = "expr::{quartic_names}('{quartic_terms}',{quartic_args})".format(quartic_names=quartic_names[idx], quartic_terms="+".join(fn), quartic_args=",".join(list(set(quartic_args[idx]))))
                    quartic_func = self.modelBuilder.factory_(quartic_expr)
                    self.modelBuilder.out._import(quartic_func)
                    fit_terms.append(quartic_names[idx])
                # Compile the full function
                fit_function = "expr::{name}('{fit_terms}',{fit_args})".format(name=name,fit_terms="+".join(fit_terms),fit_args=",".join(fit_terms[1:]))
                quadratic = self.modelBuilder.factory_(fit_function)

                # Export fit function
                self.modelBuilder.out._import(quadratic)

    def doParametersOfInterest(self):
        # user can call combine with `--setPhysicsModelParameterRanges` to set to sensible ranges
        for wc in self.wcs:
            self.modelBuilder.doVar('{0}[0, {1}, {2}]'.format(wc,self.wc_ranges[wc][0],self.wc_ranges[wc][1]))
        print("WCs to fit for: "+",".join(self.wcs))
        self.modelBuilder.doSet('POI', ','.join(self.wcs))
        self.setup()

    def getYieldScale(self, bin, process):
        if (process,bin) not in self.procbins:
            return 1
        else:
            name = 'r_{0}_{1}'.format(process,bin)
            return name

eftmodel = EFTModel()
