import pandas as pd
import pytest

from oilanalytics.balances import key_agency_comparisons


@pytest.mark.skip("TODO: Mock IEA ZIP file")
def test_balance_comparisons():
    res = key_agency_comparisons.balance_comparisons()
    assert isinstance(res, pd.DataFrame)
