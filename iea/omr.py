import zipfilefrom excel_scraper import excel_scraperfrom os import getenvfrom dotenv import load_dotenv# Load environmental variables from '.env' file.load_dotenv()table1_section = [    'OECD DEMAND',    'NON-OECD DEMAND',    'OECD SUPPLY',    'NON-OECD SUPPLY',    'OPEC',    'STOCK CHANGES AND MISCELLANEOUS',    'Memo items:']def read_world_snd_table1(omr_zip_loc=None):    if not omr_zip_loc:        omr_zip_loc = getenv("IEA_OMR_LOC")    z = zipfile.ZipFile(omr_zip_loc)    df = excel_scraper.read_table(z.open('August_2021_Table1.xls'), skiprows=[0, 1, 2, 3, 4, 5, 6])    df['Prefix'] = df['Unnamed: 0']    df.loc[~df['Prefix'].isin(table1_section), 'Prefix'] = None    df['Prefix'] = df['Prefix'].fillna(method='ffill')    df['Concat'] = df.apply(lambda x: '%s-%s' % (x['Prefix'], x['Unnamed: 0']), 1)    df = df.set_index('Concat')    df = df.filter(regex='\d\d\d\d|\d[Q]\d\d', axis=1)  # filter only on valid dates    df = df.T    df = df.dropna(how='all', axis=1)    df = df.rename(columns={x: x.strip() for x in df.columns})    return dfcols = {    'OECD DEMAND-Total OECD': 'OECD',    'NON-OECD DEMAND-Total Non-OECD': 'Non-OECD',    'NON-OECD DEMAND-Total Demand1': 'Demand',    'NON-OECD SUPPLY-Total Non-OPEC Supply2': 'Non-OPEC supply',    'OECD SUPPLY-Americas4' : 'North America',    'NON-OECD SUPPLY-FSU' : 'FSU',    'OPEC-NGLs' : 'OPEC NGLs/Condensates',    'OPEC-Crude' : 'OPEC crude',    'STOCK CHANGES AND MISCELLANEOUS-Total Stock Ch. & Misc' : 'Stock change',}def comparable_snd_table():    df = read_world_snd_table1()    df = df.rename(columns=cols)    return df