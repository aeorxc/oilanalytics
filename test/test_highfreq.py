import pytest

from oilanalytics.highfreq import ara, singapore


@pytest.mark.skip("Eikon required")
def test_ara_data():
    res = ara.ara_data(start_date="2022-01-01")
    assert "Jet" in res.columns
    assert res["Jet"].loc["2022-01-06"] == pytest.approx(7.06, 0.01)
    # Note freq might not be consistent across time, so this won't be true across history
    # self.assertEqual(pd.infer_freq(res.index), 'W-THU')


@pytest.mark.skip("Eikon required")
def test_sing_data():
    res = singapore.singapore_data(start_date="2022-01-01")
    assert "LightDistillates" in res.columns
