import logging
from datetime import datetime

import pandas as pd
from pyenergyaspects import eaapi as energyaspects_api

from oilanalytics.balances import balance_utils as bu

products_region_list = [
    "WORLD",
    "NA",
    "US",
    "PADD_1",
    "PADD_3",
    "EUR",
    "ME",
    "AP",
    "CN",
    "IN",
    "",
]


def add_formats(workbook):
    # https://xlsxwriter.readthedocs.io/working_with_colors.html
    header_date_format = workbook.add_format(
        {"num_format": "mmm-yy", "bg_color": "blue", "font_color": "white"}
    )
    header_qtr_format = workbook.add_format({"bg_color": "blue", "font_color": "white"})
    mbd_format = workbook.add_format({"num_format": "##,##0.00,"})
    mbd_format_forecast = workbook.add_format(
        {"num_format": "##,##0.00,", "bg_color": "lime"}
    )
    mbd_format_accounting = workbook.add_format(
        {"num_format": "[Color10]##,##0.00,;[Red]-##,##0.00,"}
    )

    formats = {
        "header_date_format": header_date_format,
        "header_qtr_format": header_qtr_format,
        "mbd_format": mbd_format,
        "mbd_format_forecast": mbd_format_forecast,
        "mbd_format_accounting": mbd_format_accounting,
    }
    return formats


def add_header(header, worksheet, pos_params, formats):
    # monthly header
    for count, date in header.iterrows():
        worksheet.write_datetime(
            0,
            pos_params["col_mth_start"] + count,
            datetime.date(date.iloc[0]),
            cell_format=formats["header_date_format"],
        )

    # quarterly header
    col_counter = pos_params["col_qtr_start"]
    for year in range(pos_params["start_year"], pos_params["end_year"] + 1):
        for i in ["1Q", "2Q", "3Q", "4Q", "Cal"]:
            period = "%s%s" % (i, str(year)[-2:]) if i[1] == "Q" else str(year)
            worksheet.write(0, col_counter, period, formats["header_qtr_format"])
            col_counter += 1


def add_forecast_colours_row(
    worksheet,
    df_row: pd.Series,
    row_number: int,
    col_number: int,
    start_date: datetime.date,
    format,
):
    for date, val in df_row.iteritems():
        if date >= start_date:
            worksheet.write_number(
                row=row_number, col=col_number, number=val, cell_format=format
            )
        col_number += 1


def add_forecast_colours(worksheet, df: pd.DataFrame, pos_params: dict, formats: dict):
    row_counter = pos_params["last_row"]
    for col in df.columns:
        df_row = df[col]
        fcstart = energyaspects_api.filter_meta_data(
            df, column=col, value="forecast_start_date"
        )
        if fcstart:
            fcstart = pd.to_datetime(fcstart)
            if fcstart > df.index[0]:
                add_forecast_colours_row(
                    worksheet,
                    df_row=df_row,
                    row_number=row_counter,
                    col_number=pos_params["col_mth_start"],
                    start_date=fcstart,
                    format=formats["mbd_format_forecast"],
                )

        row_counter += 1


def add_row_section(df, writer, worksheet, pos_params, formats):
    """
    Given a dataframe with timeseries data, transform and place into Excel.
    Apply formatting and showing summary quarter/calendar data
    :param df:
    :param writer:
    :param worksheet:
    :param pos_params:
    :param formats:
    :return:
    """
    df.T.to_excel(
        writer,
        sheet_name=worksheet.name,
        header=False,
        index=False,
        startrow=pos_params["last_row"],
        startcol=pos_params["col_mth_start"],
    )

    df_qtr = df.resample("QS").mean()
    df_qtr = bu.add_year_agg_to_qtr_index(df_qtr)
    df_qtr.T.to_excel(
        writer,
        sheet_name=worksheet.name,
        header=False,
        index=False,
        startrow=pos_params["last_row"],
        startcol=pos_params["col_qtr_start"],
    )

    cols = df.T.index
    cols = pd.DataFrame.from_records(cols.values, columns=cols.names)
    cols.to_excel(
        writer,
        sheet_name=worksheet.name,
        header=False,
        index=False,
        startrow=pos_params["last_row"],
    )

    # add red/green accounting colours on snd rows
    snd_row = cols[cols["aspect"] == "snd"].index[0]
    worksheet.set_row(
        row=pos_params["last_row"] + snd_row,
        cell_format=formats["mbd_format_accounting"],
    )

    # add forecast start colours
    add_forecast_colours(worksheet, df, pos_params=pos_params, formats=formats)

    # keep track of which row we are on by setting last_row as this section + 1
    pos_params["last_row"] = pos_params["last_row"] + len(df.T) + 1


def get_sheet_positional_params(df):
    start_year, end_year = df.index[0].year, df.index[-1].year
    years_span = (end_year - start_year) + 1
    col_qtr_start = 3
    col_mth_start = col_qtr_start + (5 * years_span) + 1
    data_columns = "D:BZ"

    return {
        "start_year": start_year,
        "end_year": end_year,
        "years_span": years_span,
        "col_qtr_start": col_qtr_start,
        "col_mth_start": col_mth_start,
        "data_columns": data_columns,
    }


def generate_product_sheet(
    commod: str, date_from: datetime.date, writer, formats: dict
):
    # need to generate worksheet using pandas
    pd.DataFrame([commod]).to_excel(
        writer, sheet_name=commod, header=False, index=False
    )

    worksheet = writer.sheets[commod]
    # Freeze first 2 rows or columns ABC
    worksheet.freeze_panes(2, 3)

    source = "Energy Aspects"
    column_format = {
        "format": ("extract_region", "aspect", "source"),
        "multiindex": True,
    }
    # df = energyaspects_api.read_commod_balance(commod=commod, geography='US', column_format=column_format,
    #                                            date_from=date_from)

    df = energyaspects_api.read_commod_balance(
        commod=commod, column_format=column_format, date_from=date_from
    )

    # ea don't have a source filter
    df = df.loc[:, (slice(None), slice(None), "Energy Aspects")]
    pos_params = get_sheet_positional_params(df)
    worksheet.set_column(pos_params["data_columns"], cell_format=formats["mbd_format"])

    add_header(
        pd.DataFrame(df.index), worksheet, pos_params=pos_params, formats=formats
    )

    pos_params["last_row"] = 2

    for region in products_region_list:
        try:
            dfi = df.loc[:, (region, ("supply", "demand"))]
            dfi.loc[:, (region, "snd", source)] = (
                dfi[(region, "supply", source)] - dfi[(region, "demand", source)]
            )
            add_row_section(
                dfi,
                writer=writer,
                worksheet=worksheet,
                pos_params=pos_params,
                formats=formats,
            )
        except ValueError as ex:
            logging.info("Unable to add section for %s: %s" % (region, ex))
        except KeyError as ex:
            logging.info("Unable to add section for %s: %s" % (region, ex))


def generate_balance():
    ts = datetime.now().strftime("%Y%m%d_%H%Y%M")
    workbookname = f"balance_{ts}.xlsx"

    writer = pd.ExcelWriter(workbookname, engine="xlsxwriter")
    workbook = writer.book
    formats = add_formats(workbook)

    date_from = pd.to_datetime("2020-01-01")

    for commod in ["gasoline"]:
        generate_product_sheet(
            commod, writer=writer, date_from=date_from, formats=formats
        )

    writer.save()
    return workbookname


if __name__ == "__main__":
    r = generate_balance()
    import os

    os.system("start Excel " + r)
