from HiggsAnalysis.CombinedLimit.PhysicsModel import *
from HiggsAnalysis.CombinedLimit.SMHiggsBuilder import SMHiggsBuilder
import ROOT, os
import json 

#
# See derivation and explanation, validation, tests in AN-20-204
#


class AnaliticAnomalousCouplingEFTNegative(PhysicsModel):

    "Float independently cross sections and branching ratios"
    def __init__(self):
        PhysicsModel.__init__(self)
        self.mHRange = []
        self.poiNames = []
        self.alternative = False
        self.verbose = False
        self.numOperators = {}
        self.Operators = {}
        self.sgnl_known = ['ttH','tllq','ttll','ttlnu','tHq','tttt']

        # regular expressions for process names:
        self.sm_re    = re.compile('(?P<proc>.*)_sm')
        self.lin_re   = re.compile('(?P<proc>.*)_lin_(?P<c1>.*)')
        self.quad_re  = re.compile('(?P<proc>.*)_quad_(?P<c1>.*)')
        self.mixed_re = re.compile('(?P<proc>.*)_quad_mixed_(?P<c1>.*)_(?P<c2>.*)') # should go before quad


    def loadOperators(self,fpath):
        print("Loading operators from {fpath}".format(fpath=fpath))
        jsn = open(fpath,'r').read()
        operators = json.loads(jsn)
        self.alloperators = []
        for sig in self.sgnl_known:
            self.Operators[sig] = operators[sig]
            self.numOperators[sig] = len(operators[sig])
            self.alloperators.extend(operators[sig])
        self.alloperators = list(set(self.alloperators))
        print("Operators: {ops}".format(ops=self.Operators))


    def setPhysicsOptions(self,physOptions):
        """ Handle any physics options specified by the user."""
        selected_wcs_fpath = os.path.join(os.environ['CMSSW_BASE'],'src/EFTFit/Fitter/hist_files/selectedWCs.txt')  # Default
        for po in physOptions:
            if po.startswith("eftAlternative"):
                self.alternative = True
                raise RuntimeError("Alternative not yet implemented")
            if po.startswith("selectedWCs="):
                selected_wcs_fpath = po.replace("selectedWCs=","").strip()
            if po.startswith("verbose"):
                self.verbose = True
        self.loadOperators(selected_wcs_fpath) 


    def doParametersOfInterest(self):
        """ Create POI and other parameters, and define the POI set."""
        self.modelBuilder.doVar("r[1,-10,10]")
        self.poiNames = "r"
        self.quadFactors = []

        for operator in self.alloperators:
            self.modelBuilder.doVar(operator + "[0,-200,200]")
            self.poiNames += "," + operator

        # This is the pure SM contribution
        for sig in self.sgnl_known:
            sgnl_ops = self.Operators[sig]
            if self.numOperators[sig] != 1:
                for op in sgnl_ops:
                    op_idx = sgnl_ops.index(op)
                    oplist = sgnl_ops[op_idx:]
                    terms = " ".join(['-@0*@%d'%(i+1) for i,x in enumerate(oplist[1:])])
                    formula = "@0{}".format(terms)
                    expression = "expr::func_{sig}_sm_{op}(\"{formula}\", {oplist})".format(
                        sig=sig,
                        op=op,
                        formula=formula,
                        oplist=','.join(oplist)
                    )
                    if self.verbose:
                        print("SM sub-expr: {}".format(expression))
                    self.modelBuilder.factory_(expression)
                terms = "-@".join(str(i+1) for i,x in enumerate(sgnl_ops))
                formula = "@0*(1-@{})".format(terms)
                functions = ", ".join('func_{sig}_sm_{op}'.format(sig=sig,op=op) for op in self.Operators[sig])
                expression = "expr::func_{sig}_sm(\"{formula}\", 1, {funcs})".format(
                    sig=sig,
                    formula=formula,
                    funcs=functions
                )
                if self.verbose:
                    print("SM expr: {}".format(expression))
                self.modelBuilder.factory_(expression)
            else:
                formula = "@0*(1-(@1))"
                expression = "expr::func_{sig}_sm(\"{formula}\", 1, {op})".format(
                    sig=sig,
                    formula=formula,
                    op=sgnl_ops[0]
                )
                if self.verbose:
                    print("SM expr: {}".format(expression))
                self.modelBuilder.factory_(expression)

        # This is the coefficient of "SM + Lin_i + Quad_i"
        for sig in self.sgnl_known:
            sgnl_ops = self.Operators[sig]
            if self.numOperators[sig] != 1:
                for i in range(0,self.numOperators[sig]):
                    op = sgnl_ops[i]
                    oplist = [str(sgnl_ops[j]) for j in range(len(sgnl_ops)) if i != j]
                    terms = "+@".join([str(j+2) for j in range(len(sgnl_ops) - 1)])
                    formula = "@0*(@1 * (1-(@{terms})))".format(terms=terms)
                    expression = "expr::func_{sig}_sm_linear_quadratic_{op}(\"{formula}\", 1,{op}, {oplist})".format(
                        sig=sig,
                        op=op,
                        formula=formula,
                        oplist=", ".join(oplist)
                    )
                    if self.verbose:
                        print("SM+L+Q expr: {}".format(expression))
                    self.modelBuilder.factory_(expression)
            else:
                formula = "@0*(@1)"
                expression = "expr::func_{sig}_sm_linear_quadratic_(\"{formula}\", 1, {op})".format(
                    sig=sig,
                    formula=formula,
                    op=sgnl_ops[0]
                )
                if self.verbose:
                    print("SM+L+Q expr: {}".format(expression))
                self.modelBuilder.factory_(expression)

        # Quadratic term in each Wilson coefficient
        # e.g. expr::func_sm_linear_quadratic_cH("@0*(@1 * (1-2*(@2+@3) ))", 1,cH, cG, cGtil)
        for sig in self.sgnl_known:  
            sgnl_ops = self.Operators[sig]
            # This is the coefficient of "Quad_i"
            for i in range(0,self.numOperators[sig]):
                formula = "@0*(@1*@1-@1)"
                expression = "expr::func_{sig}_quadratic_{op}(\"{formula}\", 1, {op})".format(
                    sig=sig,
                    op=sgnl_ops[i],
                    formula=formula
                )
                if self.verbose:
                    print("Quad expr: {}".format(expression))
                self.modelBuilder.factory_(expression)
            # (SM + linear) + quadratic + interference between pairs of Wilson coefficients
            if self.numOperators[sig] != 1:
                for i in range(0, self.numOperators[sig]):
                    for j in range(i+1,self.numOperators[sig]):
                        # This is the coefficient of "SM + Lin_i + Lin_j + Quad_i + Quad_j + 2 * M_ij"
                        func_name = "func_{sig}_sm_linear_quadratic_mixed_{op1}_{op2}".format(
                            sig=sig,
                            op1=sgnl_ops[j],    # Note: This is the order as it was before the code cleanup
                            op2=sgnl_ops[i]
                        )
                        self.quadFactors.append(func_name)
                        formula = "@0*@1*@2"
                        expression = "expr::{name}(\"{formula}\", 1,{op1},{op2})".format(
                            name=func_name,
                            formula=formula,
                            op1=sgnl_ops[i],
                            op2=sgnl_ops[j]
                        )
                        if self.verbose:
                            print("Mixed expr: {}".format(expression))
                        self.modelBuilder.factory_(expression)
        print(" parameters of interest = {}".format(self.poiNames))
        print(" self.numOperators = {}".format(self.numOperators))
        self.modelBuilder.doSet("POI",self.poiNames)


    def getYieldScale(self,bin,process):
        """ Define how the yields change."""
        if any( process.startswith(x) for x in self.sgnl_known):
            if self.sm_re.search(process):
                match = self.sm_re.search(process)
                return "func_{p}_sm".format(p=match.group('proc'))
            elif self.lin_re.search(process): 
                match = self.lin_re.search(process)
                return "func_{p}_sm_linear_quadratic_{c1}".format(p=match.group('proc'),c1=match.group('c1'))
            elif self.mixed_re.search(process):
                match = self.mixed_re.search(process)
                c1 = match.group('c1')
                c2 = match.group('c2')
                proc = match.group('proc')
                name = "func_{p}_sm_linear_quadratic_mixed_{c1}_{c2}".format(p=proc,c1=c1,c2=c2)
                if name in self.quadFactors:
                    return "func_{p}_sm_linear_quadratic_mixed_{c1}_{c2}".format(p=proc,c1=c1,c2=c2)
                else:
                    return "func_{p}_sm_linear_quadratic_mixed_{c2}_{c1}".format(p=proc,c1=c1,c2=c2)
            elif self.quad_re.search(process):
                match = self.quad_re.search(process)
                c1 = match.group('c1')
                proc = match.group('proc')
                return "func_{p}_quadratic_{c1}".format(p=proc,c1=c1)
            else:
                #raise RuntimeError("Undefined process %s"%process)
                print("Undefined process {}, probably below threshold and ignored".format(process))
        else:
            print("Process {} not a signal".format(process))
            return 1

#
#  Standard inputs:
# 
#     S
#     S + Li + Qi
#     Qi
#     S + Li + Lj + Qi + Qj + 2*Mij
#    
#
#
#  Alternative (triggered by eftAlternative):
#
#     S
#     S + Li + Qi
#     Qi
#     Qi + Qj + 2*Mij
#    
#  


analiticAnomalousCouplingEFTNegative = AnaliticAnomalousCouplingEFTNegative()
