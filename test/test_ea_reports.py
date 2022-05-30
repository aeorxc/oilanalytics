import pytest
from oilanalytics.energyaspects import china_stats


def test_china_stats():
    res = china_stats.generate_page()
    assert res is not None
