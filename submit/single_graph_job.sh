#!/bin/bash
ulimit -s unlimited

INPUT=$1
GRAPH=$2
PROC_DIR=$3
THREAD_ARG="--num-threads 1"
[[ -z $4 ]] || THREAD_ARG="--num-threads $4"

echo "INPUT: $INPUT"
echo "GRAPH: $GRAPH"
echo "PROC_DIR: $PROC_DIR"
echo "THREAD_ARG: $THREAD_ARG"

pushd $PROC_DIR

INP_BASE=$(basename $INPUT)
if [[ ! -d output/shapes/${INP_BASE%.pkl} ]]
then
    mkdir -p output/shapes/${INP_BASE%.pkl}
fi

source utils/setup_root.sh

echo "Running 'python submit/single_graph_job.py --input $INPUT --graph-number $GRAPH $THREAD_ARG'"
python submit/single_graph_job.py --input $INPUT --graph-number $GRAPH $THREAD_ARG