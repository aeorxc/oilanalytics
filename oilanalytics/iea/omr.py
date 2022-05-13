import zipfile
from functools import lru_cache
from os import getenv

import pandas as pd
from dotenv import load_dotenv
from excel_scraper import excel_scraper

from oilanalytics.balances import balance_config

# Load environmental variables from '.env' file.
load_dotenv()

table1_section = [
    "OECD DEMAND",
    "NON-OECD DEMAND",
    "OECD SUPPLY",
    "NON-OECD SUPPLY",
    "OPEC",
    "STOCK CHANGES AND MISCELLANEOUS",
    "Memo items:",
]


@lru_cache(maxsize=10)
def read_zip(omr_zip_loc):
    return zipfile.ZipFile(omr_zip_loc)


def read_world_snd_table1(omr_zip_loc=None):
    if not omr_zip_loc:
        omr_zip_loc = getenv("IEA_OMR_LOC")
    z = read_zip(omr_zip_loc)
    fname = [x for x in z.filelist if x.filename.endswith("Table1.xls")][0]
    df = excel_scraper.read_table(z.open(fname), skiprows=[0, 1, 2, 3, 4, 5, 6])
    df["Prefix"] = df["Unnamed: 0"]
    df.loc[~df["Prefix"].isin(table1_section), "Prefix"] = None
    df["Prefix"] = df["Prefix"].fillna(method="ffill")
    df["Concat"] = df.apply(lambda x: "%s-%s" % (x["Prefix"], x["Unnamed: 0"]), 1)
    df = df.set_index("Concat")
    df = df.filter(regex="\d\d\d\d|\d[Q]\d\d", axis=1)  # filter only on valid dates
    df = df.T
    df = df.dropna(how="all", axis=1)
    df = df.rename(columns={x: x.strip() for x in df.columns})

    return df


cols = {
    "OECD DEMAND-Total OECD": "OECD",
    "NON-OECD DEMAND-Total Non-OECD": "Non-OECD",
    "NON-OECD DEMAND-Total Demand1": "Demand",
    "NON-OECD SUPPLY-Total Non-OPEC Supply2": "Non-OPEC supply",
    "OECD SUPPLY-Americas4": "North America",
    "NON-OECD SUPPLY-FSU": "FSU",
    "OPEC-NGLs": "OPEC NGLs/Condensates",
    "OPEC-Crude": "OPEC crude",
    "STOCK CHANGES AND MISCELLANEOUS-Total Stock Ch. & Misc": "Stock change",
}


def comparable_snd_table():
    df = read_world_snd_table1()
    df = df[df.index.str.contains("Q").fillna(False)]  # keep only quarters
    df.index = pd.PeriodIndex(df.index, freq="Q")
    df = df.rename(columns=cols)
    return df


def basic_comparison_table():
    df = comparable_snd_table()[balance_config.basic_summary_cols]
    return df
