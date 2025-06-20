#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser_ntuple_processor_inputshapes as rootfile_parser
import Dumbledraw.styles as styles
import ROOT

import argparse
import copy
import yaml
import os
import math

import logging
logger = logging.getLogger("")
from multiprocessing import Pool
from multiprocessing import Process

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument(
        "-l", "--linear", action="store_true", help="Enable linear x-axis")
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes of processes")
    parser.add_argument(
        "--variables",
        type=str,
        default=None,
        help="Enable control plotting for given variable")
    parser.add_argument(
        "--category-postfix",
        type=str,
        default=None,
        help="Enable control plotting for given category_postfix. Structure of a category: <variable>_<postfix>")
    parser.add_argument(
        "--channels",
        type=str,
        default=None,
        help="Enable control plotting for given variable")
    parser.add_argument(
        "--normalize-by-bin-width",
        action="store_true",
        help="Normelize plots by bin width")
    parser.add_argument(
        "--fake-factor",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--embedding",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--nlo",
        action="store_true",
        help="Use NLO DY and Wjets MC")
    parser.add_argument(
        "--add-signals",
        action="store_true",
        help="Draw also signal processes and not only backgrounds")
    parser.add_argument(
        "--draw-jet-fake-variation",
        type=str,
        default=None,
        help="Draw variation of jetFakes or QCD in derivation region.")
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Plot a special category instead of nominal")
    parser.add_argument(
        "--boost",
        action="store_true",
        help="Plot boosted H->tau tau without genmatching")
    parser.add_argument(
        "--scaleZTT",
        action="store_true",
        help="A jet softdrop mass is added for comparison")
    parser.add_argument(
        "--blind-data",
        action="store_true",
        help="A jet softdrop mass is added for comparison")
    parser.add_argument(
        "--scaleGGH",
        action="store_true",
        help="Scale ggH process")

    return parser.parse_args()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def main(info):
    args = info["args"]
    variable = info["variable"]
    channel = info["channel"]
    channel_dict = {
        "ee": "#font[42]{#scale[0.85]{ee}}",
        "em": "#scale[0.85]{e}#mu",
        "et": "#font[42]{#scale[0.85]{e}}#tau_{#font[42]{h}}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{#font[42]{h}}",
        "tt": "#tau_{#font[42]{h}}#tau_{#font[42]{h}}"
    }
    if args.linear == True:
        split_value = 0.1
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em", "mm", "ee"]}

    bkg_processes = [
        "VVL", "TTL", "ZL", "jetFakesEMB", "EMB"
    ]
    if args.boost and not args.embedding and not args.fake_factor:
        bkg_processes = ["ZTT", "TTT", "VVT", "W", "QCDJETS"]
    if not args.fake_factor and args.embedding:
        if args.nlo:
            bkg_processes = [
                "QCDEMB", "VVL", "VVJ", "W_NLO", "TTL", "TTJ", "ZJ_NLO", "ZL_NLO", "EMB"  # TODO: Also use NLO version of QCD estimate?
            ]
        else:
            bkg_processes = [
                "VVL", "TTL", "ZL", "QCDEMB", "VVJ", "W","TTJ", "ZJ", "EMB"
            ]
    if not args.embedding and args.fake_factor:
        if args.nlo:
            bkg_processes = [
                "VVT", "VVL", "TTT", "TTL", "ZL_NLO", "jetFakes", "ZTT_NLO",  # TODO jetFakes NLO
            ]
        else:
            bkg_processes = [
                "VVT", "VVL", "TTL", "ZL", "jetFakes", "ZTT"
            ]
    if not args.embedding and not args.fake_factor and not args.boost:
        if args.nlo:

            bkg_processes = [
                "VVT", "VVL", "VVJ", "W_NLO", "TTT", "TTL", "TTJ", "ZJ_NLO", "ZL_NLO", "ZTT_NLO"  # just try to do it by process
            ]
        else:

            bkg_processes = [
                 "VVL", "VVJ", "W", "TTT", "TTL", "TTJ", "ZJ", "ZL", "ZTT"
            ]
    if args.draw_jet_fake_variation is not None:
        bkg_processes = [
            "VVL", "TTL", "ZL", "EMB"
        ]
        if not args.fake_factor and args.embedding:
            bkg_processes = [
                "VVL", "VVJ", "W", "TTL", "TTJ", "ZJ", "ZL", "EMB"
            ]
        if not args.embedding and args.fake_factor:
            bkg_processes = [
                "VVT", "VVL", "TTT", "TTL", "ZL", "ZTT"
            ]
        if not args.embedding and not args.fake_factor:
            bkg_processes = [
                "VVT", "VVL", "VVJ", "W", "TTT", "TTL", "TTJ", "ZJ", "ZL", "ZTT"
            ]
    all_bkg_processes = [b for b in bkg_processes]
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    if "2016postVFP" in args.era:
        era = "Run2016postVFP"
    elif "2016preVFP" in args.era:
        era = "Run2016preVFP"
    elif "2017" in args.era:
        era = "Run2017"
    elif "2018" in args.era:
        era = "Run2018"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # category = "_".join([channel, variable])
    # if args.category_postfix is not None:
    #     category += "_%s"%args.category_postfix
    rootfile = rootfile_parser.Rootfile_parser(args.input, variable, )
    bkg_processes = [b for b in all_bkg_processes]
    if "em" in channel:
        if not args.embedding:
            if args.nlo:
                bkg_processes = [
                    "QCD_NLO", "VVT", "VVL", "W_NLO", "TTT", "TTL", "ZL_NLO", "ZTT_NLO"
                ]
            else:
                bkg_processes = [
                    "QCD", "VVT", "VVL", "W", "TTT", "TTL", "ZL", "ZTT"
                ]
        if args.embedding:
            if args.nlo:
                bkg_processes = [
                    "QCDEMB_NLO", "VVL", "W_NLO", "TTL", "ZL_NLO", "EMB"
                ]
            else:
                bkg_processes = [
                    "QCDEMB", "VVL", "W", "TTL", "ZL", "EMB"
                ]
        if args.draw_jet_fake_variation is not None:
            if not args.embedding:
                bkg_processes = [
                    "VVT", "VVL", "W", "TTT", "TTL", "ZL", "ZTT"
                ]
            if args.embedding:
                bkg_processes = [
                    "VVL", "W", "TTL", "ZL", "EMB"
                ]

    if "mm" in channel or "ee" in channel:
        if args.embedding:
            if args.nlo:
                bkg_processes = [
                    "QCDEMB_NLO", "W_NLO", "EMB"
                ]
            else:
                bkg_processes = [
                    "QCDEMB", "W", "EMB",
                ]
        else:
            if args.nlo:
                bkg_processes = [
                    "QCD_NLO", "VVL", "W_NLO", "TTL", "ZL_NLO"
                ]
            else:
                bkg_processes = [
                    "QCDEMB", "VVL", "W", "TTL", "ZL"
                ]
    # TODO Remove QCD from list of shapes for now
    # for i, elem in enumerate(bkg_processes):
    #     if elem.startswith("QCD"):
    #         to_remove = i
    #         break
    # bkg_processes.pop(to_remove)

    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    print("%%%%%%%%%%%%% legend background processes",legend_bkg_processes)

    # create plot
    width = 600
    if args.linear == True:
        plot = dd.Plot(
            [0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
    else:
        plot = dd.Plot(
            [0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)

    # get background histograms
    total_bkg = None
    if args.category is None:
        stype = "Nominal"
        cat = None
    else:
        stype = "Nominal"
        cat = args.category

    for index,process in enumerate(bkg_processes):
        print("$$$$$$$$$$$$$$$$$$$$ index, process", index, process)
        print("rootfile type: ", type(rootfile.get_boost_file(channel, process, category=cat, shape_type=stype)))
        if index == 0:
            total_bkg = rootfile.get_boost_file(channel, process, category=cat, shape_type=stype).Clone()
        else:
            total_bkg.Add(rootfile.get_boost_file(channel, process, category=cat, shape_type=stype))
        if process in ["jetFakesEMB", "jetFakes"] and channel == "tt":
            total_bkg.Add(rootfile.get(channel, "wFakes", category=cat, shape_type=stype))
            jetfakes_hist = rootfile.get(channel, process, category=cat, shape_type=stype)
            jetfakes_hist.Add(
                rootfile.get(channel, "wFakes", category=cat, shape_type=stype))
            plot.add_hist(
                jetfakes_hist, process, "bkg")
        else:
            plot.add_hist(
                rootfile.get_boost_file(channel, process, category=cat, shape_type=stype), process, "bkg")
        plot.setGraphStyle(
            process, "hist", fillcolor=styles.color_dict[process])


    plot.add_hist(total_bkg, "total_bkg")
    plot.setGraphStyle(
        "total_bkg",
        "e2",
        markersize=0,
        fillcolor=styles.color_dict["unc"],
        linecolor=0)
    
    if not args.blind_data:

        plot.add_hist(rootfile.get(channel, "data", category=cat, shape_type=stype), "data_obs")
        data_norm = plot.subplot(0).get_hist("data_obs").Integral()
        plot.subplot(0).get_hist("data_obs").GetXaxis().SetMaxDigits(4)
        plot.subplot(0).setGraphStyle("data_obs", "e0")
        plot.subplot(0).setGraphStyle("data_obs", "e0")
        if args.linear:
            pass
        else:
            plot.subplot(1).setGraphStyle("data_obs", "e0")

    if args.scaleZTT:
        scaledZTT_scale = 0
        scaledZTT_hist = rootfile.get_boost_file(channel, "ZTT", category=cat, shape_type=stype).Clone()
        if scaledZTT_hist.Integral() > 0:
            scaledZTT_scale = 50
        scaledZTT_hist.Scale(scaledZTT_scale)
        plot.add_hist(scaledZTT_hist, "scaledZTT", "scaledZTT")
        plot.subplot(0).setGraphStyle("scaledZTT", "hist", linecolor=styles.color_dict["HWW"], linewidth=2)

        bkg_processes.remove("ZTT")
        legend_bkg_processes.remove("ZTT")

    if args.scaleGGH:
        scaledGGH_scale = 0
        scaledGGH_hist = rootfile.get_boost_file(channel, "GGH", category=cat, shape_type=stype).Clone()
        w_hist = rootfile.get(channel, "W", category=cat, shape_type=stype).Clone()
        if scaledGGH_hist.Integral() > 0:
            scaledGGH_scale = 50
        scaledGGH_hist.Scale(scaledGGH_scale)
        plot.add_hist(scaledGGH_hist, "scaledGGH", "scaledGGH")
        plot.subplot(0).setGraphStyle("scaledGGH", "hist", linecolor=styles.color_dict["ggH"], linewidth=2)


    scaledGGH_hist = rootfile.get_boost_file(channel, "GGH", category=cat, shape_type=stype).Clone()
    w_hist = rootfile.get(channel, "W", category=cat, shape_type=stype).Clone()    

    ggh_yield = scaledGGH_hist.Integral()
    w_yield = w_hist.Integral()

    signif = ggh_yield / math.sqrt(ggh_yield + w_yield)

    # get signal histograms
    plot_idx_to_add_signal = [0,2] if args.linear else [1,2]
    if args.add_signals:
        for i in plot_idx_to_add_signal:
            ggH = rootfile.get(channel, "ggH125",category=cat).Clone()
            qqH = rootfile.get(channel, "qqH125",category=cat).Clone()

            if ggH.Integral() > 0:
                ggH_scale = 10
            else:
                ggH_scale = 0.0
            if qqH.Integral() > 0:
                qqH_scale = 10
            else:
                qqH_scale = 0.0


            if i in [0,1]:
                ggH.Scale(ggH_scale)
                qqH.Scale(qqH_scale)
                # VH.Scale(VH_scale)
                # ttH.Scale(ttH_scale)
                # HWW.Scale(HWW_scale)
            plot.subplot(i).add_hist(ggH, "ggH")
            plot.subplot(i).add_hist(ggH, "ggH_top")
            plot.subplot(i).add_hist(qqH, "qqH")
            plot.subplot(i).add_hist(qqH, "qqH_top")


        plot.subplot(0 if args.linear else 1).setGraphStyle(
            "ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
        plot.subplot(0 if args.linear else 1).setGraphStyle("ggH_top", "hist", linecolor=0)
        plot.subplot(0 if args.linear else 1).setGraphStyle(
            "qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
        plot.subplot(0 if args.linear else 1).setGraphStyle("qqH_top", "hist", linecolor=0)


        # assemble ratio
        bkg_ggH = plot.subplot(2).get_hist("ggH")
        bkg_qqH = plot.subplot(2).get_hist("qqH")
        bkg_ggH.Add(plot.subplot(2).get_hist("total_bkg"))
        bkg_qqH.Add(plot.subplot(2).get_hist("total_bkg"))
        plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH")
        plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH_top")
        plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH")
        plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH_top")
        plot.subplot(2).setGraphStyle(
            "bkg_ggH",
            "hist",
            linecolor=styles.color_dict["ggH"],
            linewidth=3)
        plot.subplot(2).setGraphStyle("bkg_ggH_top", "hist", linecolor=0)
        plot.subplot(2).setGraphStyle(
            "bkg_qqH",
            "hist",
            linecolor=styles.color_dict["qqH"],
            linewidth=3)
        plot.subplot(2).setGraphStyle("bkg_qqH_top", "hist", linecolor=0)

    if args.add_signals:
        to_draw = [
            "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
            "bkg_qqH_top", "data_obs"
        ] 
    else:
        if args.blind_data:
            to_draw = [
                "total_bkg",
            ]
        if not args.blind_data:
            to_draw = [
                "total_bkg", "data_obs"
            ]
    plot.subplot(2).normalize(to_draw, "total_bkg")

    # stack background processes
    plot.create_stack(bkg_processes, "stack")

    # normalize stacks by bin-width
    if args.normalize_by_bin_width:
        plot.subplot(0).normalizeByBinWidth()
        plot.subplot(1).normalizeByBinWidth()

    # set axes limits and labels

    if not args.blind_data: 
        plot.subplot(0).setYlims(
            split_dict[channel],
            max(1.6 * plot.subplot(0).get_hist("data_obs").GetMaximum(),
                split_dict[channel] * 2))
        
    if args.blind_data: 
        plot.subplot(0).setYlims(
            split_dict[channel],
            max(2.6 * plot.subplot(0).get_hist("W").GetMaximum(),
                split_dict[channel] * 2))

    log_quantities = ["ME_ggh", "ME_vbf", "ME_z2j_1", "ME_z2j_2", "ME_q2v1", "ME_q2v2", "ME_vbf_vs_ggh", "ME_ggh_vs_Z"]
    if variable in log_quantities:
        plot.subplot(0).setLogY()
        plot.subplot(0).setYlims(
            1.0,
            1000 * plot.subplot(0).get_hist("data_obs").GetMaximum())

    # plot.subplot(2).setYlims(0.75, 1.45)
    plot.subplot(2).setYlims(0.55, 1.85)
    # if channel == "mm":
    #     plot.subplot(0).setLogY()
    #     plot.subplot(0).setYlims(1, 10**10)

    if args.linear != True:
        plot.subplot(1).setYlims(0.1, split_dict[channel])
        plot.subplot(1).setYlabel(
            "")  # otherwise number labels are not drawn on axis
        plot.subplot(1).setLogY()
    # Check if variables should be plotted with log x axis
    log_x_variables = ["puppimet"]
    if variable in log_x_variables:
        plot.subplot(0).setLogX()
        plot.subplot(1).setLogX()
        plot.subplot(2).setLogX()
    if variable != None:
        if variable in styles.x_label_dict[channel]:
            x_label = styles.x_label_dict[channel][
                variable]
        else:
            x_label = variable
        plot.subplot(2).setXlabel(x_label)
    else:
        plot.subplot(2).setXlabel("NN output")
    if args.normalize_by_bin_width:
        plot.subplot(0).setYlabel("dN/d(NN output)")
    else:
        plot.subplot(0).setYlabel("N_{events}")

    plot.subplot(2).setYlabel("")
    plot.subplot(2).setGrid()
    plot.scaleYLabelSize(0.8)
    plot.scaleYTitleOffset(1.1)

    category = ""
    if not channel == "tt" and category in ["11", "12", "13", "14", "15", "16"]:
        plot.subplot(2).changeXLabels(["0.2", "0.4", "0.6", "0.8", "1.0"])

    if args.add_signals:
        procs_to_draw = ["stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
    else:
        if not args.blind_data:
            procs_to_draw = ["stack", "total_bkg", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
            if args.scaleZTT:
                procs_to_draw.append("scaledZTT")
            if args.scaleGGH:
                procs_to_draw.append("scaledGGH")
        
        if args.blind_data:
            procs_to_draw = ["stack", "total_bkg"] if args.linear else ["stack", "total_bkg"]
            if args.scaleZTT:
                procs_to_draw.append("scaledZTT")
            if args.scaleGGH:
                procs_to_draw.append("scaledGGH")
    if args.draw_jet_fake_variation is not None:
        procs_to_draw = ["stack", "total_bkg", "data_obs"]
    plot.subplot(0).Draw(procs_to_draw)
    if args.linear != True:
        
        if args.add_signals:
            plot.subplot(1).Draw([
                "stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top",
                "data_obs"
            ])
        else:
            plot.subplot(1).Draw([
                "stack", "total_bkg", "data_obs"
            ])
    if args.draw_jet_fake_variation is None:
        plot.subplot(2).Draw([
            "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
            "bkg_qqH_top", "data_obs"
        ])
    else:
        plot.subplot(2).Draw([
            "total_bkg", "data_obs"
        ])

    # create legends
    suffix = ["", "_top"]
    for i in range(2):

        plot.add_legend(width=0.6, height=0.15)
        for process in legend_bkg_processes:
            if "mm" in channel:
                if process == "EMB":
                    plot.legend(i).add_entry(
                    0,
                    process,
                    "#mu#rightarrow#mu embedded",
                    'f',
                    )
                else:
                    plot.legend(i).add_entry(
                    0,
                    process, 
                    styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV").replace("_NLO","")], 
                    'f'
                    )
            plot.legend(i).add_entry(
            0,
            process, 
            styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV").replace("_NLO","")], 
            'f'
            )
        plot.legend(i).add_entry(0, "total_bkg", "Bkg. stat. unc.", 'f')
        if args.add_signals:
            plot.legend(i).add_entry(0 if args.linear else 1, "ggH%s" % suffix[i], "%s #times gg#rightarrowH"%str(int(ggH_scale)), 'l')
            plot.legend(i).add_entry(0 if args.linear else 1, "qqH%s" % suffix[i], "%s #times qq#rightarrowH"%str(int(qqH_scale)), 'l')
           
        if not args.blind_data:
            plot.legend(i).add_entry(0, "data_obs", "Observed", 'PE2L')
        plot.legend(i).setNColumns(3)
        if args.scaleZTT:
            plot.legend(i).add_entry(0, "scaledZTT", "Z#rightarrow#tau#tau #times "+str(scaledZTT_scale), 'l')
        if args.scaleGGH:
            plot.legend(i).add_entry(0, "scaledGGH", "gg#rightarrowH #times "+str(scaledGGH_scale), 'l')
    latex = ROOT.TLatex()
    latex.SetNDC()  # Normalized device coordinates (0-1)
    latex.SetTextSize(0.03)  # Adjust text size
    latex.SetTextFont(42)  # CMS-style font
    latex.DrawLatex(0.2, 0.55, r"\frac{S}{\sqrt(S+B)}= %.2f" % signif)
    plot.legend(0).Draw()
    plot.legend(1).setAlpha(0.0)
    plot.legend(1).Draw()

    for i in range(2):
        plot.add_legend(
            reference_subplot=2, pos=1, width=0.6, height=0.03)
        if not args.blind_data:
            plot.legend(i + 2).add_entry(0, "data_obs", "Observed", 'PE2L')
        if "mm" not in channel and "ee" not in channel and args.draw_jet_fake_variation is None and args.add_signals:
            plot.legend(i + 2).add_entry(0 if args.linear else 1, "ggH%s" % suffix[i],
                                         "ggH+bkg.", 'l')
            plot.legend(i + 2).add_entry(0 if args.linear else 1, "qqH%s" % suffix[i],
                                         "qqH+bkg.", 'l')
        plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. stat. unc.", 'f')
        plot.legend(i + 2).setNColumns(4)
    plot.legend(2).Draw()
    plot.legend(3).setAlpha(0.0)
    plot.legend(3).Draw()

    # draw additional labels
    plot.DrawCMS(thesisstyle=True, preliminary=True)
    if "2016postVFP" in args.era:
        plot.DrawLumi("16.8 fb^{-1} (2016UL postVFP, 13 TeV)")
    elif "2016preVFP" in args.era:
        plot.DrawLumi("19.5 fb^{-1} (2016UL preVFP, 13 TeV)")
    elif "2017" in args.era:
        plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)")
    elif "2018" in args.era:
        plot.DrawLumi("59.8 fb^{-1} (2018, 13 TeV)")
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    posChannelCategoryLabelLeft = None
    plot.DrawChannelCategoryLabel(
        "%s, %s" % (channel_dict[channel], "inclusive"),
        begin_left=posChannelCategoryLabelLeft)

    # save plot
    if args.category is not None:
        category = args.category
    else:
        category = "Nominal"
    if not args.embedding and not args.fake_factor:
        postfix = "fully_classic"
    if args.embedding and not args.fake_factor:
        postfix = "emb_classic"
    if not args.embedding and args.fake_factor:
        postfix = "classic_ff"
    if args.embedding and args.fake_factor:
        postfix = "emb_ff"
    if args.nlo:
        postfix = "_".join([postfix, "nlo"])
    if args.draw_jet_fake_variation is not None:
        postfix = postfix + "_" + args.draw_jet_fake_variation

    if not os.path.exists("%s_plots_%s"%(args.era,postfix)):
        os.mkdir("%s_plots_%s"%(args.era,postfix))
    if not os.path.exists("%s_plots_%s/%s"%(args.era,postfix,channel)):
        os.mkdir("%s_plots_%s/%s"%(args.era,postfix,channel))
    print("Trying to save the created plot")
    plot.save("%s_plots_%s/%s/%s_%s_%s_%s.%s" % (args.era, postfix, channel, args.era, channel, category, variable, "pdf"))
    plot.save("%s_plots_%s/%s/%s_%s_%s_%s.%s" % (args.era, postfix, channel, args.era, channel, category, variable, "png"))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.DEBUG)
    variables = args.variables.split(",")
    channels = args.channels.split(",")
    infolist = []

    if not args.embedding and not args.fake_factor:
        if args.nlo:
            postfix = "fully_classic_nlo"
        else:
            postfix = "fully_classic"
    if args.embedding and not args.fake_factor:
        if args.nlo:
            postfix = "emb_classic_nlo"
        else:
            postfix = "emb_classic"
    if not args.embedding and args.fake_factor:
        if args.nlo:
            postfix = "classic_ff_nlo"
        else:
            postfix = "classic_ff"
    if args.embedding and args.fake_factor:
        if args.nlo:
            postfix = "emb_ff_nlo"
        else:
            postfix = "emb_ff"

    if not os.path.exists("%s_plots_%s"%(args.era,postfix)):
        os.mkdir("%s_plots_%s"%(args.era,postfix))
    for ch in channels:
        if not os.path.exists("%s_plots_%s/%s"%(args.era,postfix,ch)):
            os.mkdir("%s_plots_%s/%s"%(args.era,postfix,ch))
        for v in variables:
            infolist.append({"args" : args, "channel" : ch, "variable" : v})
    # main(infolist[0])
    pool = Pool(1)
    pool.map(main, infolist)
