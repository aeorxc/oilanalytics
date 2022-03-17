import pandas as pdfrom commodplot import commodplot as cpldef format_chart(plotly_plot, chart_type=None, title=None):    """apply standard formatting to a plotly plot"""    plotly_plot.update_layout({        # shrink margins to maximise plot size        'margin': {'l': 0, 'r': 0, 't': 40, 'b': 0}    })    if chart_type == 'seasonal':        plotly_plot.update_layout({            # reverse traces to get latest dates at the top            'legend': {'traceorder': 'reversed', 'font': {'size': 12}},        })    elif chart_type == 'table':        format_dict = {'height': 30, 'font': {'size': 20}}        plotly_plot.update_traces({'cells': format_dict, 'header': format_dict})        plotly_plot.update_layout({'title': {'text': title, 'font': {'size': 20}}})    return plotly_plotdef seas_chart_weekly(df: pd.DataFrame, series: str, title: str, title_url:str = None):    if title_url:        title_url_f = title_url % series        title = f'<a href="{title_url_f}">{title}</a>'    fig = cpl.seas_line_plot(df[series], title=title, shaded_range=5, average_line=5, histfreq='W',                             visible_line_years=3)    return fig