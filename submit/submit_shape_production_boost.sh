#!/bin/bash

ERA=$1
CHANNEL=$2
SUBMIT_MODE=$3
TAG=$4
CONTROL=$5
NTUPLETAG=$6
OUTPUT=$7



[[ ! -z $1 && ! -z $2 && ! -z $3 && ! -z $4 && ! -z $5 ]] || (
    echo "[ERROR] Number of given parameters is too small."
    exit 1
)


PROCESSES="data,w,ztt,ztt_nlo,ttt,vvt,qcdjets,ggh"

source utils/setup_ul_samples.sh $NTUPLETAG $ERA
source utils/setup_root.sh
source utils/bashFunctionCollection.sh

PROCESSES=$(sort_string ${PROCESSES#,})

if [[ "$SUBMIT_MODE" == "singlegraph" ]]; then

    echo "[INFO] Preparing graph for processes $PROCESSES for submission..."
    echo "[INFO] Using tag $TAG"

    [[ ! -d $OUTPUT ]] && mkdir -p $OUTPUT

    python shapes/produce_shapes_boosted_analyse.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA \
        --optimization-level 1 \
        --only-create-graphs \
        --output-file dummy.root \
        --graph-dir $OUTPUT \
        --process-selection $PROCESSES \
        --xrootd --validation-tag $TAG --boosted_tau_analysis

    # Set output graph file name produced during graph creation.
    GRAPH_FILE_FULL_NAME=${OUTPUT}/analysis_unit_graphs-${ERA}-${CHANNEL}-${PROCESSES}.pkl
    GRAPH_FILE=${OUTPUT}/analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}.pkl
    if [[ $CONTROL == 1 ]]; then
        GRAPH_FILE_FULL_NAME=${OUTPUT}/control_unit_graphs-${ERA}-${CHANNEL}-${PROCESSES}.pkl
        GRAPH_FILE=${OUTPUT}/control_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}.pkl
    fi
    # rename the graph file to a shorter name
    mv $GRAPH_FILE_FULL_NAME $GRAPH_FILE

    # Prepare the jdl file for single core jobs.
    echo "[INFO] Creating the logging direcory for the jobs..."
    GF_NAME=$(basename $GRAPH_FILE)
    if [[ ! -d log/condorShapes/${GF_NAME%.pkl}/ ]]; then
        mkdir -p log/condorShapes/${GF_NAME%.pkl}/
    fi
    if [[ ! -d log/${GF_NAME%.pkl}/ ]]; then
        mkdir -p log/${GF_NAME%.pkl}/
    fi

    echo "[INFO] Preparing submission file for single core jobs for variation pipelines..."
    cp submit/produce_shapes_cc7.jdl $OUTPUT
    echo "output = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).out" >>$OUTPUT/produce_shapes_cc7.jdl
    echo "error = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).err" >>$OUTPUT/produce_shapes_cc7.jdl
    echo "log = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).log" >>$OUTPUT/produce_shapes_cc7.jdl
    echo "queue a3,a2,a1 from $OUTPUT/arguments.txt" >>$OUTPUT/produce_shapes_cc7.jdl
    echo "JobBatchName = Shapes_${CHANNEL}_${ERA}" >>$OUTPUT/produce_shapes_cc7.jdl
    # Prepare the multicore jdl.
    echo "[INFO] Preparing submission file for multi core jobs for nominal pipeline..."
    cp submit/produce_shapes_cc7.jdl $OUTPUT/produce_shapes_cc7_multicore.jdl
    # Replace the values in the config which differ for multicore jobs.
    if [[ $CONTROL == 1 ]]; then
        sed -i '/^RequestMemory/c\RequestMemory = 16000' $OUTPUT/produce_shapes_cc7_multicore.jdl
    else
        sed -i '/^RequestMemory/c\RequestMemory = 10000' $OUTPUT/produce_shapes_cc7_multicore.jdl
    fi
    sed -i '/^RequestCpus/c\RequestCpus = 1' $OUTPUT/produce_shapes_cc7_multicore.jdl
    sed -i '/^arguments/c\arguments = $(Proxy_path) $(a1) $(a2) $(a3) $(a4)' ${OUTPUT}/produce_shapes_cc7_multicore.jdl
    # Add log file locations to output file.
    echo "output = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).out" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
    echo "error = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).err" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
    echo "log = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).log" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
    echo "JobBatchName = Shapes_${CHANNEL}_${ERA}" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
    echo "queue a3,a2,a4,a1 from $OUTPUT/arguments_multicore.txt" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
    # Assemble the arguments.txt file used in the submission
    python submit/prepare_args_file.py --graph-file $GRAPH_FILE --output-dir $OUTPUT --pack-multiple-pipelines 10
    echo "[INFO] Submit shape production with 'condor_submit $OUTPUT/produce_shapes_cc7.jdl' and 'condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl'"
    condor_submit $OUTPUT/produce_shapes_cc7.jdl
    condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl
else
    echo "[ERROR] Given mode $SUBMIT_MODE is not supported. Aborting..."
    exit 1
fi