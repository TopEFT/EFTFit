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
        PhysicsModel.__init__(self) # not using 'super(x,self).__init__' since I don't understand it
        self.mHRange = []
        self.poiNames = []
        self.alternative = False
        self.verbose = False
        self.numOperators = {}
        self.Operators = {}
        self.sgnl_known = ['ttH','tllq','ttll','ttlnu','tHq','tttt','ttA']

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
        wcs_list_exists = False
        for po in physOptions:
            if po.startswith("higgsMassRange="):
                self.mHRange = po.replace("higgsMassRange=","").split(",")
                if len(self.mHRange) != 2:
                    raise RuntimeError("Higgs mass range definition requires two extrema")
                elif float(self.mHRange[0]) >= float(self.mHRange[1]):
                    raise RuntimeError("Extrema for Higgs mass range defined with inverterd order. Second must be larger the first")

            if po.startswith("eftOperators="):
                self.Operators = po.replace("eftOperators=","").split(",")
                print(" Operators = ", self.Operators)
                self.numOperators = len(self.Operators)

            if po.startswith("eftAlternative"):
                self.alternative = True

            #
            # this is needed in the case the complete list of operators is not the one provided above,
            # but for some reason, like a new model or a new basis, different or more operators are added.
            # There could be also the possibility that one operator is removed from the complete list of operators,
            # who knows why ... by it might happen, thus the method to remove it is given hereafter
            #
            if po.startswith("defineOperators="):
                self.Operators = po.replace("defineOperators=","").split(",")
                print(" Operators = ", self.Operators)

            if po.startswith("addToOperators="):
                toAddOperators = po.replace("addToOperators=","").split(",")
                self.Operators.extend ( toAddOperators )
                print(" Operators = ", self.Operators)

            if po.startswith("removeFromOperators="):
                toRemoveOperators = po.replace("removeFromOperators=","").split(",")
                newlist = [i for i in self.Operators if i not in toRemoveOperators]
                self.Operators = newlist
                print(" Operators = ", self.Operators)

            if po.startswith("selectedWCs="):
                selected_wcs_fpath = po.replace("selectedWCs=","").strip()
                wcs_list_exists = True

        assert wcs_list_exists, "selectedWCs.txt not provided. Provide the full path using the command line option `--PO selectedWCs=PATH_TO_DIR`."

        self.loadOperators(selected_wcs_fpath) 


#
# standard, not touched (end)
#


