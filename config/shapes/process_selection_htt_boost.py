from ntuple_processor.utils import Selection


"""Base processes

List of base processes, mostly containing only weights:
    - triggerweight
    - triggerweight_emb
    - tau_by_iso_id_weight
    - ele_hlt_Z_vtx_weight
    - ele_reco_weight
    - aiso_muon_correction
    - lumi_weight
    - MC_base_process_selection
    - DY_base_process_selection
    - TT_process_selection
    - VV_process_selection
    - W_process_selection
    - HTT_base_process_selection
    - HTT_process_selection
    - HWW_process_selection
"""


def lumi_weight(era):
    if era == "2016preVFP":
        lumi = "19.5"  # "36.326450080"
    elif era == "2016postVFP":
        lumi = "16.8"
    elif era == "2017":
        lumi = "41.529"
    elif era == "2018":
        lumi = "59.83"
    else:
        raise ValueError("Given era {} not defined.".format(era))
    return ("{} * 1000.0".format(lumi), "lumi")


def prefiring_weight(era):
    if era in ["2016postVFP", "2016preVFP", "2017"]:
        weight = ("prefiring_wgt", "prefireWeight")
    else:
        weight = ("1.0", "prefireWeight")
    return weight


def MC_base_process_selection(channel, era, boosted_tau=False):
    if channel == "em":
        isoweight = None
        idweight = None
        tauidweight = None
        vsmu_weight = None
        vsele_weight = None
        trgweight = None
    elif channel == "et":
        isoweight = ("iso_wgt_ele_1", "isoweight")
        idweight = ("id_wgt_ele_1", "idweight")
        tauidweight = (
            "((fatjet_gen_match_2==5)*id_wgt_tau_vsJet_Tight_2 + (fatjet_gen_match_2!=5))",
            "taubyIsoIdWeight",
        )
        vsmu_weight = ("id_wgt_tau_vsMu_VLoose_2", "vsmuweight")
        vsele_weight = ("id_wgt_tau_vsEle_Tight_2", "vseleweight")
        if era == "2017":
            trgweight = (
                "((pt_1>=33&&pt_1<36)*trg_wgt_single_ele32)+((pt_1>=36)*trg_wgt_single_ele35)",
                "trgweight",
            )
        else:
            trgweight = ("trg_wgt_single_ele32orele35", "trgweight")
    elif channel == "mt":
        if not boosted_tau:
            isoweight = ("iso_wgt_good_mu_1", "isoweight")
            idweight = ("id_wgt_good_mu_1", "idweight")
            tauidweight = (
                "((fatjet_gen_match_2==5)*id_wgt_tau_vsJet_Medium_2 + (fatjet_gen_match_2!=5))",
                "taubyIsoIdWeight",
            )
            vsmu_weight = ("id_wgt_tau_vsMu_Tight_2", "vsmuweight")
            vsele_weight = ("id_wgt_tau_vsEle_VVLoose_2", "vseleweight")
            if era == "2016preVFP" or era == "2016postVFP":
                trgweight = ("((pt_1>23)* trg_wgt_single_mu22)", "trgweight")
            elif era == "2017":
                trgweight = ("((pt_1>28)* trg_wgt_single_mu27)", "trgweight")
            else:
                trgweight = (
                    "((pt_1>=25 && pt_1<28)* trg_wgt_single_mu24) + ((pt_1>28)* trg_wgt_single_mu27)",
                    "trgweight",
                )
        elif boosted_tau:
            isoweight = None
            idweight = None
            tauidweight = None
            vsmu_weight = None
            vsele_weight = None
            if era == "2016preVFP" or era == "2016postVFP":
                trgweight = None
            elif era == "2017":
                trgweight = ("((pt_1>28)* trg_wgt_single_mu27)", "trgweight")
            else:
                trgweight = None
    elif channel == "tt":
        isoweight = None
        idweight = None
        tauidweight = (
            "((fatjet_gen_match_1==5)*id_wgt_tau_vsJet_Tight_1 + (fatjet_gen_match_1!=5)) * ((fatjet_gen_match_2==5)*id_wgt_tau_vsJet_Tight_2 + (fatjet_gen_match_2!=5))",
            "taubyIsoIdWeight",
        )
        vsmu_weight = (
            "((fatjet_gen_match_1==5)*id_wgt_tau_vsMu_VLoose_1 + (fatjet_gen_match_1!=5)) * ((fatjet_gen_match_2==5)*id_wgt_tau_vsMu_VLoose_1 + (fatjet_gen_match_2!=5))",
            "vsmuweight",
        )
        vsele_weight = (
            "((fatjet_gen_match_1==5)*id_wgt_tau_vsEle_VVLoose_1 + (fatjet_gen_match_1!=5)) * ((fatjet_gen_match_2==5)*id_wgt_tau_vsEle_VVLoose_1 + (fatjet_gen_match_2!=5))",
            "vseleweight",
        )
        trgweight = None
    elif channel == "mm":
        isoweight = ("iso_wgt_good_mu_1 * iso_wgt_mu_2", "isoweight")
        idweight = ("id_wgt_good_mu_1 * id_wgt_mu_2", "idweight")
        tauidweight = None
        vsmu_weight = None
        vsele_weight = None
        if era == "2017":
            trgweight = ("trg_wgt_single_mu27", "trgweight")
        elif era == "2018":
            trgweight = ("1", "trgweight")
        elif era == "2016postVFP" or era == "2016preVFP":
            trgweight = ("trg_wgt_single_mu22", "trgweight")
    elif channel == "ee":
        isoweight = ("iso_wgt_ele_1 * iso_wgt_ele_2", "isoweight")
        idweight = ("id_wgt_ele_1 * id_wgt_ele_2", "idweight")
        tauidweight = None
        vsmu_weight = None
        vsele_weight = None
        if era == "2017":
            trgweight = ("trg_wgt_single_ele35", "trgweight")
        elif era == "2018":
            trgweight = ("trg_wgt_single_ele35", "trgweight")
        elif era in ["2016postVFP", "2016preVFP"]:
            trgweight = ("trg_wgt_single_ele25", "trgweight")
    else:
        raise ValueError("Given channel {} not defined.".format(channel))
    MC_base_process_weights = [
        ("puweight", "puweight"),
        isoweight,
        idweight,
        tauidweight,
        vsmu_weight,
        vsele_weight,
        trgweight,
        lumi_weight(era),
        prefiring_weight(era),
    ]
    if channel != "mm" and channel != "mt":
        MC_base_process_weights.append(("btag_weight", "btagWeight"))
    print("%%%%%%%%%%%%%%%%%%% MC base process weights: ", MC_base_process_weights)
    return Selection(
        name="MC base",
        weights=[weight for weight in MC_base_process_weights if weight is not None],
    )


