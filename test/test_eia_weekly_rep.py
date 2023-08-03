from datetime import date

import pandas as pd

from oilanalytics.eia import weeklypetreport


def test_read_report():
    df = weeklypetreport.read_report_09()
    assert isinstance(df, pd.DataFrame)


def test_relesae_date():
    d = weeklypetreport.read_release_date(weeklypetreport.fileloc_09)
    assert isinstance(d, date)


def test_gen_page():
    res = weeklypetreport.gen_page("Test", template="templates/doe_weekly_summary.html")
    assert res is not None
