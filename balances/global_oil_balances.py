from iea import omrfrom opec import momrfrom eia import steocolorder = [    'Demand',    'OECD',    'Non-OECD',    'Non-OPEC supply',    'North America',    'FSU',    'OPEC NGLs/Condensates',    'OPEC crude',    'Stock change']def balance_comparisons():    iea = omr.comparable_snd_table()    iea = iea[iea.columns.intersection(colorder)]    opec = momr.comparable_snd_table()    opec = opec[opec.columns.intersection(colorder)]    eia = steo.comparable_snd_table()    eia = eia[eia.columns.intersection(colorder)]    res = {        'iea' : iea,        'opec' : opec,        'eia' : eia,    }    return resif __name__ == '__main__':    balance_comparisons()