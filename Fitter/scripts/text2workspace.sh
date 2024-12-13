    '''
    This scipt makes the workspace needed for running combine fits, workspace both for interference model (IM) and Dim6top model (AAC)
    The default is running with IM. Uncomment the AAC command lines to run with AAC model.

    Note: Difference in two models
          IM model - uses scalings.json file and datacards with ONLY sm templates
          AAC model - uses selectedWCs.txt file and datacards with ALL EFT templates

    Make sure you have the corret input to run the each model
    '''
# extend run time
ulimit -s unlimited

# workspace naming
WS_NAME="workspace.root"

# files input
COM_CARD="combinedcard.txt"
SCAL_DATA="scalings.json"

# physics model - interference model
PHY_MODEL="HiggsAnalysis.CombinedLimit.InterferenceModels:interferenceModel"

# physics model option - uncomment for AAC model, need selectedWC.txt file
#PHY_MODEL="EFTFit.Fitter.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative"
#AAC_OPTION="--X-allow-no-background --for-fits --no-wrappers --X-pack-asympows --optimize-simpdf-constraints=cms --PO selectedWCs=selectedWCs.txt"

# run text2workspace using interference model
RUN_COMMAND="time text2workspace.py $COM_CARD -P $PHY_MODEL --PO scalingData=$SCAL_DATA --PO verbose -o $WS_NAME"

# run text2workspace using AAC model 
#RUN_COMMAND="time text2workspace.py $COM_CARD -P $PHY_MODEL -o $WS_NAME $AAC_OPTION" 

printf "\nRunning the following command:\n$RUN_COMMAND\n\n"
$RUN_COMMAND
