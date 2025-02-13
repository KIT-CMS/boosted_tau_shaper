export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5


VARIABLES="fj_Xtm_msoftdrop"
POSTFIX="-ML"


ulimit -s unlimited
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
        # for category in "dm_binned"
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

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -i output/$datacard_output/htt_mt_${sf_cat}/ -o workspace_${sf_cat}.root --parallel 4 -m 125
    done

    exit 0

fi


if [[ $MODE == "FIT_LIMITS" ]]; then
    source utils/setup_cmssw.sh
    combineTool.py \
        -M AsymptoticLimits \
        -m 125 \
        -d output/$datacard_output/htt_mt_*/combined.txt.cmb \
        -n $ERA \
        --parallel 1 --there --verbose 2 \
        --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.01 \
        --run blind 
    echo "[INFO] Fit is done"
fi

# if [[ $MODE == "FIT" ]]; then
#     source utils/setup_cmssw.sh
#     combineTool.py \
#         -M MultiDimFit \
#         -m 125 \
#         -d output/$datacard_output/htt_mt_*/workspace_fj_softdrop*.root \
#         --algo singles --robustFit 1 \
#         --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
#         -n $ERA -v1 \
#         --parallel 1 \ 
#         --setParameterRanges r=-200,100 \
#         --setParameters r=1 \ 
#         -t -1

# fi

if [[ $MODE == "FIT" ]]; then
    source utils/setup_cmssw.sh

    combine -M MultiDimFit \
    -m 125 \
    -d /work/olavoryk/tau_pog_tau_sfs/boost_htt_v15Frb/boosted_tau_shaper/output/datacards_dm_sim_fit_proc/boost_mc_data_18UL_5Feb25_unc_v1-proc/2018_tauid/htt_mt_fj_softdrop_90_120/workspace_fj_softdrop_90_120.root \
    --algo singles --robustFit 1 \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --setParameterRanges r=-200,100 \
    --setParameters r=1 \
    -t -1


fi


