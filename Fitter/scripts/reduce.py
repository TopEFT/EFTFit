from EFTFitter import EFTFit
import sys

if __name__ == '__main__':
    fitter = EFTFit()
    fitter.reduction2DFitEFT('{}.POINTS.{}.{}'.format(sys.argv[3], sys.argv[1], sys.argv[2]), sys.argv[4:], final=False)
