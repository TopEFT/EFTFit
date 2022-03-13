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
        self.numOperators={}
        self.Operators={}
        jsons=open(os.environ['CMSSW_BASE']+'/src/EFTFit/Fitter/hist_files/selectedWCs.txt','r').read()

        operators=json.loads(jsons)
        self.sgnl_known = ['ttH','tllq','ttll','ttlnu','tHq','tttt']
        self.alloperators=[]
        for sig in self.sgnl_known:
            self.Operators[sig] = operators[sig]
            self.numOperators[sig]=len(operators[sig])
            self.alloperators.extend(operators[sig])
        self.alloperators=list(set(self.alloperators))
        print(self.Operators)
        

        # regular expressions for process names:
        self.sm_re    = re.compile('(?P<proc>.*)_sm')
        self.lin_re   = re.compile('(?P<proc>.*)_lin_(?P<c1>.*)')
        self.quad_re  = re.compile('(?P<proc>.*)_quad_(?P<c1>.*)')
        self.mixed_re = re.compile('(?P<proc>.*)_quad_mixed_(?P<c1>.*)_(?P<c2>.*)') # should go before quad


    def setPhysicsOptions(self,physOptions):
        for po in physOptions:


            if po.startswith("eftAlternative"):
                self.alternative = True
                raise RuntimeError("Alternative not yet implemented")


#
# Define parameters of interest
#

    def doParametersOfInterest(self):
        """Create POI and other parameters, and define the POI set."""

        self.modelBuilder.doVar("r[1,-10,10]")
        self.poiNames = "r"

        self.quadFactors=[]

        for operator in self.alloperators:
          self.modelBuilder.doVar(operator + "[0,-200,200]")
          self.poiNames += "," + operator



        for sig in self.sgnl_known:  
            if self.numOperators[sig] != 1:
                
              for op in self.Operators[sig]:
                  oplist=self.Operators[sig][self.Operators[sig].index( op ):]
                  formula='@0' + ' '.join([ '-@0*@%d'%(i+1) for i in range(len(oplist[1:]))])
            
                  self.modelBuilder.factory_(
                      "expr::func_{sig}_sm_{op}(\"{formula}\", {oplist})".format( sig=sig, op = op, formula=formula, oplist=','.join(oplist))
                  )

              self.modelBuilder.factory_(
                  "expr::func_%s_sm(\"@0*(1-@%s)\", 1, %s)"%(sig,'-@'.join(str(i+1) for i in range(len(self.Operators[sig]))), 
                                                             ", ".join('func_%s_sm_'%(sig)+op for op in self.Operators[sig]))
              )
              
            
            else :
              self.modelBuilder.factory_(
                   "expr::func_%s_sm(\"@0*(1-("%(sig) +
                                            "@1" +
                                            "))\", 1," + "" + str(self.Operators[sig][0]) + ")"
                   )



        #
        # this is the coefficient of "SM + Lin_i + Quad_i"
        #

        for sig in self.sgnl_known:  
            if self.numOperators[sig] != 1:
                for operator in range(0, self.numOperators[sig]):
                    
                    self.modelBuilder.factory_(
                        "expr::func_%s_sm_linear_quadratic_"%sig + str(self.Operators[sig][operator]) +
                        "(\"@0*(" +
                        "@1 * (1-(" + "@" + "+@".join( [str(j+2) for j in range(len(self.Operators[sig]) -1) ] ) + ") )" +
                        ")\", 1," + str(self.Operators[sig][operator]) +
                        ", " + ", ".join( [str(self.Operators[sig][j]) for j in range(len(self.Operators[sig])) if operator!=j ] ) +
                        ")"
                    )
            else :
            
              self.modelBuilder.factory_(
                      "expr::func_%s_sm_linear_quadratic_"%sig + str(self.Operators[sig][0]) +
                                 "(\"@0*(" +
                                 "@1" +
                                 ")\", 1," + str(self.Operators[sig][0]) +
                                 ")"
                      )

          
        #
        # quadratic term in each Wilson coefficient
        #
        #
        # e.g. expr::func_sm_linear_quadratic_cH("@0*(@1 * (1-2*(@2+@3) ))", 1,cH, cG, cGtil)
        #
        for sig in self.sgnl_known:  

          for operator in range(0, self.numOperators[sig]):
          
            #
            # this is the coefficient of "Quad_i"
            #
            
              self.modelBuilder.factory_("expr::func_%s_quadratic_"%sig+ str(self.Operators[sig][operator]) + "(\"@0*(@1*@1-@1)\", 1," + str(self.Operators[sig][operator]) + ")")
          
          
                                          
          
          
          
          #
          # (SM + linear) + quadratic + interference between pairs of Wilson coefficients
          #
          
          if self.numOperators[sig] != 1:
            for operator in range(0, self.numOperators[sig]):
              for operator_sub in range(operator+1, self.numOperators[sig]):
                #
                # this is the coefficient of "SM + Lin_i + Lin_j + Quad_i + Quad_j + 2 * M_ij"
                #
                #print "expr::func_sm_linear_quadratic_mixed_" + str(self.Operators[operator_sub]) + "_" + str(self.Operators[operator]) +          \
                #"(\"@0*@1*@2\", 1," + str(self.Operators[operator]) + "," + str(self.Operators[operator_sub]) +                      \
                #")"
                self.quadFactors.append("func_%s_sm_linear_quadratic_mixed_"%(sig) + str(self.Operators[sig][operator_sub]) + "_" + str(self.Operators[sig][operator]))
                self.modelBuilder.factory_(
                        "expr::func_%s_sm_linear_quadratic_mixed_"%(sig) + str(self.Operators[sig][operator_sub]) + "_" + str(self.Operators[sig][operator]) +
                        "(\"@0*@1*@2\", 1," + str(self.Operators[sig][operator]) + "," + str(self.Operators[sig][operator_sub]) +
                        ")")
          
          


        print " parameters of interest = ", self.poiNames
        print " self.numOperators = ", self.numOperators
        
        self.modelBuilder.doSet("POI",self.poiNames)





#
# Define how the yields change
#


    def getYieldScale(self,bin,process):

        if any( process.startswith(x) for x in self.sgnl_known):
            if self.sm_re.search(process):
                match=self.sm_re.search(process)
                return "func_%s_sm"%(match.group('proc'))
            elif self.lin_re.search(process): 
                match=self.lin_re.search(process)
                return "func_%s_sm_linear_quadratic_"%(match.group('proc'))+ match.group('c1')
            elif self.mixed_re.search(process):
                match=self.mixed_re.search(process)
                c1=match.group('c1')
                c2=match.group('c2')
                proc=match.group('proc')
                if "func_%s_sm_linear_quadratic_mixed_"%(proc) + c1 + "_" + c2 in self.quadFactors:
                    return "func_%s_sm_linear_quadratic_mixed_"%(proc) + c1 + "_" + c2
                else:
                    return "func_%s_sm_linear_quadratic_mixed_"%(proc) + c2 + "_" + c1
                
            elif  self.quad_re.search(process):
                match=self.quad_re.search(process)
                proc=match.group('proc')
                c1=match.group('c1')
                return "func_%s_quadratic_"%(proc)+c1
            else:
                #raise RuntimeError("Undefined process %s"%process)
                print("Undefined process %s, probably below threshold and ignored"%process)

        else:
            print 'Process %s not a signal'%process
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