def dy_stitching_weight(era):
    if era == "2017":
        weight = (
            "((genbosonmass >= 50.0)*0.0000298298*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.3478960398 + (npartons == 2)*0.2909516577 + (npartons == 3)*0.1397995594 + (npartons == 4)*0.1257217076) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
            "dy_stitching_weight",
        )
        # xsec_NNLO [pb] = , N_inclusive = 203,729,540, xsec_NNLO/N_inclusive = 0.0000298298 [pb], weights: [1.0, 0.3478960398, 0.2909516577, 0.1397995594, 0.1257217076]
    elif era == "2018":
        weight = (
            "((genbosonmass >= 50.0)*0.0000606542*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.194267667208 + (npartons == 2)*0.21727746547 + (npartons == 3)*0.26760465744 + (npartons == 4)*0.294078683662) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
            "dy_stitching_weight",
        )
        # xsec_NNLO [pb] = 2025.74*3, N_inclusive = 100194597,  xsec_NNLO/N_inclusive = 0.0000606542 [pb] weights: [1.0, 0.194267667208, 0.21727746547, 0.26760465744, 0.294078683662]
    else:
        raise ValueError("DY stitching weight not defined for era {}".format(era))

    return weight


def DY_process_selection(channel, era, boosted_tau):
    DY_process_weights = MC_base_process_selection(channel, era, boosted_tau).weights
    if era == "2017":
        gen_events_weight = (
            "(1./203729540)*(genbosonmass >= 50.0) + (genbosonmass < 50.0)*numberGeneratedEventsWeight",
            "numberGeneratedEventsWeight",
        )
    elif era == "2018":
        gen_events_weight = (
            "numberGeneratedEventsWeight",
            "numberGeneratedEventsWeight",
        )
    elif era in ["2016preVFP", "2016postVFP"]:
        gen_events_weight = (
            "numberGeneratedEventsWeight",
            "numberGeneratedEventsWeight",
        )
    DY_process_weights.extend(
        [
            gen_events_weight,
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            # dy_stitching_weight(era),  # TODO add stitching weight
            # ("ZPtMassReweightWeight", "zPtReweightWeight"),
            # ("1", "zPtReweightWeight"),

        ]
    )
    return Selection(name="DY", weights=DY_process_weights)


