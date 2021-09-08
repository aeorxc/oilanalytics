from excel_scraper import excel_scraperimport pandas as pdfrom utils import fileutilsfrom os import getenvfrom dotenv import load_dotenvfrom functools import lru_cache# Load environmental variables from '.env' file.load_dotenv()def tar_to_timeseries(taramount, startdate, enddate, tarname=None):    dr = pd.date_range('01/01/2015', '01/01/2025')    ser = pd.Series(0,  index=dr)    ser[startdate:enddate] = taramount    ser.name = tarname    return ser@lru_cache(maxsize=1)def read_tars_excel():    folder = getenv('EA_TARS_FOLDER')    fileloc = fileutils.find_latest_file(folder)    ex = excel_scraper.read_excel_file(fileloc)    df = ex.parse('Refinery outages')    df = df.rename(columns={x: x.lower() for x in df.columns}) # make col headings lower case for consistency    for col in ['region', 'country', 'planned/unplanned']: # same with the column entries        df[col] = df[col].str.lower()    return df@lru_cache()def convert_table_to_tar_series(value_col='unit capacity'):    tar_table = read_tars_excel()    tarser = tar_table.apply(lambda x: tar_to_timeseries(x['unit capacity'], x['start date'], x['end date'], x.name), 1)    return tarserdef tar_series(unittype='CDU', region=None, freq='MS', sum=True, value_col='unit capacity', planned=None):    if region == 'global':        region = None    df = read_tars_excel()    df1 = df[df['unit type'] == unittype]    if region is not None:        df1 = df1[df1['region'] == region]    if planned:        if planned == 'planned':            df1 = df1[df1['planned/unplanned'] == 'planned']            df1 = df1[df1['unplanned'] == 'unplanned']    tarser = convert_table_to_tar_series(value_col=value_col)    tarser = tarser[tarser.index.isin(df1.index)] # filter tarser to same ids as df1    if sum:        tf = tarser[tarser.index.isin(df1.index)].sum()    else:        tf = tarser[tarser.index.isin(df1.index)]    tf = tf.resample(freq).mean()[:'2023']    return tfdef generate_ea_tars_page():    d = tar_series('CDU', region='global')if __name__ == '__main__':    # balance_comparisons()    generate_ea_tars_page()