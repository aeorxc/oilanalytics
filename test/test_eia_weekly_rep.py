from datetime import date

import pandas as pd

from oilanalytics.eia import weeklypetreport


def test_read_report():
    df, rd = weeklypetreport.read_report()
    assert isinstance(df, pd.DataFrame)
    assert isinstance(rd, date)


def test_gen_page():
    res = weeklypetreport.gen_page("Test", template="templates/doe_weekly_summary.html")
    assert res is not None