def DY_NLO_process_selection(channel, era, boosted_tau):
    DY_process_weights = MC_base_process_selection(channel, era, boosted_tau).weights
    DY_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            # dy_stitching_weight(era),  # TODO add stitching weight
            # ("ZPtMassReweightWeight", "zPtReweightWeight"),
        ]
    )
    return Selection(name="DY_NLO", weights=DY_process_weights)


def TT_process_selection(channel, era, boosted_tau):
    TT_process_weights = MC_base_process_selection(channel, era, boosted_tau).weights
    TT_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            ("topPtReweightWeight", "topPtReweightWeight"),
        ]
    )
    return Selection(name="TT", weights=TT_process_weights)


def VV_process_selection(channel, era,boosted_tau):
    VV_process_weights = MC_base_process_selection(channel, era, boosted_tau).weights
    VV_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
        ]
    )
    return Selection(name="VV", weights=VV_process_weights)


def W_stitching_weight(era):
    if era == "2018":
        weight = (
            "((0.0008662455*((npartons <= 0 || npartons >= 5)*1.0 + (npartons == 1)*0.174101755934 + (npartons == 2)*0.136212630745 + (npartons == 3)*0.0815667415121 + (npartons == 4)*0.06721295702670023)) * (genbosonmass>=0.0) + numberGeneratedEventsWeight * crossSectionPerEventWeight * (genbosonmass<0.0))",
            "wj_stitching_weight",
        )
        # xsec_NNLO [pb] = 61526.7, N_inclusive = 71026861, xsec_NNLO/N_inclusive = 0.0008662455 [pb] weights: [1.0, 0.1741017559343336, 0.13621263074538312, 0.08156674151214884, 0.06721295702670023]
    else:
        raise ValueError("DY stitching weight not defined for era {}".format(era))
    return weight


def W_process_selection(channel, era, boosted_tau):
    W_process_weights = MC_base_process_selection(channel, era, boosted_tau).weights
    W_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            # ("0.00001", "normalizationWeight"),  #you should not use this weight for the final result
        ]
    )
    # W_process_weights.append(W_stitching_weight(era)) # TODO add W stitching weight in when npartons is available
    return Selection(name="W", weights=W_process_weights)



# """Built-on-top processes

# List of other processes meant to be put on top of base processes:
#     - DY_process_selection
#     - DY_nlo_process_selection
#     - ZTT_process_selection
#     - ZTT_nlo_process_selection
#     - ZTT_embedded_process_selection
#     - ZL_process_selection
#     - ZL_nlo_process_selection
#     - ZJ_process_selection
#     - ZJ_nlo_process_selection
#     - TTT_process_selection
#     - TTL_process_selection
#     - TTJ_process_selection
#     - VVT_process_selection
#     - VVJ_process_selection
#     - VVL_process_selection
#     - VH_process_selection
#     - WH_process_selection
#     - ZH_process_selection
#     - ttH_process_selection
#     - ggH125_process_selection
#     - qqH125_process_selection
#     - ggHWW_process_selection
#     - qqHWW_process_selection
#     - ZHWW_process_selection
#     - WHWW_process_selection
#     - SUSYqqH_process_selection
#     - SUSYbbH_process_selection
# """



