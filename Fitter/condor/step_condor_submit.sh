cmsenv
cluster=$1
job=$2

python /afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/condor/step_struct_maker_wrapper.py -i ${job}

