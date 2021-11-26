import typing as tfrom datetime import dateimport cachetools.funcimport pandas as pdfrom commodplot import commodplot as cplfrom commodplot import jinjautils as jufrom commodutil import forwardsfrom pylim import limfutures_dict = {    'FB': 'Brent',    'CL': 'WTI',    'DME.OQ': 'Dubai',    'RB.UNL': 'RBOB',    'HO': 'HO',    'FP': 'ULSD'}crude_futures = {'FB': 'Brent', 'CL': 'WTI', 'DME.OQ': 'Dubai'}@cachetools.func.ttl_cache(ttl=100 * 60)def get_contracts(limsymbol: str, start_year: int = 2019, end_year: int = 2023) -> pd.DataFrame:    contracts = lim.contracts(limsymbol, start_year=2019, end_year=end_year, start_date=pd.to_datetime(str(start_year)))    contracts = lim.limutils.convert_lim_contracts_to_datetime(contracts)    return contractsdef generate_symbol_page(limsymbol: str, symbolname: str, cust_charts: dict = None, out_loc=None):    if not out_loc:        out_loc = '%s.html' % symbolname    df = lim.series(limsymbol, start_date=pd.to_datetime('2015'))    data = {'name': symbolname,            'title': symbolname,            'candle_chart': cpl.candle_chart(lim.candlestick_data(limsymbol), title=symbolname),            'seas_chart': cpl.seas_line_plot(df, inc_change_sum=False, title='Seasonal')}    all_curve_dates = df.dropna()    asked_indexes = [-i for i in (1, 2, 5, 10, 20, 30) if i <= len(all_curve_dates)]    curve_dates = list(all_curve_dates.iloc[asked_indexes].index)    data['curve_hist'] = cpl.forward_history_plot(lim.curve(limsymbol, curve_dates=curve_dates), title="Curve History")    cont = lim.continuous_futures_rollover(limsymbol, months=['M1', 'M2', 'M6', 'M12'])    cont['M1-M2'], cont['M1-M6'], cont['M1-M12'] = cont.M1 - cont.M2, cont.M1 - cont.M6, cont.M1 - cont.M12    data['structure'] = cpl.line_plot(cont[['M1-M2', 'M1-M6', 'M1-M12']], title='Structure')    if cust_charts:        contracts = get_contracts(limsymbol=limsymbol)        index = 1        for cust_chart in cust_charts:            d = forwards.spread_combination(contracts, cust_chart)            f = cpl.reindex_year_line_plot(d, title=cust_charts[cust_chart])            data['cust_ch%s' % index] = f            index += 1    ju.render_html(data, 'symbol.html', out_loc, package_loader_name='oilanalytics.prices')def futures_structure(start_date: t.Optional[t.Union[str, date]] = 'date is within 5 days',                      convert_to_bbls: bool = True) -> pd.DataFrame:    dfs = {}    for symbol in futures_dict.keys():        df = lim.continuous_futures_rollover(symbol, months=['M1', 'M2', 'M6', 'M12'], start_date=start_date)        if convert_to_bbls:            if symbol == 'FP':                df = df / 7.45            if symbol in ('RB.UNL', 'HO'):                df = df * 0.42        df[f'{symbol}_M1M2'] = df[f'{symbol}_M1'] - df[f'{symbol}_M2']        df[f'{symbol}_M1M6'] = df[f'{symbol}_M1'] - df[f'{symbol}_M6']        df[f'{symbol}_M1M12'] = df[f'{symbol}_M1'] - df[f'{symbol}_M12']        dfs[symbol] = df    res = pd.concat(list(dfs.values()), axis=1)    return resdef generate_structure(out_loc: str = 'structure.html'):    df = futures_structure(start_date='date is within 5 days')    # df = futures_structure(start_date='2018')    data = {'name': 'Structure', 'title': 'Structure', }    data['m1m2'] = cpl.line_plot(df[[x for x in df.columns if 'M1M2' in x]])    data['m1m6'] = cpl.line_plot(df[[x for x in df.columns if 'M1M6' in x]])    data['m1m12'] = cpl.line_plot(df[[x for x in df.columns if 'M1M12' in x]])    ju.render_html(data, 'structure.html', out_loc, package_loader_name='oilanalytics.prices')if __name__ == '__main__':    # print(get_prices(crude_futures))    # generate_symbol_page('FB', 'Brent', cust_charts={'JunJun' : 'JunJun', 'DecDec': 'DecDec'})    # df = futures_structure()    generate_structure()