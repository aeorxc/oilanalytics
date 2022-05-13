import eikon as ek
import pandas as pd
from commodutil import convfactors

from oilanalytics.utils import eikonutils

start_date = "2010-01-01"


def ara_data(start_date=start_date, df: pd.DataFrame = None) -> pd.DataFrame:
    # note crude is from Genscape but subscription is required: 0#GNS-ARC-STOR
    rics = {
        "Gasoline": "STK-GL-ARA",
        "Naphtha": "STK-NAF-ARA",
        "Gasoil": "STK-GO-ARA",
        "FuelOil": "STK-FO-ARA",
        "Jet": "STK-JET-ARA",
    }

    if df is None:
        eikonutils.setup_eikon()
        df = ek.get_timeseries(
            list(rics.values()), fields="Close", start_date=start_date
        )
        df = df.rename(columns=dict((v, k) for k, v in rics.items()))

    if "Crude" in df.columns:
        df["Crude"] = df["Crude"] / 1000
    df["Gasoline"] = (
        convfactors.convert(
            df["Gasoline"], fromunit="kt", tounit="bbl", commodity="gasoline"
        )
        / 1000
    )
    df["Gasoil"] = (
        convfactors.convert(
            df["Gasoil"], fromunit="kt", tounit="bbl", commodity="diesel"
        )
        / 1000
    )
    df["Jet"] = (
        convfactors.convert(df["Jet"], fromunit="kt", tounit="bbl", commodity="jet")
        / 1000
    )
    df["FuelOil"] = (
        convfactors.convert(df["FuelOil"], fromunit="kt", tounit="bbl", commodity="fo")
        / 1000
    )
    df["Naphtha"] = (
        convfactors.convert(
            df["Naphtha"], fromunit="kt", tounit="bbl", commodity="naphtha"
        )
        / 1000
    )

    df.attrs["region"] = "ara"
    return df
