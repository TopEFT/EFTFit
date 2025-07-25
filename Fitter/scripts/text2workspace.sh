#!/usr/bin/env bash

# This scipt makes the workspace needed for running combine fits, workspace both for interference model (IM) and Dim6top model (AAC).
# The default is running with IM, but it can be switched to AAC (see -m option in PrintUsage function).

#----------------------------------------
# Default parameters
#----------------------------------------
DIR="."
WS_NAME="workspace.root"
COM_CARD="combinedcard.txt"
SCAL_DATA="scalings.json"
MODEL="IM"  # IM or AAC

# Will be set later based on the combined card path
SELECTED_WCS=""

#----------------------------------------
# Usage function
#----------------------------------------
PrintUsage() {
  cat <<EOF
Usage: $0 [options]

  -d <dir>          Directory containing ${WS_NAME}, ${COM_CARD} and ${SCAL_DATA}
                    (default: current directory)
  -m <model>        Physics model: IM or AAC       (default: $MODEL)
  -h                Show this help message and exit
EOF
  exit 1
}

#----------------------------------------
# Parse options
#----------------------------------------
while getopts "d:m:h" opt; do
  case "$opt" in
    d) DIR="$OPTARG"        ;;
    m) MODEL="$OPTARG"      ;;
    h) PrintUsage           ;;
    *) PrintUsage           ;;
  esac
done
shift $((OPTIND -1))

#----------------------------------------
# Resolve paths
#----------------------------------------

if [[ ! -d "$DIR" ]]; then
  echo "Error: directory '$DIR' not found." >&2
  exit 1
fi

WS_NAME="$(realpath "$DIR/$WS_NAME")"
COM_CARD="$(realpath "$DIR/$COM_CARD")"
SCAL_DATA="$(realpath "$DIR/$SCAL_DATA")"
SELECTED_WCS="$(realpath "$DIR/selectedWCs.txt")"

for file in "$COM_CARD" "$SCAL_DATA"; do
  if [[ ! -f "$file" ]]; then
    echo "Error: required file '$file' not found." >&2
    exit 1
  fi
done

if [[ "$MODEL" == "AAC" && ! -f "$SELECTED_WCS" ]]; then
  echo "Error: required file '$SELECTED_WCS' not found." >&2
  exit 1
fi

#----------------------------------------
# Main script
#----------------------------------------

# extend stack size
ulimit -s unlimited

# choose physics model
if [[ "$MODEL" == "AAC" ]]; then
  PHY_MODEL="EFTFit.Fitter.AnomalousCouplingEFTNegative:analyticAnomalousCouplingEFTNegative"
  AAC_OPTION="--X-allow-no-background --for-fits --no-wrappers --X-pack-asympows \
--optimize-simpdf-constraints=cms --PO selectedWCs=${SELECTED_WCS}"
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
