import numpy as np
from ntuple_processor.utils import Selection
from ntuple_processor import Histogram

discriminator_variable = "fj_Xtm_msoftdrop"
discriminator_binning = np.arange(30, 120, 5)
discriminator_binning_enlarged = np.arange(30, 160, 5)


categories = {
    "mt": {
        "fj_wjets_enriched": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(mt_fatjet > 60) && (nbtag==0)",
        },
        "fj_tt_enriched": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(mt_fatjet < 60) && (nbtag>0)",
        },
        "fj_ggH_enriched": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(mt_fatjet < 60) && (nbtag==0)",
        },
    }
}

categorization = {
    "mt": [
        (
            Selection(
                name=x, cuts=[(categories["mt"][x]["cut"], "category_selection")]
            ),
            [
                Histogram(
                    categories["mt"][x]["var"],
                    categories["mt"][x]["expression"],
                    categories["mt"][x]["bins"],
                )
            ],
        )
        for x in categories["mt"]
    ],

}