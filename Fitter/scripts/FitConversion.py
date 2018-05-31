print "Parsing cross section parameterizations..."
import numpy as np
import os

#Dict that will hold the parameterizations of the cross-sections
scales = {}

#Input location
scalespath = os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/fitparams/'

#Loop over input files
print "Walking through files..."
for path,indirs,infiles in os.walk(scalespath):
    for infile in infiles:
        process = path.split('/')[-1]
        #For now, treat tllq, ttll, ttlnu as tZq, ttZ, ttW
        process = process.replace('tllq','tZq')
        process = process.replace('ttll','ttZ')
        process = process.replace('ttlnu','ttW')
        operator = infile.split('_')[-2]
        #Generate a table of the parameterizations with numpy
        filetable = np.genfromtxt(path+'/'+infile, skip_header=1, dtype=None)
        filetable = np.atleast_1d(filetable)
        for equation in filetable:
            if 'run2' in equation[0]: #Use the run2 parameterization
                coeffs = tuple(equation)[1:]
                if operator not in scales: #Check if dict key is initialized
                    scales[operator] = {}
                scales[operator].update({process:coeffs})

print "Saving numpy file {}...".format("scales.npy")
np.save(os.environ["CMSSW_BASE"]+'/src/EFTFit/Fitter/data/scales.npy', scales)
