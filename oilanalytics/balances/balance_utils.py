import pandas as pd
from commodutil import dates


def color_negative_red(value):
    """
    Colors elements in a dateframe
    green if positive and red if
    negative. Does not color NaN
    values.
    """

    if value < 0:
        color = "red"
    elif value > 0:
        color = "green"
    else:
        color = "black"

    return "color: %s" % color


def color_negative_red_series(series):
    return series.apply(lambda x: color_negative_red(x), 1)


def color_negative_red_row(series):
    return series.apply(lambda x: color_negative_red(x), 0)


def style_quarter_summary_table(df, accounting_col=None):
    style_td = dict(
        selector="td", props=[("border-style", "solid"), ("border-width", "1px")]
    )
    style_th = dict(
        selector="th", props=[("border-style", "solid"), ("border-width", "1px")]
    )

    year_subset = [str(x) for x in list(set(dates.find_year(df).values()))]
    dfs = (
        df.style.format("{:.2f}")
        .apply(color_negative_red_row)  # Todo apply to certain rows only
        .set_properties(**{"background-color": "lightblue"}, axis=1, subset=year_subset)
        .set_table_styles([style_th, style_td])
    )
    return dfs.render()


def quarter_summary_format(df, accounting_col=None):
    """
    Given a dataframe where the index is PeriodIndex(period[Q-DEC]),
    format dataframe using pandas styler to:
    - have yearly mean inserted between quarters
    - format to 2dp
    - highlight +/- using red/green colours for selected rows
    - transpose table horizontally

    :param df:
    :param accounting_col:
    :return:
    """
    df = add_year_agg_to_qtr_index(df)
    df.index = df.index.astype(
        str, copy=False
    )  # requires string for style to apply slicers
    df.columns.name = None
    df = df.T  # make it horizontal table
    # df = df.replace(np.nan, None)

    dfs = style_quarter_summary_table(df, accounting_col)
    return dfs


def add_year_agg_to_qtr_index(df):
    """
    Given a dataframe of PeriodIndex('Q') add Yearly averages and return
    with yearly avg inserted into the appropriate rows
    :param df:
    :return:
    """

    y = df.groupby(pd.Grouper(freq="Y")).mean()  # average the qtrs
    dfs = []
    for x, year in y.iterrows():
        year_name = year.name
        if isinstance(year_name, pd.Timestamp):
            year_name = year_name.year
        d = df.loc[str(year_name)]
        d = pd.concat([d, pd.DataFrame(year).T])
        dfs.append(d)

    res = pd.concat(dfs)
    return res


def calculate_change_from_prev_week(df_input):
    """
    calculates absolute and % change from previous week for a given DataFrame
    """
    df_change = df_input.sort_index().tail(2)
    if isinstance(df_change.index, pd.DatetimeIndex):
        df_change.index = df_change.index.strftime("%d-%b")
    df_change = df_change.T
    df_change["Change"] = (
        df_change[df_change.columns[1]] - df_change[df_change.columns[0]]
    )
    df_change["%"] = 100 * df_change["Change"] / df_change[df_change.columns[0]]
    return df_change