# def ZTT_process_selection(channel):
#     tt_cut = __get_ZTT_cut(channel)
#     return Selection(name="ZTT", cuts=[(tt_cut, "ztt_cut")])


# def ZTT_nlo_process_selection(channel):
#     tt_cut = __get_ZTT_cut(channel)
#     return Selection(name="ZTT_nlo", cuts=[(tt_cut, "ztt_cut")])


# def __get_ZTT_cut(channel):
#     if "mt" in channel:
#         return "fatjet_gen_match_1==4 && fatjet_gen_match_2==5"
#     elif "et" in channel:
#         return "fatjet_gen_match_1==3 && fatjet_gen_match_2==5"
#     elif "tt" in channel:
#         return "fatjet_gen_match_1==5 && fatjet_gen_match_2==5"
#     elif "em" in channel:
#         return "fatjet_gen_match_1==3 && fatjet_gen_match_2==4"
#     elif "mm" in channel:
#         return "fatjet_gen_match_1==4 && fatjet_gen_match_2==4"
#     elif "ee" in channel:
#         return "fatjet_gen_match_1==3 && fatjet_gen_match_2==3"



# def ZL_process_selection(channel):
#     veto = __get_ZL_cut(channel)
#     return Selection(
#         name="ZL",
#         cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
#     )


# def ZL_nlo_process_selection(channel):
#     veto = __get_ZL_cut(channel)
#     return Selection(
#         name="ZL_nlo",
#         cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
#     )


# def __get_ZL_cut(channel):
#     emb_veto = ""
#     ff_veto = ""
#     if "mt" in channel:
#         emb_veto = "!(fatjet_gen_match_1==4 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_2 == 6)"
#     elif "et" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_2 == 6)"
#     elif "tt" in channel:
#         emb_veto = "!(fatjet_gen_match_1==5 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_1 == 6 || fatjet_gen_match_2 == 6)"
#     elif "em" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==4)"
#         ff_veto = "(1.0)"
#     elif "mm" in channel:
#         emb_veto = "!(fatjet_gen_match_1==4 && fatjet_gen_match_2==4)"
#         ff_veto = "(1.0)"
#     elif "ee" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==3)"
#         ff_veto = "(1.0)"
#     return (emb_veto, ff_veto)


# def ZJ_process_selection(channel):
#     veto = __get_ZJ_cut(channel)
#     return Selection(name="ZJ", cuts=[(__get_ZJ_cut(channel), "dy_fakes")])


# def ZJ_nlo_process_selection(channel):
#     veto = __get_ZJ_cut(channel)
#     return Selection(name="ZJ_nlo", cuts=[(__get_ZJ_cut(channel), "dy_fakes")])


# def __get_ZJ_cut(channel):
#     if "mt" in channel or "et" in channel:
#         return "fatjet_gen_match_2 == 6"
#     elif "tt" in channel:
#         return "(fatjet_gen_match_1 == 6 || fatjet_gen_match_2 == 6)"
#     elif "em" in channel:
#         return "0 == 1"
#     elif "mm" in channel:
#         return "0 == 1"
#     elif "ee" in channel:
#         return "0 == 1"
#     else:
#         return ""


# def TTT_process_selection(channel):
#     tt_cut = ""
#     if "mt" in channel:
#         tt_cut = "fatjet_gen_match_1==4 && fatjet_gen_match_2==5"
#     elif "et" in channel:
#         tt_cut = "fatjet_gen_match_1==3 && fatjet_gen_match_2==5"
#     elif "tt" in channel:
#         tt_cut = "fatjet_gen_match_1==5 && fatjet_gen_match_2==5"
#     elif "em" in channel:
#         tt_cut = "fatjet_gen_match_1==3 && fatjet_gen_match_2==4"
#     elif "mm" in channel:
#         tt_cut = "fatjet_gen_match_1==4 && fatjet_gen_match_2==4"
#     elif "ee" in channel:
#         tt_cut = "fatjet_gen_match_1==3 && fatjet_gen_match_2==3"
#     return Selection(name="TTT", cuts=[(tt_cut, "ttt_cut")])