#
# Define parameters of interest
#

    def doParametersOfInterest(self):
        """Create POI and other parameters, and define the POI set."""
        self.modelBuilder.doVar("r[1,-10,10]")
        self.poiNames = "r"
        self.quadFactors = []


        for sig in self.sgnl_known:
            for operator in range(0, self.numOperators[sig]):
              self.modelBuilder.doVar(str(self.Operators[sig][operator]) + "[0,-200,200]")
              self.poiNames += "," + str(self.Operators[sig][operator])

            #
            # model: SM + k*linear + k**2 * quadratic
            #
            #   SM        = Asm**2
            #   linear    = Asm*Absm
            #   quadratic = Absm**2
            #
            #  ... and extended to more operators
            #
            #
            # model: SM + k*linear + k**2 * quadratic
            #
            #   SM        = Asm**2
            #   linear_1        = Asm*Abs_1
            #   linear_2        = Asm*Absm_2
            #   linear_3        = Absm_1*Absm_2
            #   quadratic_1 = Absm_1**2
            #   quadratic_2 = Absm_2**2
            #
            #
            #  Combine limitation/assumption: all histograms are defined positive
            #      See http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part2/physicsmodels/#interference
            #  There will be some algebra here below to deal with it, but it will be transparent for the user
            #  as if it was ...
            #
            #
            # e.g. expr::func_"+sig+"_sm("@0*(1-(@1+@2+@3-@1*@2-@1*@3-@2*@1-@2*@3-@3*@1-@3*@2))",r,cG,cGtil, cG,cH, cGtil,cG, cGtil,cH, cH,cG, cH,cGtil)
            #

            #
            # sm
            #
            # print " Test = "


            #
            # this is the coefficient of "SM"
            #

            if not self.alternative :
              #if self.numOperators != 1:
                  #print "expr::func_"+sig+"_sm(\"@0*(1-(" +                                                                                                                                                                  \
                                 #"@" + "+@".join([str(i+1) for i in range(len(self.Operators[sig]))])  +                                                                                                               \
                                 #"-@" + "-@".join([str(i+1)+"*@"+str(j+1) for i in range(len(self.Operators[sig])) for j in range(len(self.Operators[sig])) if i<j ]) +                                                     \
                                 #"))\",r," + ", ".join([str(self.Operators[sig][i]) for i in range(len(self.Operators[sig]))]) + ")"
              #else:
                #print "expr::func_"+sig+"_sm(\"@0*(1-(" +                                                                     \
                        #"@1" +                                                                                          \
                        #"))\",r," + str(self.Operators[sig][0]) + ")"
              if self.numOperators != 1:
                self.modelBuilder.factory_(
                     "expr::func_"+sig+"_sm(\"@0*(1-(" +
                                              "@" + "+@".join([str(i+1) for i in range(len(self.Operators[sig]))])  +
                                              "-@" + "-@".join([str(i+1)+"*@"+str(j+1) for i in range(len(self.Operators[sig])) for j in range(len(self.Operators[sig])) if i<j ]) +
                                              "))\",r," + ", ".join([str(self.Operators[sig][i]) for i in range(len(self.Operators[sig]))]) + ")"
                     )
              else :
                self.modelBuilder.factory_(
                     "expr::func_"+sig+"_sm(\"@0*(1-(" +
                                              "@1" +
                                              "))\",r," + str(self.Operators[sig][0]) + ")"
                     )
            else :

              #print "expr::func_"+sig+"_sm(\"@0*(1-(" +                                                                                                                                                               \
                             #"@" + "+@".join([str(i+1) for i in range(len(self.Operators[sig]))])  +                                                                                                               \
                             #"))\",r," + ", ".join([str(self.Operators[sig][i]) for i in range(len(self.Operators[sig]))]) + ")"

              if self.numOperators != 1:
                self.modelBuilder.factory_(
                     "expr::func_"+sig+"_sm(\"@0*(1-(" +
                                              "@" + "+@".join([str(i+1) for i in range(len(self.Operators[sig]))])  +
                                              "))\",r," + ", ".join([str(self.Operators[sig][i]) for i in range(len(self.Operators[sig]))]) + ")"
                     )
              else :
                self.modelBuilder.factory_(
                     "expr::func_"+sig+"_sm(\"@0*(1-(" +
                                              "@1" +
                                              "))\",r," + str(self.Operators[sig][0]) + ")"
                     )





            #
            # this is the coefficient of "SM + Lin_i + Quad_i"
            #

            if not self.alternative :
              if self.numOperators != 1:
                for operator in range(0, self.numOperators[sig]):
                  #print " Test = "
                  #print "expr::func_"+sig+"_sm_linear_quadratic_" + str(self.Operators[sig][operator]) +                                           \
                                     #"(\"@0*(" +                                                                                      \
                                     #"@1 * (1-(" + "@" + "+@".join( [str(j+2) for j in range(len(self.Operators[sig]) -1) ] ) + ") )" +      \
                                     #")\",r," + str(self.Operators[sig][operator]) +                                                     \
                                     #", " + ", ".join( [str(self.Operators[sig][j]) for j in range(len(self.Operators[sig])) if operator!=j ] ) +            \
                                     #")"
                  #
                  #
                  # expr::func_"+sig+"_sm_linear_quadratic_cG("@0*(@1 * (1-2*(@2+@3) ))",r,cG, cGtil, cH)
                  #
                  #
                  self.modelBuilder.factory_(
                          "expr::func_"+sig+"_sm_linear_quadratic_" + str(self.Operators[sig][operator]) +
                                     "(\"@0*(" +
                                     "@1 * (1-(" + "@" + "+@".join( [str(j+2) for j in range(len(self.Operators[sig]) -1) ] ) + ") )" +
                                     ")\",r," + str(self.Operators[sig][operator]) +
                                     ", " + ", ".join( [str(self.Operators[sig][j]) for j in range(len(self.Operators[sig])) if operator!=j ] ) +
                                     ")"
                          )
              else :
                #print "expr::func_"+sig+"_sm_linear_quadratic_" + str(self.Operators[sig][operator]) +                   \
                          #"(\"@0*(" +                                                                      \
                          #"@1" +                                                                           \
                          #")\",r," + str(self.Operators[sig][0]) +                                           \
                          #")"
  
                self.modelBuilder.factory_(
                        "expr::func_"+sig+"_sm_linear_quadratic_" + str(self.Operators[sig][operator]) +
                                   "(\"@0*(" +
                                   "@1" +
                                   ")\",r," + str(self.Operators[sig][0]) +
                                   ")"
                        )

            else :
              for operator in range(0, self.numOperators[sig]):
                #print "expr::func_"+sig+"_sm_linear_quadratic_" + str(self.Operators[sig][operator]) +                   \
                          #"(\"@0*(" +                                                                      \
                          #"@1" +                                                                           \
                          #")\",r," + str(self.Operators[sig][operator]) +                                           \
                          #")"

                self.modelBuilder.factory_(
                        "expr::func_"+sig+"_sm_linear_quadratic_" + str(self.Operators[sig][operator]) +
                                    "(\"@0*(" +
                                    "@1" +
                                    ")\",r," + str(self.Operators[sig][operator]) +
                                    ")"
                        )
              
              
            #
            # quadratic term in each Wilson coefficient
            #
            #
            # e.g. expr::func_"+sig+"_sm_linear_quadratic_cH("@0*(@1 * (1-2*(@2+@3) ))",r,cH, cG, cGtil)
            #

            for operator in range(0, self.numOperators[sig]):

              #
              # this is the coefficient of "Quad_i"
              #
              
              if not self.alternative :

                #print "expr::func_"+sig+"_quadratic_"+ str(self.Operators[sig][operator]) + "(\"@0*(@1*@1-@1)\",r," + str(self.Operators[sig][operator]) + ")"

                self.modelBuilder.factory_("expr::func_"+sig+"_quadratic_"+ str(self.Operators[sig][operator]) + "(\"@0*(@1*@1-@1)\",r," + str(self.Operators[sig][operator]) + ")")


              else :

                if self.numOperators != 1:

                  #print "expr::func_"+sig+"_quadratic_"+ str(self.Operators[sig][operator]) +    \
                                            #"(\"@0*(@1*@1-@1-@1*(" + "@" + "+@".join([str(j+1) for j in range(len(self.Operators[sig])) if j != 0 ]) +   \
                                            #"))\",r," +  str(self.Operators[sig][operator]) + ", " + ", ".join([str(self.Operators[sig][i]) for i in range(len(self.Operators[sig])) if i != operator ]) + ")"

                  self.modelBuilder.factory_("expr::func_"+sig+"_quadratic_"+ str(self.Operators[sig][operator]) +      \
                                            "(\"@0*(@1*@1-@1-@1*(" + "@" + "+@".join([str(j+1) for j in range(len(self.Operators[sig])) if j != 0 ]) +   \
                                            "))\",r," +  str(self.Operators[sig][operator]) + ", " + ", ".join([str(self.Operators[sig][i]) for i in range(len(self.Operators[sig])) if i != operator ]) + ")"
                                            )
                                                                                                                                                                                    

                else:

                  #print "expr::func_"+sig+"_quadratic_"+ str(self.Operators[sig][0]) + \
                                            #"(\"@0*(@1*@1-@1" +   \
                                            #")\",r," + str(self.Operators[sig][0]) + ")"

                  self.modelBuilder.factory_("expr::func_"+sig+"_quadratic_"+ str(self.Operators[sig][operator]) +  \
                                            "(\"@0*(@1*@1-@1" +   \
                                            ")\",r," + str(self.Operators[sig][0]) + ")"
                                            )



            #
            # (SM + linear) + quadratic + interference between pairs of Wilson coefficients
            #
            
            if not self.alternative :
              
              if self.numOperators != 1:
                for operator in range(0, self.numOperators[sig]):
                  for operator_sub in range(operator+1, self.numOperators[sig]):

                    #
                    # this is the coefficient of "SM + Lin_i + Lin_j + Quad_i + Quad_j + 2 * M_ij"
                    #
                    #print "expr::func_"+sig+"_sm_linear_quadratic_mixed_" + str(self.Operators[sig][operator_sub]) + "_" + str(self.Operators[sig][operator]) +          \
                    #"(\"@0*@1*@2\",r," + str(self.Operators[sig][operator]) + "," + str(self.Operators[sig][operator_sub]) +                      \
                    #")"

                    self.modelBuilder.factory_(
                            "expr::func_"+sig+"_sm_linear_quadratic_mixed_" + str(self.Operators[sig][operator_sub]) + "_" + str(self.Operators[sig][operator]) +
                            "(\"@0*@1*@2\",r," + str(self.Operators[sig][operator]) + "," + str(self.Operators[sig][operator_sub]) +
                            ")")
                    func_name = "func_{sig}_sm_linear_quadratic_mixed_{op1}_{op2}".format(
                        sig=sig,
                        op1=self.Operators[sig][operator_sub],    # Note: This is the order as it was before the code cleanup
                        op2=self.Operators[sig][operator]
                    )
                    self.quadFactors.append(func_name)
                    if self.verbose:
                        print(func_name)

            else:

              if self.numOperators != 1:
                for operator in range(0, self.numOperators[sig]):
                  for operator_sub in range(operator+1, self.numOperators[sig]):

                    #
                    # this is the coefficient of "Quad_i + Quad_j + 2 * M_ij"
                    #
                    #print "expr::func_"+sig+"_quadratic_mixed_" + str(self.Operators[sig][operator_sub]) + "_" + str(self.Operators[sig][operator]) +          \
                    #"(\"@0*@1*@2\",r," + str(self.Operators[sig][operator]) + "," + str(self.Operators[sig][operator_sub]) +                      \
                    #")"

                    self.modelBuilder.factory_(
                            "expr::func_"+sig+"_quadratic_mixed_" + str(self.Operators[sig][operator_sub]) + "_" + str(self.Operators[sig][operator]) +
                            "(\"@0*@1*@2\",r," + str(self.Operators[sig][operator]) + "," + str(self.Operators[sig][operator_sub]) +
                            ")")
                    func_name = "func_{sig}_sm_linear_quadratic_mixed_{op1}_{op2}".format(
                        sig=sig,
                        op1=self.Operators[sig][operator_sub],    # Note: This is the order as it was before the code cleanup
                        op2=self.Operators[sig][operator]
                    )
                    self.quadFactors.append(func_name)
                    if self.verbose:
                        print(func_name)



        print(" parameters of interest = ", self.poiNames)
        print(" self.numOperators = ", self.numOperators[sig])
        
        self.modelBuilder.doSet("POI",self.poiNames)





#
# Define how the yields change
#


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
