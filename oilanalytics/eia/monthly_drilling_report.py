import pandas as pd
from commodplot import jinjautils as ju
from commodplot.messaging import compose_and_send_jinja_report
from excel_scraper import excel_scraper
from datetime import datetime
import re
import requests
from oilanalytics.utils import chartutils as cu
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from commodplot import commodplot as cpl
from bs4 import BeautifulSoup
import urllib.request as urllib2

filenames = ["dpr-data", "duc-data"]
fileloc = "https://www.eia.gov/petroleum/drilling//xls/%s.xlsx"

eia_webpage = "https://www.eia.gov/petroleum/drilling/"

sheets_to_graph = ["Bakken Region", "Eagle Ford Region", "Permian Region"]

all_sheets = [
    "Anadarko Region",
    "Appalachia Region",
    "Bakken Region",
    "Eagle Ford Region",
    "Haynesville Region",
    "Niobrara Region",
    "Permian Region",
]


def read_release_date():
    r = urllib2.urlopen(eia_webpage).read()
    x = []
    soup = BeautifulSoup(r, "html.parser")
    result = soup.find_all("span", {"class": "date"})[0].text.strip()
    if result:
        release_date = datetime.strptime(result, "%B %d, %Y")
    return release_date


def create_dualaxis_graph(df, title=None):
    # ensure that the DF is of format index / secondary axis col / primary axis col
    tf_list = [True, False]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col, tf in zip(df.columns, tf_list):
        if tf is False:
            fig.add_trace(go.Bar(x=df.index, y=df[col], name=col), secondary_y=tf)
        else:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), secondary_y=tf)
        fig.update_yaxes(title_text=col, secondary_y=tf, showgrid=not tf)
    fig.update_layout(title=title)
    return fig


def read_rig_report(name):
    filename = fileloc % name
    ex = excel_scraper.read_excel_file(filename)
    tot_prod_list = []
    graphs = []
    for tab in sheets_to_graph:
        d = ex.parse(tab, index_col=0).iloc[:, :4]
        # reorganise the DF (as parameters don't work in parse)
        new_header = d.iloc[0]
        d = d.iloc[1:]
        d.columns = new_header
        title = d.index.name
        d.index.name = None
        tot_prod_list.append(d["Total production"].rename(title))
        fig = create_dualaxis_graph(
            d[["Production per rig", "Rig count"]], title=f"{title} Rig Count"
        )
        graphs.append(fig)
        d["MoM"] = d["Total production"] - d["Total production"].shift(1)
        fig_mom = create_dualaxis_graph(
            d[["Total production", "MoM"]], title=f"{title} Production"
        )
        graphs.append(fig_mom)
    total_prod = pd.concat(tot_prod_list, axis=1)
    fig = cpl.seas_line_plot(
        total_prod.sum(axis=1).astype(float),
        title="Total Shale Production - 3 Main Plays",
        precision_format="{0:,.0f}",
    )
    graphs.append(fig)
    total_prod["YoY Changes"] = total_prod.sum(axis=1) - total_prod.sum(axis=1).shift(
        12
    )
    total_prod["YoY Average Changes"] = (
        total_prod["YoY Changes"].rolling(window=12).mean()
    )
    fig = cpl.bar_line_plot(
        total_prod[["YoY Changes", "YoY Average Changes"]],
        linecol="YoY Average Changes",
        title="US Shale Production",
    )
    graphs.append(fig)
    return graphs


def read_duc_report(name):
    filename = fileloc % name
    ex = excel_scraper.read_excel_file(filename)
    d = ex.parse("Data", index_col=0)
    header = pd.MultiIndex.from_product(
        [
            [x.strip() for x in list(d.iloc[1]) if str(x) != "nan"],
            list(
                dict.fromkeys([x.strip() for x in list(d.iloc[2]) if str(x) != "nan"])
            ),
        ],
        names=["loc", "drill_type"],
    )
    d.dropna(axis=1, how="all", inplace=True)
    d.columns = header
    d = d.iloc[3:]
    locs = [x.replace(" Region", "") for x in sheets_to_graph]
    graphs = []
    for loc in locs:
        df = d.xs(loc, level="loc", axis=1)
        fig = cpl.seas_line_plot(
            df["DUC"].astype(float), shaded_range=[2017, 2020], title=f"{loc} DUCs"
        )
        graphs.append(fig)
    return graphs


def get_jinja_dict():
    data = {"title": "EIA Productivity Report", "name": "EIA Productivity Report"}
    data["release_date"] = read_release_date()
    data["rig_charts"] = read_rig_report(filenames[0])
    data["duc_charts"] = read_duc_report(filenames[1])

    return data


def generate_page(filename=None):
    return ju.render_html(
        data=get_jinja_dict(),
        template="monthly_drilling_report.html",
        filename=filename,
        package_loader_name="oilanalytics.eia",
        template_globals={"cu": cu},
    )


def generate_email():
    compose_and_send_jinja_report(
        "EIA Productivity Report",
        data=get_jinja_dict(),
        template="monthly_drilling_report_email.html",
        package_loader_name="oilanalytics.eia",
        template_globals={"cu": cu},
    )


if __name__ == "__main__":
    proxy_support = urllib2.ProxyHandler(
        {"http": "http://proxy-rwest-uk.energy.local:8080"}
    )
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
    # graphs = read_rig_report(filenames[0])
    generate_page("test.html")
    # date = read_release_date()
    # generate_email()
