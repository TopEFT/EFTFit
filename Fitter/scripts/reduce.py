from EFTFitter import EFTFit
import sys

if __name__ == '__main__':
    fitter = EFTFit()
    fitter.reductionFitEFT('{}.POINTS.{}.{}'.format(sys.argv[2], sys.argv[1], sys.argv[4]), sys.argv[3], final=False)
