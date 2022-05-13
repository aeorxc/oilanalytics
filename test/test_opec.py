import pandas as pd

from oilanalytics.opec import momr


def test_read_table1():
    res = momr.read_table1()
    assert isinstance(res, pd.DataFrame)


def test_comparable_snd_table():
    res = momr.comparable_snd_table()
    assert isinstance(res.index, pd.PeriodIndex)
