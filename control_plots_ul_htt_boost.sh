source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

# VARIABLES="fj_XtmVsQCD_pt,fj_Xtm_eta,fj_Xtm_phi,fj_Xtm_mass,fj_Xtm_particleNet_XtmVsQCD,fj_Xtm_msoftdrop,fj_Xte_particleNet_XteVsQCD,fj_Xtt_particleNet_XttVsQCD,fj_Xtm_nsubjettiness_2over1,fj_Xtm_nsubjettiness_3over2"
VAR_KINEM="fj_XtmVsQCD_pt,fj_Xtm_eta,fj_Xtm_phi,fj_Xtm_mass,fj_Xtm_msoftdrop"
VAR_DISCR="fj_Xtm_particleNet_XtmVsQCD,fj_Xte_particleNet_XteVsQCD,fj_Xtt_particleNet_XttVsQCD"
VAR_SUBJET="fj_Xtm_nsubjettiness_2over1,fj_Xtm_nsubjettiness_3over2"
VAR_FINALSTATE="muons_finalstate,eles_finalstate"
VAR_MU_TAU="mu_tau_finalstate_deltaR,mu_tau_finalstate_mu_pt,mu_tau_finalstate_mu_eta,mu_tau_finalstate_mu_iso"
VAR_MET="fj_Xtm_met_deltaPhi,met_fatjet_pt"
VAR_COLL_APPROX="fj_Xtm_m_inv_ditau"

VARIABLES="${VAR_KINEM},${VAR_DISCR},${VAR_SUBJET},${VAR_FINALSTATE},${VAR_MU_TAU},${VAR_MET}"

ulimit -s unlimited
source utils/setup_root.sh
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

output_shapes="control_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shape_rootfile=${shapes_output}.root
# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"

if [[ $MODE == "XSEC" ]]; then

echo "##############################################################################################"
echo "#      Checking xsec friends directory                                                       #"
echo "##############################################################################################"

    echo "running xsec friends script"
    echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsdcache-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
fi

if [[ $MODE == "SHAPES" ]]; then
    echo "##############################################################################################"
    echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
    echo "##############################################################################################"

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output" ]; then
        mkdir -p $shapes_output
    fi
    
    python shapes/produce_shapes_htt_boost.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 4 --num-threads 12 \
        --optimization-level 1 --control_plots \
        --control-plot-set ${VARIABLES} --skip-systematic-variations \
        --output-file $shapes_output \
        --xrootd --validation-tag $TAG --boosted_tau_analysis

    # echo "##############################################################################################"
    # echo "#      Additional estimations                                      #"
    # echo "##############################################################################################"
    # if [[ $CHANNEL == "mm" ]]; then
    #     python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-qcd
    # else
    #     python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-qcd
    # fi
fi

if [[ $MODE == "PLOT" ]]; then
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

    # python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding --fake-factor
    # python3 plotting/plot_shapes_control_boost_htt.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding
    # python3 plotting/plot_shapes_control_boost_htt.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL}  --boost --blind-data --scaleGGH
    python3 plotting/plot_shapes_control_boost_htt.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --blind-data --boost --scaleZTT  --scaleGGH
fi
