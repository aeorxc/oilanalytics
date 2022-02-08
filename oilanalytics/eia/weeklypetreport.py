import pandas as pdfrom commodplot import jinjautils as jufrom excel_scraper import excel_scraperfrom oilanalytics.utils import chartutils as cufileloc = 'https://ir.eia.gov/wpsr/psw09.xls'sheets_to_parse = [    'Data 1', 'Data 2', 'Data 3', 'Data 4', 'Data 5', 'Data 6', 'Data 7', 'Data 8', 'Data 9', 'Data 10', 'Data 11']def report_symbols() -> dict:    """    Get a list of all the symbols in the Weekly Report    :return:    """    ex = excel_scraper.read_excel_file(fileloc)    symbols = {}    for tab in sheets_to_parse:        if 'Data' in tab:            d = ex.parse(tab, skiprows=[0]).head(1).iloc[0].to_dict()            symbols = {**symbols, **d}    return symbolsdef read_report() -> pd.DataFrame:    """    Read all the timeseries in the report    :return:    """    ex = excel_scraper.read_excel_file(fileloc)    dfs = []    for tab in sheets_to_parse:        if 'Data' in tab:            d = ex.parse(tab, skiprows=[0, 2], index_col=0)            d = d['2000':]            # if tab in ['Data 1', 'Data 2', 'Data 6']:            d = d / 1000            dfs.append(d)    res = pd.concat(dfs, axis=1)    res['Gas Yield'] = res['W_EPM0F_YPR_NUS_MBBLD'] / res['WCRRIUS2']    res['Non Oxy Yield'] = (res['W_EPM0F_YPR_NUS_MBBLD'] - res['W_EPOOXE_YOP_NUS_MBBLD']) / res['WCRRIUS2']    return resdef gen_page(title: str, template:str, out_loc:str, report_data:pd.DataFrame=None):    data = {'name': title, 'title': title }    if report_data is None:        report_data = read_report()    data['report'] = report_data    ju.render_html(data, template, out_loc, package_loader_name='oilanalytics.eia',                   template_globals={'cu': cu})def gen_summary_charts(out_loc, report_data=None):    data = {'name': 'DOE Weekly Quick Report', 'title': 'DOE Weekly Quick', }    if report_data is None:        report_data = read_report()    data['report'] = report_data    ju.render_html(data, 'doe_weekly_summary.html', out_loc, package_loader_name='oilanalytics.eia',                   template_globals={'cu': cu})if __name__ == '__main__':    gen_page(title='DOE Weekly Quick Report', template='doe_weekly_summary.html', out_loc=r'M:\SitePages\Fundamentals\DOEWeekly\summary.aspx')    # gen_page(title='DOE Weekly Quick Report - Crude', template='doe_weekly_crude.html',    #          out_loc=r'M:\SitePages\Fundamentals\DOEWeekly\crude.aspx')    # gen_page(title='DOE Weekly Quick Report - Gasoline', template='doe_weekly_gasoline.html',    #          out_loc=r'M:\SitePages\Fundamentals\DOEWeekly\gasoline.aspx')