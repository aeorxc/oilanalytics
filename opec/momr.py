from excel_scraper import excel_scraperimport pandas as pdfrom os import getenvfrom dotenv import load_dotenv# Load environmental variables from '.env' file.load_dotenv()def read_table1(fileloc=None):    # todo grab file directly from website    if not fileloc:        fileloc = getenv("OPEC_MOMR_LOC")    df = excel_scraper.read_table(fileloc, sheet_name='Table 11 - 1', skiprows=[0, 1, 2, 3])    colhead = 'World oil demand and supply balance'    # find col after colhead to help filter for main sections    col_after = df.columns[list(df.columns.values).index(colhead) + 1]    df['Prefix'] = df.apply(lambda x: x[colhead] if pd.isnull(x[col_after]) else None, 1).ffill()    df['Concat'] = df.apply(lambda x: '%s-%s' % (x['Prefix'], x[colhead]) if pd.notnull(x[col_after]) else x[            'Prefix'], 1).ffill()    df = df.set_index('Concat')    df = df.filter(regex='\d\d\d\d|\d[Q]\d\d', axis=1) # filter only on valid dates    df = df.T    df = df.dropna(how='all', axis=1)    return dfcols = {    'World demand-Total OECD': 'OECD',    'World demand-Total Non-OECD': 'Non-OECD',    'World demand-(a) Total world demand': 'Demand',    'Non-OPEC liquids production-Total Non-OPEC production': 'Non-OPEC supply',    'Non-OPEC liquids production-Americas' : 'North America',    'Non-OPEC liquids production-  of which US': 'USA',    'NON-OECD SUPPLY-FSU' : 'FSU',    'OPEC-NGLs' : 'OPEC NGLs/Condensates',    'Non-OPEC liquids production-OPEC crude oil production (secondary sources)': 'OPEC crude',    'Non-OPEC liquids production-Balance (stock change and miscellaneous)' : 'Stock change',}def comparable_snd_table():    df = read_table1()    df = df.rename(columns=cols)    return df