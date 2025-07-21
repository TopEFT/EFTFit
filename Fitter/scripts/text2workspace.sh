#!/usr/bin/env bash

#----------------------------------------
# Default parameters
#----------------------------------------
WS_NAME="workspace.root"
COM_CARD="combinedcard.txt"
SCAL_DATA="scalings.json"
MODEL="IM"  # IM or AAC

#----------------------------------------
# Usage function
#----------------------------------------
PrintUsage() {
  cat <<EOF
Usage: $0 [options]

  -n <workspace>    Name of the output workspace file (default: $WS_NAME)
  -c <card>         Combined card input file       (default: $COM_CARD)
  -s <scaling-data> Scalings JSON file             (default: $SCAL_DATA)
  -m <model>        Physics model: IM or AAC       (default: $MODEL)
  -h                Show this help message and exit
EOF
  exit 1
}

#----------------------------------------
# Parse options
#----------------------------------------
while getopts "n:c:s:m:h" opt; do
  case "$opt" in
    n) WS_NAME="$OPTARG"    ;;
    c) COM_CARD="$OPTARG"   ;;
    s) SCAL_DATA="$OPTARG"  ;;
    m) MODEL="$OPTARG"      ;;
    h) PrintUsage           ;;
    *) PrintUsage           ;;
  esac
done
shift $((OPTIND -1))

#----------------------------------------
# Main script
#----------------------------------------

# extend stack size
ulimit -s unlimited

# choose physics model
if [[ "$MODEL" == "AAC" ]]; then
  PHY_MODEL="EFTFit.Fitter.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative"
  AAC_OPTION="--X-allow-no-background --for-fits --no-wrappers --X-pack-asympows \
--optimize-simpdf-constraints=cms --PO selectedWCs=selectedWCs.txt"
  RUN_COMMAND="time text2workspace.py \
    ${COM_CARD} \
    -P ${PHY_MODEL} \
    -o ${WS_NAME} \
    ${AAC_OPTION}"
else
  PHY_MODEL="HiggsAnalysis.CombinedLimit.InterferenceModels:interferenceModel"
  RUN_COMMAND="time text2workspace.py \
    ${COM_CARD} \
    -P ${PHY_MODEL} \
    --PO scalingData=${SCAL_DATA} \
    --PO verbose \
    -o ${WS_NAME}"
fi

printf "\nRunning the following command:\n%s\n\n" "$RUN_COMMAND"
$RUN_COMMAND
