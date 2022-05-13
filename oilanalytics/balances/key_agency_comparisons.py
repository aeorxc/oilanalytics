from commodplot import commodplot as cpl
from commodplot import jinjautils as ju

from oilanalytics.balances import balance_config, balance_utils
from oilanalytics.eia import steo
from oilanalytics.iea import omr
from oilanalytics.opec import momr


def balance_comparisons(additional_sources: dict = None):
    iea = omr.comparable_snd_table()
    iea = iea[iea.columns.intersection(balance_config.global_oil_cols)]
    opec = momr.comparable_snd_table()
    opec = opec[opec.columns.intersection(balance_config.global_oil_cols)]
    eia = steo.comparable_snd_table()
    eia = eia[eia.columns.intersection(balance_config.global_oil_cols)]

    res = {
        "iea": iea,
        "opec": opec,
        "eia": eia,
    }

    if additional_sources:
        for additional_source in additional_sources:
            res[additional_source] = additional_sources[additional_source]

    return res


def format_table(df):
    summary_table = cpl.table_plot(df, chtype="table", formatted_cols=["Change", "%"])
    format_dict = {"height": 30, "font": {"size": 10}}
    summary_table.update_traces({"cells": format_dict, "header": format_dict})
    return summary_table


def generate_comparisons_page(out_loc=None):
    if not out_loc:
        out_loc = "BalanceComparison.html"
    d = balance_comparisons()
    data = {"name": "Balance Comparisons", "title": "Balance Comparisons"}
    data["iea_table"] = balance_utils.quarter_summary_format(
        d["iea"][balance_config.global_oil_basic_summary_cols]
    )
    data["eia_table"] = balance_utils.quarter_summary_format(
        d["eia"]
    )  # [balance_config.global_oil_basic_summary_cols])
    data["opec_table"] = balance_utils.quarter_summary_format(
        d["opec"]
    )  # [balance_config.global_oil_basic_summary_cols])
    ju.render_html(
        data,
        "balance_comparisons.html",
        filename=out_loc,
        package_loader_name="oilanalytics.balances",
    )


if __name__ == "__main__":
    # balance_comparisons()
    generate_comparisons_page()
