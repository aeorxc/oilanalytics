from oilanalytics.energyaspects import china_stats, fsu_stats


def test_china_stats():
    res = china_stats.generate_page()
    assert res is not None


def test_fsu_stats():
    res = fsu_stats.generate_page()
    assert res is not None
