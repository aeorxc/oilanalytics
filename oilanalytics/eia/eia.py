import typing as t
from functools import reduce

import pandas as pd
from dotenv import load_dotenv
from eiapy import Category, MultiSeries

# Load environmental variables from '.env' file.
load_dotenv()


def extract_dataframe(data: list, series_id: str, freq: str = "M") -> pd.DataFrame:
    df = pd.DataFrame(data, columns=["date", series_id]).set_index("date")
    f = None
    if freq == "M":
        f = "%Y%m"
    df.index = pd.to_datetime(df.index, format=f)
    return df


def get_data(series_ids: t.Tuple[str], last=10) -> pd.DataFrame:
    """
    Given a list of EIA series Id, call api, get the data and return as a DataFrame
    :param series_ids:
    :param last: how many data points going back are required
    :return:
    """
    res = MultiSeries(series_ids).last(last)
    dfs = [extract_dataframe(x["data"], x["series_id"], x["f"]) for x in res["series"]]
    dfs = reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how="outer"
        ),
        dfs,
    )
    dfs.attrs["meta"] = {x["series_id"]: x for x in res["series"]}
    return dfs


def child_series(category_ids: t.Tuple[int], freq_filter: str = None) -> list:
    """
    Given a list of EIA category ids, get a list of series_ids that make up those categories
    :param category_ids:
    :param freq_filter: filter for frequency eg annual, monthly, quarterly
    :return:
    """
    a = [Category(x).get_info()["category"]["childseries"] for x in category_ids]
    a = [item for sublist in a for item in sublist]
    if freq_filter:
        a = [x for x in a if x["f"] == freq_filter]
    return a
