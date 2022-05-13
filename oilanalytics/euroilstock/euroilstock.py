import os

import eikon as ek
from commodplot import commodplot as cpl
from commodplot import jinjautils as ju
from dotenv import load_dotenv

# Load environmental variables from '.env' file.
load_dotenv()

eikonkey = os.environ["EIKON_KEY"]
ek.set_app_key(eikonkey)

rics = {
    "CFSL-EU-EBBL": "Crude Stocks",
    "GLSL-EU-EBBL": "Gasoline Stocks",
    "DSTSL-EU-EBBL": "Distillate Stocks",
    "FOSL-EU-EBBL": "Fuel Stocks",
    "NAFSL-EU-EBBL": "Naphtha Stocks",
    "CRI1-EU-EBBL": "Refinery Intake",
    "CRI2-EU-EBBL": "Refinery Intake2",
    "GLRI-EU-EBBL": "Ref Output Gasoline",
    "DSTR-EU-EBBL": "Ref Output Distillate",
    "FORI-EU-EBBL": "Ref Output Fuel",
    "NAFRI-EU-EBBL": "Ref Output Naphtha",
    "REFO-EU-EBBL": "Ref Net Output",
}


def seas_chart(tarser, title):
    f = cpl.seas_line_plot(tarser, title=title, shaded_range=5)
    return f


def generate_euroil_stock_page(out_loc=None):
    if not out_loc:
        out_loc = "Euroil.html"

    data = {"name": "Euroil Stocks", "title": "Euroil Stocks"}
    start_date = "2012-01-01"
    df = ek.get_timeseries(
        list(rics.keys()), fields="Close", start_date=start_date
    ).rename(columns=rics)

    data["Crude Stocks"] = seas_chart(df["Crude Stocks"], title="Crude Stocks")
    data["Refinery Intake"] = seas_chart(df["Refinery Intake"], title="Refinery Intake")

    for product in ["Gasoline", "Distillate", "Naphtha", "Fuel"]:
        stocks = "%s Stocks" % product
        data[stocks] = seas_chart(df[stocks], title=stocks)
        supply = "Ref Output %s" % product
        supply_d = df[supply].dropna()
        data[supply] = seas_chart(supply_d, title=supply)

        # data['%s_supply'] = seas_chart(df[ric[1]].dropna(), title='%s Supply' % product)
        # yield_ = (df[ric[1]].dropna() / df['CRI1-EU-EBBL']).round(2)
        # data['%s_yield'] = seas_chart(pd.DataFrame(yield_), title='%s Supply' % product)

    ju.render_html(
        data,
        "euroilstock.html",
        filename=out_loc,
        package_loader_name="oilanalytics.euroilstock",
    )


if __name__ == "__main__":
    # balance_comparisons()
    generate_euroil_stock_page(r"M:\SitePages\Fundamentals\Euroilstock.aspx")
    # areachart()
