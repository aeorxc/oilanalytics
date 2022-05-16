import pandas as pd
from commodplot import jinjautils as ju
from commodplot.messaging import compose_and_send_jinja_report
from excel_scraper import excel_scraper
from datetime import datetime
import urllib3
import re
from oilanalytics.utils import chartutils as cu

fileloc = "https://ir.eia.gov/wpsr/psw09.xls"

eia_url = "https://www.eia.gov/opendata/qb.php?sdid=PET.%s.W"

sheets_to_parse = [
    "Contents",
    "Data 1",
    "Data 2",
    "Data 3",
    "Data 4",
    "Data 5",
    "Data 6",
    "Data 7",
    "Data 8",
    "Data 9",
    "Data 10",
    "Data 11",
    "Data 14",
    "Data 16",
]


def report_symbols() -> dict:
    """
    Get a list of all the symbols in the Weekly Report
    :return:
    """
    ex = excel_scraper.read_excel_file(fileloc)
    symbols = {}
    for tab in sheets_to_parse:
        if "Data" in tab:
            d = ex.parse(tab, skiprows=[0]).head(1).iloc[0].to_dict()
            symbols = {**symbols, **d}
    return symbols


def read_report() -> pd.DataFrame:
    """
    Read all the timeseries in the report
    :return:
    """
    ex = excel_scraper.read_excel_file(fileloc)
    dfs = []
    for tab in sheets_to_parse:
        if "Data" in tab:
            d = ex.parse(tab, skiprows=[0, 2], index_col=0)
            d = d["2000":]
            # if tab in ['Data 1', 'Data 2', 'Data 6']:
            d = d / 1000
            if tab == "Data 14":
                # d.rename(columns={'WDIRPUS2':'WDIRPUS2_4wk', 'WKJRPUS2':'WKJRPUS2_4wk'}, inplace=True)

                d.rename(columns={"WDIRPUS2": "WDIRPUS2_4wk"}, inplace=True)
                d = d["WDIRPUS2_4wk"]
            if tab == "Data 16":
                d.rename(
                    columns={"W_EPOOXE_YOP_NUS_MBBLD": "W_EPOOXE_YOP_NUS_MBBLD_4wk"},
                    inplace=True,
                )
                d = d["W_EPOOXE_YOP_NUS_MBBLD_4wk"]

            dfs.append(d)
        else:
            d = ex.parse(tab)
            ind_row = 27
            ind_col = 2
            # Check that the values we have match the location of 'Release Date:' in the file
            rl_date_ind = int(d[d.eq("Release Date:").any(1)].index.values)
            if rl_date_ind == ind_row:
                release_date = pd.to_datetime(d.iloc[ind_row][ind_col], dayfirst=False)
            else:
                raise ValueError("Row indexes do not match")
    res = pd.concat(dfs, axis=1)

    res["Gas Yield"] = (res["W_EPM0F_YPR_NUS_MBBLD"] / res["WCRRIUS2"]) * 100
    res["Non Oxy Yield"] = (
        (res["W_EPM0F_YPR_NUS_MBBLD"] - res["W_EPOOXE_YOP_NUS_MBBLD"]) / res["WCRRIUS2"]
    ) * 100
    res["Dist Yield"] = (res["WDIRPUS2"] / res["WCRRIUS2"]) * 100

    res["mogas_dc"] = (res["WGTSTUS1"] / res["WGFUPUS2"]).rolling(window=4).mean()
    res["distillate_dc"] = (res["WDISTUS1"] / res["WDIRPUS2"]).rolling(window=4).mean()
    res["jet_dc"] = (res["WKJSTUS1"] / res["WKJUPUS2"]).rolling(window=4).mean()

    return res, release_date


def gen_page(
    title: str, template: str, filename: str = None, report_data: pd.DataFrame = None
):
    data = {"name": title, "title": title, "eia_url": eia_url}

    if report_data is None:
        report_data = read_report()
    data["report"], data["release_date"] = report_data

    return ju.render_html(
        data,
        template=template,
        filename=filename,
        package_loader_name="oilanalytics.eia",
        template_globals={"cu": cu},
    )


