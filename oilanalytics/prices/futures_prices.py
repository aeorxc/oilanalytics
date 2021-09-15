from pylim import limfrom commodutil import forwardsfrom commodplot import commodplotutil as cpufrom commodplot import commodplot as cplimport cachetools.funcimport pandas as pdfutures_dict = {        'FB': 'Brent',        'CL': 'WTI',        'DME.OQ': 'Dubai',        'RB.UNL': 'RBOB',        'HO': 'HO',        'FP': 'ULSD'    }crude_futures = {'FB': 'Brent', 'CL': 'WTI', 'DME.OQ': 'Dubai'}@cachetools.func.ttl_cache(ttl=100 * 60)def get_contracts(limsymbol:str, start_year:int = 2019, end_year:int = 2023) -> pd.DataFrame:    contracts = lim.contracts(limsymbol, start_year=2019, end_year=end_year, start_date=pd.to_datetime(str(start_year)))    contracts = lim.limutils.convert_lim_contracts_to_datetime(contracts)    return contractsdef generate_symbol_page(limsymbol: str, symbolname: str, cust_charts:dict = None, out_loc=None):    if not out_loc:        out_loc = '%s.html' % symbolname    df = lim.series('FB', start_date=pd.to_datetime('2015'))    data = {'name': symbolname,            'title': symbolname,            'candle_chart': cpl.candle_chart(lim.candlestick_data(limsymbol), title=symbolname),            'seas_chart': cpl.seas_line_plot(df, inc_change_sum=False, title='Seasonal')}    all_curve_dates = df.dropna()    asked_indexes = [-i for i in (1, 2, 5, 10, 20, 30) if i <= len(all_curve_dates)]    curve_dates = list(all_curve_dates.iloc[asked_indexes].index)    data['curve_hist'] = cpl.forward_history_plot(lim.curve(limsymbol, curve_dates=curve_dates) , title="Curve History")    cont = lim.continuous_futures_rollover(limsymbol, months=['M1', 'M2', 'M6', 'M12'])    cont['M1-M2'], cont['M1-M6'], cont['M1-M12'] = cont.M1 - cont.M2, cont.M1 - cont.M6, cont.M1 - cont.M12    data['structure'] = cpl.line_plot(cont[['M1-M2', 'M1-M6', 'M1-M12']], title='Structure')    if cust_charts:        contracts = get_contracts(limsymbol=limsymbol)        index = 1        for cust_chart in cust_charts:            d = forwards.spread_combination(contracts, cust_chart)            f = cpl.reindex_year_line_plot(d, title=cust_charts[cust_chart])            data['cust_ch%s' % index] = f            index += 1    cpu.render_html(data, 'symbol.html', out_loc, package_loader_name='oilanalytics.prices')if __name__ == '__main__':    # print(get_prices(crude_futures))    generate_symbol_page('FB', 'Brent', cust_charts={'JunJun' : 'JunJun', 'DecDec': 'DecDec'})