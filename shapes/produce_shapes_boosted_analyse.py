#!/usr/bin/env python
import argparse
import logging
import os
import pickle
import re
import yaml
from itertools import combinations

from shapes.utils import (
    add_process,
    book_histograms,
    add_control_process,
    get_nominal_datasets,
    filter_friends,
    add_tauES_datasets,
    book_tauES_histograms,
)
from ntuple_processor.variations import ReplaceVariable
from ntuple_processor import Histogram
from ntuple_processor import (
    Unit,
    UnitManager,
    GraphManager,
    RunManager,
)
from ntuple_processor.utils import Selection

from config.shapes.channel_selection_boost_htt import channel_selection
from config.shapes.file_names_boost_htt import files
from config.shapes.process_selection_htt_boost import (
    # Data_base_process_selection,
    DY_process_selection,
    DY_NLO_process_selection,
    TT_process_selection,
    VV_process_selection,
    W_process_selection,
    QCDJETS_process_selection,
    GGH_process_selection
    # ZTT_process_selection,
    # ZL_process_selection,
    # ZJ_process_selection,
    # TTT_process_selection,
    # TTL_process_selection,
    # TTJ_process_selection,
    # VVT_process_selection,
    # VVJ_process_selection,
    # VVL_process_selection,
    # ggH125_process_selection,
    # qqH125_process_selection,
    # ZTT_embedded_process_selection,
    # ZH_process_selection,
    # WH_process_selection,
    # ggHWW_process_selection,
    # qqHWW_process_selection,
    # ZHWW_process_selection,
    # WHWW_process_selection,
    # ttH_process_selection,
)

# from config.shapes.category_selection import categorization
# from config.shapes.category_selection import categorization as default_categorization
from config.shapes.boosted_fit_binning import categorization as default_categorization
# from config.shapes.tauid_measurement_binning import (
#     categorization as tauid_categorization,
# )

# from config.shapes.boosted_fit_binning import (

#  categorization as tauid_categorization,
# )

# Variations for estimation of fake processes
from config.shapes.variations import (
    same_sign,
    same_sign_em,
    anti_iso_lt,
    anti_iso_tt,
    anti_iso_tt_mcl,
    abcd_method,
)

# Energy scale uncertainties
from config.shapes.variations import (
    tau_es_3prong,
    tau_es_3prong1pizero,
    tau_es_1prong,
    tau_es_1prong1pizero,
    mu_fake_es_inc,
    ele_fake_es,
    emb_tau_es_3prong,
    emb_tau_es_3prong1pizero,
    emb_tau_es_1prong,
    emb_tau_es_1prong1pizero,
    jet_es,
    # TODO add missing ES
    # mu_fake_es_1prong,
    # mu_fake_es_1prong1pizero,
    # ele_es,
    # ele_res,
    emb_e_es,
    # ele_fake_es_1prong,
    # ele_fake_es_1prong1pizero,
    # ele_fake_es,
)

# MET related uncertainties.
from config.shapes.variations import (
    met_unclustered,
    recoil_resolution,
    recoil_response,
)

# efficiency uncertainties
from config.shapes.variations import (
    tau_id_eff_lt,
    tau_id_eff_tt,
    emb_tau_id_eff_lt,
    emb_tau_id_eff_tt,
    emb_tau_id_eff_lt_corr,
)

# fake rate uncertainties
from config.shapes.variations import jet_to_tau_fake, zll_et_fake_rate, zll_mt_fake_rate

# TODO add trigger efficiency uncertainties
# # trigger efficiencies
from config.shapes.variations import (
    # tau_trigger_eff_tt,
    # tau_trigger_eff_tt_emb,
    trigger_eff_mt,
    trigger_eff_et,
    trigger_eff_et_emb,
    trigger_eff_mt_emb,
)

# Additional uncertainties
from config.shapes.variations import (
    prefiring,
    zpt,
    top_pt,
    pileup_reweighting,
)

# TODO add missing uncertainties
# Additional uncertainties
# from config.shapes.variations import (
#     btag_eff,
#     mistag_eff,
#     emb_decay_mode_eff_lt,
#     emb_decay_mode_eff_tt,
# )
from config.shapes.signal_variations import (
    ggh_acceptance,
    qqh_acceptance,
)

# jet fake uncertainties
from config.shapes.variations import (
    wfakes_tt,
    wfakes_w_tt,
)

# TODO add jetfake uncertainties
# # jet fake uncertainties
from config.shapes.variations import (
    ff_variations_lt,
    # ff_variations_tt,
    # ff_variations_tt_mcl,
    # qcd_variations_em,
    wfakes_tt,
    wfakes_w_tt,
    ff_variations_tau_es_lt,
    ff_variations_tau_es_emb_lt,
    # ff_variations_tau_es_tt,
    # ff_variations_tau_es_tt_mcl,
)

