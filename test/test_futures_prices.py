from oilanalytics.prices import futures_prices


def test_futures_structure():
    res = futures_prices.futures_structure(start_date="date is within 5 days")
    assert "FB_M1" in res.columns


def test_gen_symbol_page():
    res = futures_prices.generate_symbol_page("FB", symbolname="Brent")
    assert res is not None


def test_gen_structure_page():
    res = futures_prices.generate_structure_page()
    assert res is not None
