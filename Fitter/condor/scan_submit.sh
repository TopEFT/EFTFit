cmsenv
cluster=$1
job=$2

python /afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/condor/2sigma_scan_wrapper.py -i ${job}

