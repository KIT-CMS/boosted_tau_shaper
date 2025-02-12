source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5


VARIABLES="fj_Xtm_msoftdrop"
POSTFIX="-ML"


ulimit -s unlimited
source utils/setup_root.sh
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

output_shapes="control_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root

datacard_output="datacards_dm_sim_fit_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid"

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"



fj_softdrop_m_categories=("fj_softdrop_50_90" "fj_softdrop_90_120")

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi


if [[ $MODE == "XSEC" ]]; then

echo "##############################################################################################"
echo "#      Checking xsec friends directory                                                       #"
echo "##############################################################################################"

    echo "running xsec friends script"
    echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsdcache-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
fi

if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes_boosted_analyse.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --optimization-level 1 \
        --output-file $shapes_output \
        --xrootd --validation-tag $TAG --boosted_tau_analysis
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_boost.sh $ERA $CHANNEL \
        "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT 
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh

    echo "##############################################################################################"
    echo "#     synced shapes                                      #"
    echo "##############################################################################################"

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        --variable-selection ${VARIABLES} \
        -n 1

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root


    exit 0
fi

if [[ "${ERA}" == "2018"  ||  "${ERA}" == "2017" ]]; then 
    datacard_era=${ERA}
elif [[ "${ERA}" == "2016postVFP"  ||  "${ERA}" == "2016preVFP" ]]; then
   datacard_era="2016"
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh

        for sf_cat in "${fj_softdrop_m_categories[@]}"
    do
        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        # # for category in "dm_binned"
        $CMSSW_BASE/bin/el9_amd64_gcc12/MorphingTauID2017 \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --input_folder_mm=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=0 \
            --embedding=1 \
            --verbose=true \
            --postfix=$POSTFIX \
            --use_control_region=false \
            --auto_rebin=true \
            --categories=${sf_cat} \
            --era=$datacard_era \
            --output=$datacard_output
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd output/$datacard_output/
    
        cd $THIS_PWD

        # echo "[INFO] Create Workspace for datacard"
        # combineTool.py -M T2W -i output/$datacard_output_dm/htt_mt_${sf_cat}/ -o workspace_sf.root --parallel 4 -m 125
    done

    exit 0

fi
