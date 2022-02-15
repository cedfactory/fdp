import pandas as pd

def make_df_stock_info(list_stock, list_company_name, list_isin,list_sectors, list_industry, list_country, list_exchange):
    return (pd.DataFrame({'symbol': list_stock,
                          'name': list_company_name,
                          'isin': list_isin,
                          'sector': list_sectors,
                          'industry': list_industry,
                          'country': list_country,
                          'exchange': list_exchange,
                          }))

def get_list_CAC():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/CAC_40')
    df_cac = df_html[3]
    list_cac = df_cac["Ticker"].tolist()
    list_sectors = df_cac["Sector"].tolist()
    list_industry = df_cac["GICS Sub-Industry"].tolist()
    list_company_name = df_cac["Company"].tolist()

    list_isin = ['' for i in range(len(list_cac))]
    list_country = ['France' for i in range(len(list_cac))]
    list_exchange = ['Euronext' for i in range(len(list_cac))]

    df = make_df_stock_info(list_cac, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_DAX():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/DAX')
    df_dax = df_html[3]
    list_dax = df_dax["Ticker symbol"].tolist()
    list_industry = ['' for i in range(len(list_dax))]
    list_company_name = df_dax["Company"].tolist()
    list_sectors = df_dax["Prime Standard Sector"].tolist()

    list_isin = ['' for i in range(len(list_dax))]
    list_country = ['Germany' for i in range(len(list_dax))]
    list_exchange = ['Euronext' for i in range(len(list_dax))]

    df = make_df_stock_info(list_dax, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_NASDAQ100():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
    df_NASDAQ = df_html[3]
    list_nasdaq = df_NASDAQ["Ticker"].tolist()
    list_sectors = df_NASDAQ["GICS Sector"].tolist()
    list_industry = df_NASDAQ["GICS Sub-Industry"].tolist()
    list_company_name = df_NASDAQ["Company"].tolist()

    list_isin = ['' for i in range(len(list_nasdaq))]
    list_country = ['united state' for i in range(len(list_nasdaq))]
    list_exchange = ['NASDAQ' for i in range(len(list_nasdaq))]

    df = make_df_stock_info(list_nasdaq, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_DJI():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
    df_dji = df_html[1]
    list_dji = df_dji["Symbol"].tolist()
    list_industry = df_dji["Industry"].tolist()
    list_company_name = df_dji["Company"].tolist()
    list_exchange = df_dji["Exchange"].tolist()

    list_sectors = ['' for i in range(len(list_dji))]
    list_isin = ['' for i in range(len(list_dji))]
    list_country = ['united state' for i in range(len(list_dji))]

    df = make_df_stock_info(list_dji, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df


def get_list_SP500():
    df_html = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df_sp500 = df_html[0]
    list_sp500 = df_sp500["Symbol"].to_list()
    list_sectors = df_sp500["GICS Sector"].tolist()
    list_industry = df_sp500["GICS Sub-Industry"].tolist()
    list_company_name = df_sp500["Security"].tolist()

    list_isin = ['' for i in range(len(list_sp500))]
    list_country = ['united state' for i in range(len(list_sp500))]
    list_exchange = ['SP500' for i in range(len(list_sp500))]

    df = make_df_stock_info(list_sp500, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df