# def TTL_process_selection(channel):
#     emb_veto = ""
#     ff_veto = ""
#     if "mt" in channel:
#         emb_veto = "!(fatjet_gen_match_1==4 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_2 == 6)"
#     elif "et" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_2 == 6)"
#     elif "tt" in channel:
#         emb_veto = "!(fatjet_gen_match_1==5 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_1 == 6 || fatjet_gen_match_2 == 6)"
#     elif "em" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==4)"
#         ff_veto = "(1.0)"
#     elif "mm" in channel:
#         emb_veto = "!(fatjet_gen_match_1==4 && fatjet_gen_match_2==4)"
#         ff_veto = "(1.0)"
#     elif "ee" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==3)"
#         ff_veto = "(1.0)"
#     return Selection(
#         name="TTL",
#         cuts=[
#             ("{}".format(emb_veto), "tt_emb_veto"),
#             ("{}".format(ff_veto), "ff_veto"),
#         ],
#     )


# def TTJ_process_selection(channel):
#     ct = ""
#     if "mt" in channel or "et" in channel:
#         ct = "(fatjet_gen_match_2 == 6 && fatjet_gen_match_2 == 6)"
#     elif "tt" in channel:
#         ct = "(fatjet_gen_match_1 == 6 || fatjet_gen_match_2 == 6)"
#     elif "em" in channel:
#         ct = "0 == 1"
#     elif "mm" in channel or "ee" in channel:
#         ct = "0 == 1"
#     return Selection(name="TTJ", cuts=[(ct, "tt_fakes")])


# def VVT_process_selection(channel):
#     tt_cut = ""
#     if "mt" in channel:
#         tt_cut = "fatjet_gen_match_1==4 && fatjet_gen_match_2==5"
#     elif "et" in channel:
#         tt_cut = "fatjet_gen_match_1==3 && fatjet_gen_match_2==5"
#     elif "tt" in channel:
#         tt_cut = "fatjet_gen_match_1==5 && fatjet_gen_match_2==5"
#     elif "em" in channel:
#         tt_cut = "fatjet_gen_match_1==3 && fatjet_gen_match_2==4"
#     elif "mm" in channel:
#         tt_cut = "fatjet_gen_match_1==4 && fatjet_gen_match_2==4"
#     elif "ee" in channel:
#         tt_cut = "fatjet_gen_match_1==3 && fatjet_gen_match_2==3"
#     return Selection(name="VVT", cuts=[(tt_cut, "vvt_cut")])


# def VVJ_process_selection(channel):
#     ct = ""
#     if "mt" in channel or "et" in channel:
#         ct = "(fatjet_gen_match_2 == 6 && fatjet_gen_match_2 == 6)"
#     elif "tt" in channel:
#         ct = "(fatjet_gen_match_1 == 6 || fatjet_gen_match_2 == 6)"
#     elif "em" in channel:
#         ct = "0.0 == 1.0"
#     elif "mm" in channel or "ee" in channel:
#         ct = "0.0 == 1.0"
#     return Selection(name="VVJ", cuts=[(ct, "vv_fakes")])


# def VVL_process_selection(channel):
#     emb_veto = ""
#     ff_veto = ""
#     if "mt" in channel:
#         emb_veto = "!(fatjet_gen_match_1==4 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_2 == 6)"
#     elif "et" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_2 == 6)"
#     elif "tt" in channel:
#         emb_veto = "!(fatjet_gen_match_1==5 && fatjet_gen_match_2==5)"
#         ff_veto = "!(fatjet_gen_match_1 == 6 || fatjet_gen_match_2 == 6)"
#     elif "em" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==4)"
#         ff_veto = "(1.0)"
#     elif "mm" in channel:
#         emb_veto = "!(fatjet_gen_match_1==4 && fatjet_gen_match_2==4)"
#         ff_veto = "(1.0)"
#     elif "ee" in channel:
#         emb_veto = "!(fatjet_gen_match_1==3 && fatjet_gen_match_2==3)"
#         ff_veto = "(1.0)"
#     return Selection(
#         name="VVL",
#         cuts=[
#             ("{}".format(emb_veto), "tt_emb_veto"),
#             ("{}".format(ff_veto), "ff_veto"),
#         ],
#     )


