import re
from datetime import datetime
from commodutil import pandasutil as pdu
import pandas as pd
import urllib3
from commodplot import jinjautils as ju
from commodplot.messaging import compose_and_send_jinja_report
from excel_scraper import excel_scraper
from myeia.api import API

from oilanalytics.utils import chartutils as cu

fileloc_09 = "https://ir.eia.gov/wpsr/psw09.xls"

fileloc_01 = "https://ir.eia.gov/wpsr/psw01.xls"

fileloc_05a = "https://ir.eia.gov/wpsr/psw05a.xls"

fileloc_08 = "https://ir.eia.gov/wpsr/psw08.xls"

# canada_importa_file_loc = (
#     "https://www.eia.gov/dnav/pet/hist_xls/W_EPC0_IM0_NUS-NCA_MBBLDw.xls"
# )

eia_url = "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=%s&f=W"
file_09_sheets_to_parse = [
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


monthly_report_codes = [
    # https://www.eia.gov/dnav/pet/PET_SUM_SND_D_NUS_MBBLPD_M_CUR.htm
    'PET.M_EPC0_TVP_NUS_MBBLD.M',
    'PET.M_EPLLPA_TVP_NUS_MBBLD.M',
    'PET.M_EPL2_TVP_NUS_MBBLD.M',
    'PET.M_EPLLNG_TVP_NUS_MBBLD.M',

]

# def read_canada_imports():
#     df = excel_scraper.read_table(
#         canada_importa_file_loc, sheet_name="Data 1", skiprows=(0, 2), index_col=0
#     )
#     return df


def modify_level(level0, level1):
    return [
        item + "_4wa" if i < len(level1) and "4-Week Avg" in level1[i] else item
        for i, item in enumerate(level0)
    ]


def read_monthly_data():
    eia = API()
    dfs = []
    codemap = {}
    for code in monthly_report_codes:
        dfx = eia.get_series(series_id=code)
        codemap[code] = dfx.columns[0]
        dfs.append(dfx)
    df = pd.concat(dfs, axis=1)
    df.attrs['codemap'] = codemap
    return df


def read_release_date(fileloc):
    ex = excel_scraper.read_excel_file(fileloc)
    d = ex.parse("Contents")
    ind_row = 27
    ind_col = 2
    # Check that the values we have match the location of 'Release Date:' in the file
    rl_date_ind = int(d[d.eq("Release Date:").any(1)].index.values)
    if rl_date_ind == ind_row:
        release_date = pd.to_datetime(d.iloc[ind_row][ind_col], dayfirst=False)
        return release_date
    else:
        raise ValueError("Row indexes do not match")


def read_tab(d):
    d = d["2000":]
    d = d / 1000
    # rename and columns with 4wa
    levels = list(d.columns.levels)
    levels[0] = modify_level(levels[0], levels[1])
    d.columns = d.columns.set_levels(levels)
    d.columns = d.columns.droplevel(1)
    return d


def read_report_09() -> pd.DataFrame:
    """
    Read all the timeseries in the report
    :return:
    """
    ex = excel_scraper.read_excel_file(fileloc_09)
    dfs = []
    for tab in file_09_sheets_to_parse:
        if "Data" in tab:
            d = ex.parse(tab, skiprows=[0], header=[0, 1], index_col=0)
            dx = read_tab(d)
            dfs.append(dx)

    res = pd.concat(dfs, axis=1)

    res["Gas Yield"] = (res["W_EPM0F_YPR_NUS_MBBLD"] / res["WCRRIUS2"]) * 100
    res["Non Oxy Yield"] = (
        (res["W_EPM0F_YPR_NUS_MBBLD"] - res["W_EPOOXE_YOP_NUS_MBBLD"]) / res["WCRRIUS2"]
    ) * 100
    res["Dist Yield"] = (res["WDIRPUS2"] / res["WCRRIUS2"]) * 100

    res["mogas_dc"] = (res["WGTSTUS1"] / res["WGFUPUS2"]).rolling(window=4).mean()
    res["distillate_dc"] = (res["WDISTUS1"] / res["WDIRPUS2"]).rolling(window=4).mean()
    res["jet_dc"] = (res["WKJSTUS1"] / res["WKJUPUS2"]).rolling(window=4).mean()

    # res = pdu.mergets(res, read_canada_imports())

    return res


def read_report_01() -> pd.DataFrame:
    ex = excel_scraper.read_excel_file(fileloc_01)
    dfs = []
    for tab in ["Data 2"]:
        if "Data" in tab:
            d = ex.parse(tab, skiprows=[0], header=[0, 1], index_col=0)
            dx = read_tab(d)
            dfs.append(dx)
    res = pd.concat(dfs, axis=1)
    return res


def read_report_08() -> pd.DataFrame:
    ex = excel_scraper.read_excel_file(fileloc_08)
    dfs = []
    for tab in ["Data 1"]:
        if "Data" in tab:
            d = ex.parse(tab, skiprows=[0], header=[0, 1], index_col=0)
            dx = read_tab(d)
            dfs.append(dx)
    res = pd.concat(dfs, axis=1)
    return res


def read_report_05a() -> pd.DataFrame:
    ex = excel_scraper.read_excel_file(fileloc_05a)
    dfs = []
    for tab in ["Data 1"]:
        if "Data" in tab:
            d = ex.parse(tab, skiprows=[0], header=[0, 1], index_col=0)
            dx = read_tab(d)
            dfs.append(dx)
    res = pd.concat(dfs, axis=1)
    return res


def read_report():
    r09 = read_report_09()
    r01 = read_report_01()
    r05a = read_report_05a()
    r08 = read_report_08()
    report = pd.concat([r09, r01, r05a, r08], axis=1)
    return report


def gen_page(
    title: str, template: str, filename: str = None, report_data: pd.DataFrame = None
):
    data = {"name": title, "title": title, "eia_url": eia_url}

    if report_data is None:
        report = read_report()
        report = report.loc[:, ~report.columns.duplicated()]
        data["report"] = report
    data["release_date"] = read_release_date(fileloc_09)

    return ju.render_html(
        data,
        template=template,
        filename=filename,
        package_loader_name="oilanalytics.eia",
        template_globals={"cu": cu},
    )


def gen_crude_transfer_page(filename: str = None, report_data: pd.DataFrame = None):
    t = "DOE Weekly Report - Crude Transfers"
    data = {"name": t, "title": t, "eia_url": eia_url}

    if report_data is None:
        report = read_report()
        report = report.loc[:, ~report.columns.duplicated()]
        data["report"] = report

    data["report_monthly"] = read_monthly_data()
    data["release_date"] = read_release_date(fileloc_09)
    return ju.render_html(
        data,
        template="doe_weekly_crude_transfers.html",
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
        report_data = read_report_09()
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
        report_data = read_report_09()

    summary_table_items = {
        "WCESTUS1": "Crude Stocks",
        "W_EPC0_SAX_YCUOK_MBBL": "Cushing Stocks",
        "WGTSTUS1": "Mogas Stocks",
        "WDISTUS1": "Distillate Stocks",
        "WPRSTUS1": "Propane and Propylene Stocks",
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
    # gen_page(
    #     title="DOE Weekly Report",
    #     template="templates/doe_weekly_summary.html",
    #     filename=r"summary.html",
    # )
    # gen_page(
    #     title="DOE Weekly Report - Refineries",
    #     template="doe_weekly_refineries.html",
    #     filename=r"refineries.html",
    # )
    # gen_page(
    #     title="DOE Weekly Report - Distillates",
    #     template="doe_weekly_distillates.html",
    #     filename=r"distillates.html",
    # )
    # gen_page(
    #     title="DOE Weekly Report - Jet",
    #     template="doe_weekly_jet.html",
    #     filename=r"jet.html",
    # )
    # gen_page(
    #     title="DOE Weekly Report - Fuel",
    #     template="doe_weekly_fuel.html",
    #     filename=r"fuel.html",
    # )
    # gen_page(
    #     title="DOE Weekly Report - LPG",
    #     template="doe_weekly_lpg.html",
    #     filename=r"lpg.html",
    # )
    # gen_page(
    #     title="DOE Weekly Report - Ethanol",
    #     template="doe_weekly_ethanol.html",
    #     filename=r"ethanol.html",
    # )
    gen_page(
        title="DOE Weekly Report - Crude",
        template="doe_weekly_crude.html",
        filename=r"crude.html",
    )
    # gen_page(
    #     title="DOE Weekly Report - Gasoline",
    #     template="doe_weekly_gasoline.html",
    #     filename=r"gasoline.html",
    # )
    gen_crude_transfer_page(
        filename=r"doe_weekly_crude_transfers.html",
    )
    # gen_and_send_email()
