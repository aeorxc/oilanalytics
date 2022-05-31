import logging as logger
import typing as t
from datetime import date

import cachetools.func
import pandas as pd
import plotly.graph_objects as go
from commodplot import commodplot as cpl
from commodplot import jinjautils as ju
from commodutil import forwards
from plotly.subplots import make_subplots
from pylim import lim

futures_dict = {
    "FB": "Brent",
    "CL": "WTI",
    "DME.OQ": "Dubai",
    "RB.UNL": "RBOB",
    "HO": "HO",
    "FP": "ULSD",
}

crude_futures = {"FB": "Brent", "CL": "WTI", "DME.OQ": "Dubai"}

default_cust_charts = {"JunJun": "JunJun", "DecDec": "DecDec"}


@cachetools.func.ttl_cache(ttl=100 * 60)
def get_contracts(
    limsymbol: str, start_year: int = 2019, end_year: int = 2023
) -> pd.DataFrame:
    contracts = lim.contracts(
        limsymbol,
        start_year=2019,
        end_year=end_year,
        start_date=pd.to_datetime(str(start_year)),
    )
    contracts = lim.limutils.convert_lim_contracts_to_datetime(contracts)

    return contracts


def generate_oi_vol_plot(df: pd.DataFrame):
    # Create subplots and mention plot grid size
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=("Price", "Volume", "OpenInterest"),
        row_width=[0.33, 0.33, 0.33],
    )

    # Plot OHLC on 1st row
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Bar trace for volumes on 2nd row without legend
    fig.add_trace(go.Bar(x=df.index, y=df["TotalVol"], showlegend=False), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["TotalOI"], showlegend=False), row=3, col=1)

    # Do not show OHLC's rangeslider plot
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(height=1000)
    for subx in range(0, 3):
        fig.layout.annotations[subx].update(x=0.025)
    return fig


def generate_symbol_page(
    limsymbol: str, symbolname: str, cust_charts: dict = None, file_path: str = None
):
    df = lim.series(limsymbol, start_date=pd.to_datetime("2015"))
    candle = lim.candlestick_data(
        limsymbol, additional_columns=("TotalOI", "TotalVol"), days=440
    )

    data = {
        "name": symbolname,
        "title": symbolname,
        "candle_chart": cpl.candle_chart(candle.tail(90), title=symbolname),
        "seas_chart": cpl.seas_line_plot(df, inc_change_sum=False, title="Seasonal"),
    }

    all_curve_dates = df.dropna()
    asked_indexes = [-i for i in (1, 2, 5, 10, 20, 30) if i <= len(all_curve_dates)]
    curve_dates = list(all_curve_dates.iloc[asked_indexes].index)
    data["curve_hist"] = cpl.forward_history_plot(
        lim.curve(limsymbol, curve_dates=curve_dates), title="Curve History"
    )

    structure = futures_structure(
        start_date="date is within 3650 days", symbol=limsymbol, convert_to_bbls=False
    )
    structure = structure[
        [x for x in structure if "M1M2" in x or "M1M6" in x or "M1M12" in x]
    ]

    data["structure"] = cpl.line_plot(structure.tail(60), title="Structure")
    data["m1m2"] = cpl.seas_line_plot(
        structure[[x for x in structure if "M1M2" in x]], title="M1-M2"
    )
    data["m1m6"] = cpl.seas_line_plot(
        structure[[x for x in structure if "M1M6" in x]], title="M1-M6"
    )
    data["m1m12"] = cpl.seas_line_plot(
        structure[[x for x in structure if "M1M12" in x]], title="M1-M12"
    )

    contracts = get_contracts(limsymbol=limsymbol)
    for spread in [
        "janfeb",
        "febmar",
        "marapr",
        "aprmay",
        "mayjun",
        "junjul",
        "julaug",
        "augsep",
        "sepoct",
        "octnov",
        "novdec",
        "decjan",
    ]:
        d = forwards.spread_combination(contracts=contracts, combination_type=spread)
        data[spread] = cpl.reindex_year_line_plot(d, title=spread)

    if cust_charts:

        index = 1
        for cust_chart in cust_charts:
            d = forwards.spread_combination(contracts, cust_chart)
            f = cpl.reindex_year_line_plot(d, title=cust_charts[cust_chart])
            data["cust_ch%s" % index] = f
            index += 1

    data["oi_vol"] = generate_oi_vol_plot(candle)

    if file_path:
        logger.info(f"generated {symbolname} page to {file_path}")
    return ju.render_html(
        data,
        "symbol.html",
        filename=file_path,
        package_loader_name="oilanalytics.prices",
    )


def futures_structure(
    start_date: t.Optional[t.Union[str, date]] = "date is within 5 days",
    convert_to_bbls: bool = True,
    symbol: str = None,
) -> pd.DataFrame:
    dfs = {}
    loop = futures_dict
    if symbol:
        loop = {symbol: symbol}

    for symbol in loop.keys():
        df = lim.continuous_futures_rollover(
            symbol, months=["M1", "M2", "M6", "M12"], start_date=start_date
        )
        if convert_to_bbls:
            if symbol == "FP":
                df = df / 7.45
            if symbol in ("RB.UNL", "HO"):
                df = df * 0.42

        df[f"{symbol}_M1M2"] = df[f"{symbol}_M1"] - df[f"{symbol}_M2"]
        df[f"{symbol}_M1M6"] = df[f"{symbol}_M1"] - df[f"{symbol}_M6"]
        df[f"{symbol}_M1M12"] = df[f"{symbol}_M1"] - df[f"{symbol}_M12"]
        dfs[symbol] = df

    res = pd.concat(list(dfs.values()), axis=1)
    return res


def generate_structure_page(
    start_date: t.Optional[t.Union[str, date]] = date(2018, 1, 1), file_path: str = None
):
    df = futures_structure(start_date=start_date)

    data = {
        "name": "Structure",
        "title": "Structure",
    }

    data["m1m2"] = cpl.line_plot(df[[x for x in df.columns if "M1M2" in x]])
    data["m1m6"] = cpl.line_plot(df[[x for x in df.columns if "M1M6" in x]])
    data["m1m12"] = cpl.line_plot(df[[x for x in df.columns if "M1M12" in x]])
    if file_path:
        logger.info(f"generated structure page to {file_path}")
    return ju.render_html(
        data=data,
        template="structure.html",
        filename=file_path,
        package_loader_name="oilanalytics.prices",
    )


if __name__ == "__main__":
    # print(get_prices(crude_futures))
    # generate_symbol_page('FB', 'Brent', cust_charts={'JunJun': 'JunJun', 'DecDec': 'DecDec'}, file_path='Brent.html')
    # df = futures_structure()
    generate_structure_page(file_path="Structure.html")
