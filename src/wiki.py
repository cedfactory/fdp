import pandas as pd

from . import utils

def get_list_cac():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/CAC_40')
    df_cac = df_html[4]
    list_cac = df_cac["Ticker"].tolist()
    list_sectors = df_cac["Sector"].tolist()
    list_industry = df_cac["GICS Sub-Industry"].tolist()
    list_company_name = df_cac["Company"].tolist()

    n = len(list_cac)
    list_isin = [''] * n
    list_country = ['France'] * n
    list_exchange = ['Euronext'] * n

    df = utils.make_df_stock_info(list_cac, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_dax():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/DAX')
    df_dax = df_html[4]
    list_dax = df_dax["Ticker"].tolist()
    list_company_name = df_dax["Company"].tolist()
    list_sectors = df_dax["Prime Standard Sector"].tolist()

    n = len(list_dax)
    list_industry = [''] * n
    list_isin = [''] * n
    list_country = ['Germany'] * n
    list_exchange = ['Euronext'] * n

    df = utils.make_df_stock_info(list_dax, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_nasdaq100():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
    df_nasdaq = df_html[4]
    list_nasdaq = df_nasdaq["Company"].tolist()
    list_sectors = df_nasdaq["GICS Sector"].tolist()
    list_industry = df_nasdaq["GICS Sub-Industry"].tolist()
    list_company_name = df_nasdaq["Company"].tolist()

    n = len(list_nasdaq)
    list_isin = [''] * n
    list_country = ['united state'] * n
    list_exchange = ['NASDAQ'] * n

    df = utils.make_df_stock_info(list_nasdaq, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_dji():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
    df_dji = df_html[1]
    list_dji = df_dji["Symbol"].tolist()
    list_industry = df_dji["Industry"].tolist()
    list_company_name = df_dji["Company"].tolist()
    list_exchange = df_dji["Exchange"].tolist()

    n = len(list_dji)
    list_sectors = [''] * n
    list_isin = [''] * n
    list_country = ['united state'] * n

    df = utils.make_df_stock_info(list_dji, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df


def get_list_sp500():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df_sp500 = df_html[0]
    list_sp500 = df_sp500["Symbol"].to_list()
    list_sectors = df_sp500["GICS Sector"].tolist()
    list_industry = df_sp500["GICS Sub-Industry"].tolist()
    list_company_name = df_sp500["Security"].tolist()

    n = len(list_sp500)
    list_isin = [''] * n
    list_country = ['united state'] * n
    list_exchange = ['SP500'] * n

    df = utils.make_df_stock_info(list_sp500, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df