from config.shapes.control_binning import control_binning_htt_boost as default_control_binning
from config.shapes.gof_binning import load_gof_binning

logger = logging.getLogger("")


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for the legacy MSSM analysis."
    )
    parser.add_argument("--era", required=True, type=str, help="Experiment era.")
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist: [channel for channel in channellist.split(",")],
        help="Channels to be considered, seperated by a comma without space",
    )
    parser.add_argument(
        "--directory", required=True, type=str, help="Directory with Artus outputs."
    )
    parser.add_argument(
        "--et-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for et.",
    )
    parser.add_argument(
        "--mt-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for mt.",
    )
    parser.add_argument(
        "--tt-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for tt.",
    )
    parser.add_argument(
        "--em-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for em.",
    )
    parser.add_argument(
        "--mm-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for mm.",
    )
    parser.add_argument(
        "--ee-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for ee.",
    )
    parser.add_argument(
        "--optimization-level",
        default=2,
        type=int,
        help="Level of optimization for graph merging.",
    )
    parser.add_argument(
        "--num-processes", default=1, type=int, help="Number of processes to be used."
    )
    parser.add_argument(
        "--num-threads", default=1, type=int, help="Number of threads to be used."
    )
    parser.add_argument(
        "--skip-systematic-variations",
        action="store_true",
        help="Do not produce the systematic variations.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        type=str,
        help="ROOT file where shapes will be stored.",
    )
    parser.add_argument(
        "--control_plots",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes.",
    )
    parser.add_argument(
        "--gof-inputs",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes.",
    )
    parser.add_argument(
        "--do-2dGofs",
        action="store_true",
        help="It set, run the 2D gof Tests as well",
    )
    parser.add_argument(
        "--control-plots-full-samples",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes.",
    )
    parser.add_argument(
        "--control-plot-set",
        default=[],
        type=lambda varlist: [variable for variable in varlist.split(",")],
        help="Variables the shapes should be produced for.",
    )
    parser.add_argument(
        "--only-create-graphs",
        action="store_true",
        help="Create and optimise graphs and create a pkl file containing the graphs to be processed.",
    )
    parser.add_argument(
        "--process-selection",
        default=None,
        type=lambda proclist: set([process.lower() for process in proclist.split(",")]),
        help="Subset of processes to be processed.",
    )
    parser.add_argument(
        "--graph-dir",
        default=None,
        type=str,
        help="Directory the graph file is written to.",
    )
    parser.add_argument(
        "--enable-booking-check",
        action="store_true",
        help="Enables check for double actions during booking. Takes long for all variations.",
    )
    parser.add_argument(
        "--special-analysis",
        help="Can be set to a special analysis name to only run that analysis.",
        choices=["TauID", "TauES"],
        default=None,
    )
    parser.add_argument(
        "--boosted_tau_analysis",
        action="store_true",
        help="Can be set to a switch to a boosted tau analysis selection.",
    )
    parser.add_argument(
        "--xrootd",
        action="store_true",
        help="Read input ntuples and friends via xrootd from gridka dCache",
    )
    parser.add_argument(
        "--validation-tag",
        default="default",
        type=str,
        help="Tag to be used for the validation of the input samples",
    )
    return parser.parse_args()


def get_analysis_units(
    channel, era, datasets, categorization, special_analysis, nn_shapes=False, boosted_tau = False,
):
    analysis_units = {}
    
    add_process(
        analysis_units,
        name="data",
        dataset=datasets["data"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            # Data_base_process_selection(era, channel),
        ],
        categorization=categorization,
        channel=channel,
    )

    add_process(
        analysis_units,
        name="ztt",
        dataset=datasets["DY"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            DY_process_selection(channel, era, boosted_tau),
            
        ],
        categorization=categorization,
        channel=channel,
    )

    add_process(
        analysis_units,
        name="ztt_nlo",
        dataset=datasets["DYNLO"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            DY_NLO_process_selection(channel, era, boosted_tau),
            
        ],
        categorization=categorization,
        channel=channel,
    )

    add_process(
        analysis_units,
        name="ttt",
        dataset=datasets["TT"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            TT_process_selection(channel, era, boosted_tau),
            
        ],
        categorization=categorization,
        channel=channel,
    )

    add_process(
        analysis_units,
        name="vvt",
        dataset=datasets["VV"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            VV_process_selection(channel, era, boosted_tau),
            
        ],
        categorization=categorization,
        channel=channel,
    )
    
    add_process(
        analysis_units,
        name="w",
        dataset=datasets["W"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            W_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )

    add_process(
        analysis_units,
        name="qcdjets",
        dataset=datasets["QCDJETS"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            QCDJETS_process_selection(channel, era, boosted_tau),
            
        ],
        categorization=categorization,
        channel=channel,
    )

    add_process(
        analysis_units,
        name="ggh",
        dataset=datasets["GGH"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau),
            GGH_process_selection(channel, era, boosted_tau),
            
        ],
        categorization=categorization,
        channel=channel,
    )

    return analysis_units



