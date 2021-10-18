from datetime import datetimeimport pandas as pdfrom oilanalytics.balances import balance_utils as bufrom oilanalytics.energyaspects import energyaspects_apidef add_formats(workbook):    # https: // xlsxwriter.readthedocs.io / working_with_colors.html    header_date_format = workbook.add_format({'num_format': 'mmm-yy', 'bg_color': 'blue', 'font_color': 'white'})    header_qtr_format = workbook.add_format({'bg_color': 'blue', 'font_color': 'white'})    mbd_format = workbook.add_format({'num_format': '##,##0.00,'})    formats = {        'header_date_format': header_date_format,        'header_qtr_format': header_qtr_format,        'mbd_format': mbd_format,    }    return formatsdef add_header(header, worksheet, pos_params, formats):    # monthly header    for count, date in header.iterrows():        worksheet.write_datetime(0, pos_params['col_mth_start'] + count, datetime.date(date.iloc[0]),                                 cell_format=formats['header_date_format'])    # quarterly header    col_counter = pos_params['col_qtr_start']    for year in range(pos_params['start_year'], pos_params['end_year'] + 1):        for i in ['Q1', 'Q2', 'Q3', 'Q4', 'Cal']:            period = '%s%s' % (i, str(year)[-2:]) if i.startswith('Q') else str(year)            worksheet.write(0, col_counter, period, formats['header_qtr_format'])            col_counter += 1def add_row_section(df, writer, worksheet, pos_params, formats):    df.T.to_excel(writer, sheet_name=worksheet.name, header=False, index=False, startrow=pos_params['last_row'],                  startcol=pos_params['col_mth_start'])    df_qtr = df.resample('QS').mean()    df_qtr = bu.add_year_agg_to_qtr_index(df_qtr)    df_qtr.T.to_excel(writer, sheet_name=worksheet.name, header=False, index=False, startrow=pos_params['last_row'],                  startcol=pos_params['col_qtr_start'])    # todo bump last_rowdef get_sheet_positional_params(df):    start_year, end_year = df.index[0].year, df.index[-1].year    years_span = (end_year - start_year) + 1    col_qtr_start = 3    col_mth_start = col_qtr_start + (5 * years_span) + 1    return {        'start_year': start_year,        'end_year': end_year,        'years_span': years_span,        'col_qtr_start': col_qtr_start,        'col_mth_start': col_mth_start,    }def generate_product_page(commod: str, date_from: datetime.date, writer, formats: dict):    # need to generate worksheet using pandas    pd.DataFrame([commod]).to_excel(writer, sheet_name=commod, header=False, index=False)    worksheet = writer.sheets[commod]    worksheet.set_column('D:AZ', cell_format=formats['mbd_format'])    column_format = {'format': ('extract_region', 'aspect', 'source'), 'multiindex': True}    df = energyaspects_api.read_commod_balance(commod=commod, geography='WORLD', column_format=column_format,                                               date_from=date_from)    pos_params = get_sheet_positional_params(df)    add_header(pd.DataFrame(df.index), worksheet, pos_params=pos_params, formats=formats)    pos_params['last_row'] = 2    add_row_section(df, writer=writer, worksheet=worksheet, pos_params=pos_params, formats=formats)def generate_balance():    ts = datetime.now().strftime('%Y%m%d_%H%Y%M')    workbookname = f'balance_{ts}.xlsx'    writer = pd.ExcelWriter(workbookname, engine='xlsxwriter')    workbook = writer.book    formats = add_formats(workbook)    date_from = pd.to_datetime('2020-01-01')    for commod in ['gasoline']:        generate_product_page(commod, writer=writer, date_from=date_from, formats=formats)    # # headers    # for col_num, data in enumerate(quarters):    # 	worksheet.write(row, col_num + col, data, yearly_headers)    writer.save()    return workbooknameif __name__ == '__main__':    r = generate_balance()    import os    os.system('start Excel ' + r)