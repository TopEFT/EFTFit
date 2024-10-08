import numpy as np

from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel
#Based on 'Quadratic' model from HiggsAnalysis.CombinedLimit.QuadraticScaling

class EFT2DModel(PhysicsModel):
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
        self.coefficient = []
        self.processes = []
        self.bins = []
        for option, value in [x.split('=') for x in options]:
            if option == 'coefficient': # list of EFT operators to scale
                self.coefficient.append(value)
            if option == 'process':  # processes which will be scaled
                self.processes.append(value)
            if option == 'bin': # bins to be scaled
                self.bins.append(value)
            if option == 'scaling': # file with the fit functions
                self.scaling = value

    def setup(self):
        print("Setting up fits")
        scaling = np.load(self.scaling)[()]
        for process in self.processes:
            #for bin in self.bins:
                self.modelBuilder.out.var(process)
                #name = 'r_{0}_{1}'.format(process, bin)
                name = 'r_{0}'.format(process)
                if not self.modelBuilder.out.function(name):
                    template = "expr::{name}('{a0} + ({a1}*{c1}) + ({a2}*{c1}*{c1})+{b0} + ({b1}*{c2}) + ({b2}*{c2}*{c2})', {c1}, {c2})"
                    a0, a1, a2 = scaling[self.coefficient[0]][process]
                    b0, b1, b2 = scaling[self.coefficient[1]][process]
                    #print('Quadratic:',template.format(name=name, a0=a0, a1=a1, a2=a2, b0=b0, b1=b1, b2=b2 c1=self.coefficient[0],c2=self.coefficient[1]))
                    quadratic = self.modelBuilder.factory_(template.format(name=name, a0=a0, a1=a1, a2=a2, b0=b0, b1=b1, b2=b2, c1=self.coefficient[0], c2=self.coefficient[1]))
                    self.modelBuilder.out._import(quadratic)

    def doParametersOfInterest(self):
        # user should call combine with `--setPhysicsModelParameterRanges` set to sensible ranges
        self.modelBuilder.doVar('{0}[1, -inf, inf]'.format(self.coefficient[0]))
        self.modelBuilder.doVar('{0}[1, -inf, inf]'.format(self.coefficient[1]))
        self.modelBuilder.doSet('POI', '{0},{1}'.format(self.coefficient[0],self.coefficient[1]))
        self.setup()

    def getYieldScale(self, bin, process):
        if process not in self.processes:
            return 1
        else:
            print('Scaling {0}, {1}'.format(process, bin))
            name = 'r_{0}'.format(process)

            return name


eft2D = EFT2DModel()
