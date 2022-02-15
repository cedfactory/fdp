# import re
# from selenium import webdriver
import pandas as pd
from inspect import getframeinfo, stack
from bs4 import BeautifulSoup
import requests
from yahoo_fin import stock_info as si

from . import wiki

def print_exception_info(exception):
    caller = getframeinfo(stack()[2][0])
    print("[{}:{}] - {}".format(caller.filename, caller.lineno, exception))

def get_from_si(si_call):
    df = None
    try:
        df = si_call()
    except BaseException as exception:
        print_exception_info(exception)

    return df

def get_list_NASDAQ():
    list_nasdaq = si.tickers_nasdaq()

    list_sectors = ['' for i in range(len(list_nasdaq))]
    list_industry = ['' for i in range(len(list_nasdaq))]
    list_company_name = ['' for i in range(len(list_nasdaq))]

    list_isin = ['' for i in range(len(list_nasdaq))]
    list_country = ['' for i in range(len(list_nasdaq))]
    list_exchange = ['' for i in range(len(list_nasdaq))]

    df = wiki.make_df_stock_info(list_nasdaq, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_yahoo_SP500():
    list_sp500 = si.tickers_sp500()

    list_sectors = ['' for i in range(len(list_sp500))]
    list_industry = ['' for i in range(len(list_sp500))]
    list_company_name = ['' for i in range(len(list_sp500))]

    list_isin = ['' for i in range(len(list_sp500))]
    list_country = ['' for i in range(len(list_sp500))]
    list_exchange = ['' for i in range(len(list_sp500))]

    df = wiki.make_df_stock_info(list_sp500, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_DOW():
    list_dow = si.tickers_dow()

    list_sectors = ['' for i in range(len(list_dow))]
    list_industry = ['' for i in range(len(list_dow))]
    list_company_name = ['' for i in range(len(list_dow))]

    list_isin = ['' for i in range(len(list_dow))]
    list_country = ['' for i in range(len(list_dow))]
    list_exchange = ['' for i in range(len(list_dow))]

    df = wiki.make_df_stock_info(list_dow, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_FTSE100():
    list_ftse = si.tickers_ftse100()

    list_sectors = ['' for i in range(len(list_ftse))]
    list_industry = ['' for i in range(len(list_ftse))]
    list_company_name = ['' for i in range(len(list_ftse))]

    list_isin = ['' for i in range(len(list_ftse))]
    list_country = ['' for i in range(len(list_ftse))]
    list_exchange = ['' for i in range(len(list_ftse))]

    df = wiki.make_df_stock_info(list_ftse, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_FTSE250():
    list_ftse = si.tickers_ftse250()

    list_sectors = ['' for i in range(len(list_ftse))]
    list_industry = ['' for i in range(len(list_ftse))]
    list_company_name = ['' for i in range(len(list_ftse))]

    list_isin = ['' for i in range(len(list_ftse))]
    list_country = ['' for i in range(len(list_ftse))]
    list_exchange = ['' for i in range(len(list_ftse))]

    df = wiki.make_df_stock_info(list_ftse, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_IBOVESPA():
    list_ibovespa = si.tickers_ibovespa()

    list_sectors = ['' for i in range(len(list_ibovespa))]
    list_industry = ['' for i in range(len(list_ibovespa))]
    list_company_name = ['' for i in range(len(list_ibovespa))]

    list_isin = ['' for i in range(len(list_ibovespa))]
    list_country = ['' for i in range(len(list_ibovespa))]
    list_exchange = ['' for i in range(len(list_ibovespa))]

    df = wiki.make_df_stock_info(list_ibovespa, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_NIFTY50():
    list_nifty = get_from_si(si.tickers_nifty50)
    if isinstance(list_nifty, pd.DataFrame) == False:
        return None

    list_sectors = ['' for i in range(len(list_nifty))]
    list_industry = ['' for i in range(len(list_nifty))]
    list_company_name = ['' for i in range(len(list_nifty))]

    list_isin = ['' for i in range(len(list_nifty))]
    list_country = ['' for i in range(len(list_nifty))]
    list_exchange = ['' for i in range(len(list_nifty))]

    df = wiki.make_df_stock_info(list_nifty, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_NIFTY_BANK():
    list_nifty = si.tickers_niftybank()

    list_sectors = ['' for i in range(len(list_nifty))]
    list_industry = ['' for i in range(len(list_nifty))]
    list_company_name = ['' for i in range(len(list_nifty))]

    list_isin = ['' for i in range(len(list_nifty))]
    list_country = ['' for i in range(len(list_nifty))]
    list_exchange = ['' for i in range(len(list_nifty))]

    df = wiki.make_df_stock_info(list_nifty, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_EURONEXT():
    """
    list stock EURONEXT downloaded:
        https://live.euronext.com/en/products/equities/list
    """
    df_EURONEXT = pd.read_csv("./data/Euronext_Equities.csv")

    list_euronext = df_EURONEXT["symbol"].tolist()
    list_exchange = df_EURONEXT["market"].tolist()
    list_isin = df_EURONEXT["ISIN"].tolist()
    list_company_name = df_EURONEXT["name"].tolist()

    list_country = ['' for i in range(len(list_euronext))]
    list_industry = ['' for i in range(len(list_euronext))]
    list_sectors = ['' for i in range(len(list_euronext))]

    df = wiki.make_df_stock_info(list_euronext, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_undervalued():
    df_day_undervalued = get_from_si(si.get_undervalued_large_caps)
    if isinstance(df_day_undervalued, pd.DataFrame) == False:
        return None

    list_undervalued = df_day_undervalued['Symbol'].tolist()

    list_sectors = ['' for i in range(len(list_undervalued))]
    list_industry = ['' for i in range(len(list_undervalued))]
    list_company_name = ['' for i in range(len(list_undervalued))]

    list_isin = ['' for i in range(len(list_undervalued))]
    list_country = ['' for i in range(len(list_undervalued))]
    list_exchange = ['' for i in range(len(list_undervalued))]

    df = wiki.make_df_stock_info(list_undervalued, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_losers():
    df_day_losers = get_from_si(si.get_day_losers)
    if isinstance(df_day_losers, pd.DataFrame) == False:
        return None

    list_losers = df_day_losers['Symbol'].tolist()

    list_sectors = ['' for i in range(len(list_losers))]
    list_industry = ['' for i in range(len(list_losers))]
    list_company_name = ['' for i in range(len(list_losers))]

    list_isin = ['' for i in range(len(list_losers))]
    list_country = ['' for i in range(len(list_losers))]
    list_exchange = ['' for i in range(len(list_losers))]

    df = wiki.make_df_stock_info(list_losers, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_gainers():
    df_day_gainers = get_from_si(si.get_day_gainers)
    if isinstance(df_day_gainers, pd.DataFrame) == False:
        return None

    list_gainers = df_day_gainers['Symbol'].tolist()

    list_sectors = ['' for i in range(len(list_gainers))]
    list_industry = ['' for i in range(len(list_gainers))]
    list_company_name = ['' for i in range(len(list_gainers))]

    list_isin = ['' for i in range(len(list_gainers))]
    list_country = ['' for i in range(len(list_gainers))]
    list_exchange = ['' for i in range(len(list_gainers))]

    df = wiki.make_df_stock_info(list_gainers, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_most_actives():
    df_day_most_active = get_from_si(si.get_day_most_active)
    if isinstance(df_day_most_active, pd.DataFrame) == False:
        return None

    list_actives = df_day_most_active['Symbol'].tolist()

    list_sectors = ['' for i in range(len(list_actives))]
    list_industry = ['' for i in range(len(list_actives))]
    list_company_name = ['' for i in range(len(list_actives))]

    list_isin = ['' for i in range(len(list_actives))]
    list_country = ['' for i in range(len(list_actives))]
    list_exchange = ['' for i in range(len(list_actives))]

    df = wiki.make_df_stock_info(list_actives, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_trending_tickers():
    url = 'https://finance.yahoo.com/trending-tickers'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')

    list_trending = []
    list_company_name = []
    for item in soup.select('.simpTblRow'):
        list_trending.append(item.select('[aria-label=Symbol]')[0].get_text())
        list_company_name.append(item.select('[aria-label=Name]')[0].get_text())

    list_sectors = ['' for i in range(len(list_trending))]
    list_industry = ['' for i in range(len(list_trending))]

    list_isin = ['' for i in range(len(list_trending))]
    list_country = ['' for i in range(len(list_trending))]
    list_exchange = ['' for i in range(len(list_trending))]

    df = wiki.make_df_stock_info(list_trending, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_YAHOO():
    """
    if (config.COLAB == True):
        options = webdriver.ChromeOptions()
        options.add_argument('-headless')
        options.add_argument('-no-sandbox')
        options.add_argument('-disable-dev-shm-usage')
        driver = webdriver.Chrome('chromedriver', options=options)
    else:
        #DRIVER_PATH = "C:/Users/despo/chromedriver_win32/chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.add_argument('-headless')
        options.headless = True
        options.add_argument('-no-sandbox')
        options.add_argument('-window-size=1920,1200')
        options.add_argument('-disable-gpu')
        options.add_argument('-ignore-certificate-errors')
        options.add_argument('-disable-extensions')
        options.add_argument('-disable-dev-shm-usage')
        #driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
        driver = webdriver.Chrome(executable_path=config.DRIVER_PATH, options=options)

    driver.get('https://finance.yahoo.com/gainers')

    if (config.COLAB == False):
        driver.find_element_by_name("agree").click()
    """

    df_actives = get_list_most_actives()
    df_trending = get_list_trending_tickers()
    df_gainers = get_list_gainers()
    df_loosers = get_list_losers()
    df_undervalated = get_list_undervalued()

    return df_actives, df_trending, df_gainers, df_loosers, df_undervalated
