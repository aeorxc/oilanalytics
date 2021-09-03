from excel_scraper import excel_scraperimport pandas as pddef read_table1(fileloc):    t = excel_scraper.read_table(fileloc, sheet_name='Table 11 - 1', skiprows=[0, 1, 2, 3])    colhead = 'World oil demand and supply balance'    # find col after colhead to help filter for main sections    col_after = t.columns[list(t.columns.values).index(colhead) + 1]    t['Prefix'] = t.apply(lambda x: x[colhead] if pd.isnull(x[col_after]) else None, 1).ffill()    t['Concat'] = t.apply(lambda x: '%s-%s' % (x['Prefix'], x[colhead]) if pd.notnull(x[col_after]) else x[            'Prefix'], 1).ffill()    t = t.set_index('Concat')    t = t.filter(regex='\d\d\d\d|\d[Q]\d\d', axis=1) # filter only on valid dates    t = t.T    t = t.dropna(how='all', axis=1)    return t