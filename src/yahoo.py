import pandas as pd
from inspect import getframeinfo, stack
from bs4 import BeautifulSoup
import requests
from yahoo_fin import stock_info as si

from . import utils

def print_exception_info(exception):
    caller = getframeinfo(stack()[2][0])
    print("[{}:{}] - {}".format(caller.filename, caller.lineno, exception))

def get_from_si(si_call):
    df = None
    try:
        df = si_call()
    except BaseException as exception:
        print_exception_info(exception)
        raise exception

    return df

def get_list_nasdaq():
    list_nasdaq = si.tickers_nasdaq()
    n = len(list_nasdaq)
    df = utils.make_df_stock_info(list_nasdaq, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_yahoo_sp500():
    list_sp500 = si.tickers_sp500()
    n = len(list_sp500)
    df = utils.make_df_stock_info(list_sp500, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_dow():
    list_dow = si.tickers_dow()
    n = len(list_dow)
    df = utils.make_df_stock_info(list_dow, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_ftse100():
    list_ftse = si.tickers_ftse100()
    n = len(list_ftse)
    df = utils.make_df_stock_info(list_ftse, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_ftse250():
    list_ftse = si.tickers_ftse250()
    n = len(list_ftse)
    df = utils.make_df_stock_info(list_ftse, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_ibovespa():
    list_ibovespa = si.tickers_ibovespa()
    n = len(list_ibovespa)
    df = utils.make_df_stock_info(list_ibovespa, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_nifty50():
    list_nifty = get_from_si(si.tickers_nifty50)
    if isinstance(list_nifty, pd.DataFrame) == False:
        return None
    n = len(list_nifty)
    df = utils.make_df_stock_info(list_nifty, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_nifty_bank():
    list_nifty = si.tickers_niftybank()
    n = len(list_nifty)
    df = utils.make_df_stock_info(list_nifty, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_euronext():
    """
    list stock EURONEXT downloaded:
        https://live.euronext.com/en/products/equities/list
    """
    df_euronext = pd.read_csv("./data/Euronext_Equities.csv")

    list_euronext = df_euronext["symbol"].tolist()
    list_exchange = df_euronext["market"].tolist()
    list_isin = df_euronext["ISIN"].tolist()
    list_company_name = df_euronext["name"].tolist()

    n = len(list_euronext)
    list_country = [''] * n
    list_industry = [''] * n
    list_sectors = [''] * n

    df = utils.make_df_stock_info(list_euronext, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)
    return df

def get_list_undervalued():
    df_day_undervalued = get_from_si(si.get_undervalued_large_caps)
    if isinstance(df_day_undervalued, pd.DataFrame) == False:
        return None

    list_undervalued = df_day_undervalued['Symbol'].tolist()
    n = len(df_day_undervalued)
    df = utils.make_df_stock_info(list_undervalued, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_losers():
    df_day_losers = get_from_si(si.get_day_losers)
    if isinstance(df_day_losers, pd.DataFrame) == False:
        return None

    list_losers = df_day_losers['Symbol'].tolist()
    n = len(list_losers)
    df = utils.make_df_stock_info(list_losers, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_gainers():
    df_day_gainers = get_from_si(si.get_day_gainers)
    if isinstance(df_day_gainers, pd.DataFrame) == False:
        return None

    list_gainers = df_day_gainers['Symbol'].tolist()
    n = len(list_gainers)
    df = utils.make_df_stock_info(list_gainers, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
    return df

def get_list_most_actives():
    df_day_most_active = get_from_si(si.get_day_most_active)
    if isinstance(df_day_most_active, pd.DataFrame) == False:
        return None

    list_actives = df_day_most_active['Symbol'].tolist()
    n = len(list_actives)
    df = utils.make_df_stock_info(list_actives, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)
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

    n = len(list_trending)
    list_sectors = [''] * n
    list_industry = [''] * n

    list_isin = [''] * n
    list_country = [''] * n
    list_exchange = [''] * n

    df = utils.make_df_stock_info(list_trending, list_company_name, list_isin, list_sectors, list_industry, list_country, list_exchange)

    return df

def get_list_yahoo():
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