def gen_summary_charts(filename, report_data=None):
    data = {
        "name": "DOE Weekly Quick Report",
        "title": "DOE Weekly Quick",
        "eia_url": eia_url,
    }

    if report_data is None:
        report_data = read_report()
    data["report"] = report_data

    return ju.render_html(
        data,
        "doe_weekly_em.html",
        filename=filename,
        package_loader_name="oilanalytics.eia",
        template_globals={"cu": cu},
    )


def gen_and_send_email(
    report_data=None,
    sender_email: str = None,
    receiver_email: str = None,
    dashboard_link: str = None,
):
    data = {
        "name": "DOE Weekly Petroleum Report",
        "title": "DOE Weekly",
        "eia_url": eia_url,
    }
    if report_data is None:
        report_data = read_report()[0]

    summary_table_items = {
        "WCESTUS1": "Crude Stocks",
        "W_EPC0_SAX_YCUOK_MBBL": "Cushing Stocks",
        "WGTSTUS1": "Mogas Stocks",
        "WDISTUS1": "Distillate Stocks",
        "WGFUPUS2": "Mogas Demand",
        "WDIUPUS2": "Distillate Demand",
        "WCRFPUS2": "Crude Supply",
        "WCREXUS2": "Crude Exports",
        "WCRRIUS2": "Runs",
    }

    df_sum = report_data[summary_table_items.keys()].rename(columns=summary_table_items)
    data["summary_table"] = cu.gen_wow_summary_table(df_sum)

    for key, title in summary_table_items.items():
        data[title] = cu.seas_chart_weekly(df=report_data, series=key, title=title)

    if dashboard_link:
        data["dashboard_link"] = f'<a href="{dashboard_link}">Link to Dashboard</a>'

    compose_and_send_jinja_report(
        "DOE EIA Weekly Report",
        data=data,
        template="doe_weekly_email.html",
        package_loader_name="oilanalytics.eia",
        receiver_email=receiver_email,
        sender_email=sender_email,
    )


def extract_release_date(url: str) -> datetime.date:
    """
    Given a url, extract the release date to allow comparisons between runs and detect if report has been updated
    :param url:
    :return:
    """

    http = urllib3.PoolManager(cert_reqs="CERT_NONE", assert_hostname=False)
    pg = http.request("GET", url)

    # Get html docstring
    pg_data = str(pg.data)
    x = re.search("\d{1,2}-[a-zA-Z]{3}-\d{4}", pg_data)
    if x:
        release_date = datetime.strptime(x[0], "%d-%b-%Y")
        return release_date


if __name__ == "__main__":
    gen_page(
        title="DOE Weekly Report",
        template="templates/doe_weekly_summary.html",
        filename=r"summary.html",
    )
    gen_page(
        title="DOE Weekly Report - Refineries",
        template="doe_weekly_refineries.html",
        filename=r"refineries.html",
    )
    gen_page(
        title="DOE Weekly Report - Distillates",
        template="doe_weekly_distillates.html",
        filename=r"distillates.html",
    )
    gen_page(
        title="DOE Weekly Report - Jet",
        template="doe_weekly_jet.html",
        filename=r"jet.html",
    )
    gen_page(
        title="DOE Weekly Report - Fuel",
        template="doe_weekly_fuel.html",
        filename=r"fuel.html",
    )
    gen_page(
        title="DOE Weekly Report - LPG",
        template="doe_weekly_lpg.html",
        filename=r"lpg.html",
    )
    gen_page(
        title="DOE Weekly Report - Ethanol",
        template="doe_weekly_ethanol.html",
        filename=r"ethanol.html",
    )
    gen_page(
        title="DOE Weekly Report - Crude",
        template="doe_weekly_crude.html",
        filename=r"crude.html",
    )
    gen_page(
        title="DOE Weekly Report - Gasoline",
        template="doe_weekly_gasoline.html",
        filename=r"gasoline.html",
    )
