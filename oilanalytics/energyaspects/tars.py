### Note the way this gets data via the EA excel file should be deprecated
### now that data is available via API


from os import getenv

import cachetools.func
import pandas as pd
import plotly.graph_objects as go
from commodplot import commodplot as cpl
from commodplot import jinjautils as ju
from commodutil import dates
from dotenv import load_dotenv
from excel_scraper import excel_scraper

from oilanalytics.utils import fileutils

# Load environmental variables from '.env' file.
load_dotenv()


def tar_to_timeseries(taramount, startdate, enddate, tarname=None):
    dr = pd.date_range("01/01/2015", "01/01/2025")
    ser = pd.Series(0, index=dr)
    ser[startdate:enddate] = taramount
    ser.name = tarname
    return ser


@cachetools.func.ttl_cache(maxsize=1, ttl=100 * 60)
def read_tars_excel():
    folder = getenv("EA_TARS_FOLDER")
    fileloc = fileutils.find_latest_file(folder)
    ex = excel_scraper.read_excel_file(fileloc)
    df = ex.parse("Refinery outages")
    df = df.rename(
        columns={x: x.lower() for x in df.columns}
    )  # make col headings lower case for consistency
    for col in [
        "region",
        "country",
        "planned/unplanned",
    ]:  # same with the column entries
        df[col] = df[col].str.lower()
    return df


@cachetools.func.ttl_cache(ttl=100 * 60)
def convert_table_to_tar_series(value_col="unit capacity"):
    tar_table = read_tars_excel()
    tarser = tar_table.apply(
        lambda x: tar_to_timeseries(
            x[value_col], x["start date"], x["end date"], x.name
        ),
        1,
    )
    tarser = tarser / 1000000
    return tarser


def tar_series(
    unittype="CDU",
    region=None,
    freq="MS",
    sum=True,
    value_col="unit capacity",
    planned=None,
):
    if region == "global":
        region = None

    df = read_tars_excel()
    tarser = convert_table_to_tar_series(value_col=value_col)
    df1 = df[df["unit type"] == unittype]
    if region is not None:
        df1 = df1[df1["region"] == region]

    if planned:
        if planned == "planned":
            df1 = df1[df1["planned/unplanned"] == "planned"]
            df1 = df1[df1["unplanned"] == "unplanned"]

    tarser = tarser[tarser.index.isin(df1.index)]  # filter tarser to same ids as df1
    if sum:
        tf = tarser[tarser.index.isin(df1.index)].sum()
        tf = tf.resample(freq).mean()
    else:
        tf = tarser[tarser.index.isin(df1.index)]

    return tf


def seas_chart(tarser, title):
    f = cpl.seas_line_plot(tarser, title=title, inc_change_sum=False)
    return f


def generate_ea_tars_page(out_loc=None):
    if not out_loc:
        out_loc = "TarsDashboard.html"

    data = {"name": "TARs Dashboard", "title": "Tars Dashboard"}
    data["global_cdu_tars"] = seas_chart(
        tar_series("CDU", region="global"), title="Global CDU Tars"
    )
    data["global_cdu_runs_impact"] = seas_chart(
        tar_series("CDU", region="global", value_col="estimated runs impact"),
        title="Estimates runs impact",
    )

    data["global_fcc_tars"] = seas_chart(
        tar_series("CDU", region="global"), title="Global FCC Tars"
    )
    data["global_hcu_tars"] = seas_chart(
        tar_series("HCU", region="global"), title="Global Hydrocrakcer Tars"
    )
    data["global_cok_tars"] = seas_chart(
        tar_series("COK", region="global"), title="Global Coker Tars"
    )
    ju.render_html(
        data,
        "tars_dashboard.html",
        filename=out_loc,
        package_loader_name="oilanalytics.energyaspects",
    )


def areachart(tarser, title):
    f = tarser.T[dates.curyear :]
    f = f.loc[:, (f != 0).any(axis=0)]  # remove all 0 columns
    fig = go.Figure()

    for col in f.columns:
        fig.add_trace(go.Scatter(x=f.index, y=f[col], stackgroup="one"))
    fig.update_layout(title=title)
    return fig


if __name__ == "__main__":
    # balance_comparisons()
    generate_ea_tars_page()
    # areachart()
