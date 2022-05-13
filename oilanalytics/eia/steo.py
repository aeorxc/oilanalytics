import pandas as pd

from oilanalytics.eia import eia as eia

# https://www.eia.gov/opendata/qb.php?category=829716

categs = [
    829747,  # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Consumption
    829748,  # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Inventories
    829751,
    # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Production > Non-OPEC
    1039874,
    # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Production > OPEC
]


def get_data(freq="M", last=10):
    series = eia.child_series(categs, freq_filter=freq)
    series_ids = [x["series_id"] for x in series]
    df = eia.get_data(series_ids, last)
    return df


cols = {
    "STEO.PATC_OECD.Q": "OECD",
    "STEO.PATC_NON_OECD.Q": "Non-OECD",
    "STEO.PATC_WORLD.Q": "Demand",
    "NON-OECD SUPPLY-Total Non-OPEC Supply2": "Non-OPEC supply",
    "OECD SUPPLY-Americas4": "North America",
    "NON-OECD SUPPLY-FSU": "FSU",
    "OPEC-NGLs": "OPEC NGLs/Condensates",
    "STEO.PAPR_OPEC.Q": "OPEC crude",
    "STOCK CHANGES AND MISCELLANEOUS-Total Stock Ch. & Misc": "Stock change",
}


def comparable_snd_table():
    df = get_data(freq="Q", last=10)
    df = df.rename(columns=cols)
    df.index = pd.PeriodIndex(df.index, freq="Q")
    return df
