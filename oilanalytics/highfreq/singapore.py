import logging

import eikon as ek
import pandas as pd
from commodplot import jinjautils as ju

from oilanalytics.utils import chartutils as cu
from oilanalytics.utils import eikonutils

start_date = "2010-01-01"


def singapore_data(start_date=start_date, df: pd.DataFrame = None) -> pd.DataFrame:
    rics = {
        "LightDistillates": "STKLD-SIN",
        "MiddleDistillates": "STKMD-SIN",
        "HeavyDistillates": "STKRS-SIN",
    }

    if df is None:
        eikonutils.setup_eikon()
        df = ek.get_timeseries(
            list(rics.values()), fields="Close", start_date=start_date
        )
        df = df.rename(columns=dict((v, k) for k, v in rics.items()))

    df = df / 1000  # kbbl to mbbl
    df.attrs["region"] = "singapore"
    return df


def generate_singapore_page(df_data=None, out_loc: str = None):
    logging.info("generating singapore page")
    if df_data is None:
        df_data = singapore_data()

    data = {"name": "Singapore", "title": "Singapore", "df_input": df_data}

    ju.render_html(
        data,
        "singapore.html",
        filename=out_loc,
        package_loader_name="oilfundamentals.highfrequency",
        template_globals={"cu": cu},
    )
