import pandas as pdfrom excel_scraper import excel_scraperfrom oilanalytics.eia import chartutils as cufrom commodplot import jinjautils as jufileloc = 'https://ir.eia.gov/wpsr/psw09.xls'def report_symbols() -> dict:    """    Get a list of all the symbols in the Weekly Report    :return:    """    ex = excel_scraper.read_excel_file(fileloc)    symbols = {}    for tab in ex.sheet_names:        if 'Data' in tab:            d = ex.parse(tab, skiprows=[0]).head(1).iloc[0].to_dict()            symbols = {**symbols, **d}    return symbolsdef read_report() -> pd.DataFrame:    """    Read all the timeseries in the report    :return:    """    ex = excel_scraper.read_excel_file(fileloc)    dfs = []    for tab in ex.sheet_names:        if 'Data' in tab:            d = ex.parse(tab, skiprows=[0, 2], index_col=0)            dfs.append(d)    res = pd.concat(dfs, axis=1)    return resdef gen_summary_charts(out_loc):    data = {'name': 'DOE Weekly Quick', 'title': 'DOE Weekly Quick', }    data['report'] = read_report()    ju.render_html(data, 'doe_weekly_summary.html', out_loc, package_loader_name='oilanalytics.eia', template_globals={'cu': cu})if __name__ == '__main__':    gen_summary_charts(out_loc=r'M:\SitePages\Fundamentals\DOEWeekly\summary.aspx')