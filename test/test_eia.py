import pandas as pd

from oilanalytics.eia import eia, steo


def test_get_data_1():
    res = eia.get_data(["STEO.PATC_NON_OECD.M", "STEO.PATC_OECD.M"])
    assert "STEO.PATC_OECD.M" in res.columns
    assert "STEO.PATC_NON_OECD.M" in res.columns
    assert isinstance(res.index, pd.DatetimeIndex)


def test_get_data_2():
    res = eia.get_data(["STEO.PATC_NON_OECD.Q", "STEO.PATC_OECD.M"])
    assert "STEO.PATC_OECD.M" in res.columns
    assert isinstance(res.index, pd.DatetimeIndex)


def test_child_series():
    categs = [
        829747,  # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Consumption
        829748,  # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Inventories
        829751,
        # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Production > Non-OPEC
        1039874,
        # EIA Data Sets > Short-Term Energy Outlook > International Petroleum and Other Liquids > Production > OPEC
    ]
    res = eia.child_series(categs, freq_filter="M")
    assert "STEO.PATC_NON_OECD.M" in [x["series_id"] for x in res]


def test_steo_get_data():
    res = steo.get_data()
    assert "STEO.PATC_NON_OECD.M" in res.columns
