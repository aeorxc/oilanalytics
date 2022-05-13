import pandas as pd
import pytest

from oilanalytics.iea import omr


@pytest.mark.skip("TODO: Mock IEA ZIP file")
def test_read_world_snd_table1():
    res = omr.read_world_snd_table1()
    assert isinstance(res, pd.DataFrame)


@pytest.mark.skip("TODO: Mock IEA ZIP file")
def test_comparable_snd_table():
    res = omr.comparable_snd_table()
    assert isinstance(res, pd.DataFrame)
    assert isinstance(res.index, pd.PeriodIndex)