def prepare_special_analysis(special):
    if special is None:
        return default_categorization
    elif special and special == "TauID":
        return tauid_categorization
    elif special and special == "TauES":
        return taues_categorization
    else:
        raise ValueError("Unknown special analysis: {}".format(special))


def main(args):
    # Parse given arguments.
    friend_directories = {
        "et": args.et_friend_directory,
        "mt": args.mt_friend_directory,
        "tt": args.tt_friend_directory,
        "em": args.em_friend_directory,
        "mm": args.mm_friend_directory,
        "ee": args.ee_friend_directory,
    }
    if ".root" in args.output_file:
        output_file = args.output_file
    else:
        output_file = "{}.root".format(args.output_file)
    # setup categories depending on the selected anayses
    special_analysis = args.special_analysis
    categorization = prepare_special_analysis(special_analysis)
    um = UnitManager()
    do_check = args.enable_booking_check
    era = args.era
    boostes_tau_analysis = args.boosted_tau_analysis

    nominals = {}
    nominals[era] = {}
    nominals[era]["datasets"] = {}
    nominals[era]["units"] = {}

    # Step 1: create units and book actions
    for channel in args.channels:
        nominals[era]["datasets"][channel] = get_nominal_datasets(
            era, channel, friend_directories, files, args.directory,
            xrootd=args.xrootd, validation_tag=args.validation_tag
        )

        nominals[era]["units"][channel] = get_analysis_units(
            channel,
            era,
            nominals[era]["datasets"][channel],
            categorization,
            special_analysis,
            boosted_tau=boostes_tau_analysis,
        )

    # boosted_proc = {"data", "ztt", "ztt_nlo", "ttt", "vvt", "w", "w_nlo", "qcdjets"}
    boosted_proc = {"data",  "w", "ztt", "ztt_nlo", "ttt", "vvt","qcdjets"}
    # boosted_proc_mc = {"w", "ztt", "ztt_nlo", "ttt", "vvt","qcdjets"}

    if channel in ["mt"] and args.boosted_tau_analysis == True:
        book_histograms(
            um,
            processes=boosted_proc,
            datasets=nominals[era]["units"][channel],
            variations=[],
            enable_check=do_check,
        )

        ##################################
        # SYSTEMATICS
        ############################
        # if args.skip_systematic_variations:
        #     pass
        # else:

        book_histograms(
            um,
            processes=boosted_proc- {"data"},
            datasets=nominals[era]["units"][channel],
            variations=[jet_es],
            enable_check=do_check,
        )

        book_histograms(
            um,
            processes=boosted_proc- {"data"},
            datasets=nominals[era]["units"][channel],
            variations=[met_unclustered, pileup_reweighting],
            enable_check=do_check,
        )

        book_histograms(
            um,
            processes=boosted_proc- {"data"},
            datasets=nominals[era]["units"][channel],
            variations=[recoil_resolution, recoil_response],
            enable_check=do_check,
        )

    # Step 2: convert units to graphs and merge them
    g_manager = GraphManager(um.booked_units, True)
    g_manager.optimize(args.optimization_level)
    graphs = g_manager.graphs
    for graph in graphs:
        print("%s" % graph)

    if args.only_create_graphs:
        if args.control_plots or args.gof_inputs:
            graph_file_name = "control_unit_graphs-{}-{}-{}.pkl".format(
                era, ",".join(args.channels), ",".join(sorted(boosted_proc))
            )
        else:
            graph_file_name = "analysis_unit_graphs-{}-{}-{}.pkl".format(
                era, ",".join(args.channels), ",".join(sorted(boosted_proc))
            )
        if args.graph_dir is not None:
            graph_file = os.path.join(args.graph_dir, graph_file_name)
        else:
            graph_file = graph_file_name
        logger.info("Writing created graphs to file %s.", graph_file)
        with open(graph_file, "wb") as f:
            pickle.dump(graphs, f)
    else:
        # Step 3: convert to RDataFrame and run the event loop
        r_manager = RunManager(graphs)
        r_manager.run_locally(output_file, args.num_processes, args.num_threads)
    return


if __name__ == "__main__":
    args = parse_arguments()
    if ".root" in args.output_file:
        log_file = args.output_file.replace(".root", ".log")
    else:
        log_file = "{}.log".format(args.output_file)
    setup_logging(log_file, logging.DEBUG)
    main(args)
