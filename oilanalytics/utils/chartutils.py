import pandas as pd
from commodplot import commodplot as cpl
from commodplot import commodplottable as cplt

from oilanalytics.balances import balance_utils as bu


def format_chart(plotly_plot, chart_type=None, title=None):
    """apply standard formatting to a plotly plot"""

    plotly_plot.update_layout(
        {
            # shrink margins to maximise plot size
            "margin": {"l": 0, "r": 0, "t": 40, "b": 0}
        }
    )

    if chart_type == "seasonal":
        plotly_plot.update_layout(
            {
                # reverse traces to get latest dates at the top
                "legend": {"traceorder": "reversed", "font": {"size": 12}},
            }
        )
    elif chart_type == "table":
        format_dict = {"height": 30, "font": {"size": 20}}
        plotly_plot.update_traces({"cells": format_dict, "header": format_dict})
        plotly_plot.update_layout({"title": {"text": title, "font": {"size": 20}}})

    return plotly_plot


def seas_chart(
    df: pd.DataFrame,
    series: str,
    title: str,
    title_url: str = None,
    histfreq: str = None,
):
    if title_url:
        title_url_f = title_url % series
        title = f'<a href="{title_url_f}">{title}</a>'

    fig = cpl.seas_line_plot(
        df[series],
        title=title,
        shaded_range=5,
        average_line=5,
        histfreq=histfreq,
        visible_line_years=3,
    )

    return fig


def seas_chart_weekly(df: pd.DataFrame, series: str, title: str, title_url: str = None):
    return seas_chart(
        df=df, series=series, title=title, title_url=title_url, histfreq="W"
    )


def gen_wow_summary_table(df_input, precision=2, single_date=False):
    """
    generic method to create a summary table for individual location page
    :param df_input: DataFrame to summarise. Must have datetime index
    :return: html table containing summary data
    """
    df_sum = bu.calculate_change_from_prev_week(df_input)
    # format the DataFrame
    df_sum = df_sum.round(2)
    df_sum.index.rename("Product", inplace=True)
    df_sum = df_sum[
        [df_sum.columns[1], df_sum.columns[0]] + df_sum.columns[2:].tolist()
        ]  # swap first 2 columns
    df_sum.columns.name = None
    df_sum.index.name = None
    if single_date:
        df_sum.rename(columns={df_sum.columns[1]: "Last Week"}, inplace=True)
    get_summary_table = cplt.generate_table(
        df_sum, precision=precision, accounting_col_columns=["Change", "%"]
    )

    return get_summary_table
