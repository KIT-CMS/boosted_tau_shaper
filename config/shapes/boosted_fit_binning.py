import numpy as np
from ntuple_processor.utils import Selection
from ntuple_processor import Histogram

discriminator_variable = "fj_Xtm_msoftdrop"
discriminator_binning = np.arange(30, 120, 5)
discriminator_binning_enlarged = np.arange(30, 160, 5)


categories = {
    "mt": {
        "fj_softdrop_50_90": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(fj_Xtm_msoftdrop >= 50) && (fj_Xtm_msoftdrop < 90)",
        },
        "fj_softdrop_90_120": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(fj_Xtm_msoftdrop >= 90) && (fj_Xtm_msoftdrop < 120)",
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