import pandas as pd
from inspect import getframeinfo, stack
from datetime import datetime

def print_exception_info(exception):
    caller = getframeinfo(stack()[2][0])
    print("[{}:{}] - {}".format(caller.filename, caller.lineno, exception))

def make_df_stock_info(list_stock, list_company_name, list_isin,list_sectors, list_industry, list_country, list_exchange):
    return (pd.DataFrame({'symbol': list_stock,
                          'name': list_company_name,
                          'isin': list_isin,
                          'sector': list_sectors,
                          'industry': list_industry,
                          'country': list_country,
                          'exchange': list_exchange,
                          }))

def convert_string_to_datetime(str):
    if str == None:
        return str
    try:
        result = datetime.strptime(str, "%Y-%m-%d")
    except ValueError:
        timestamp = int(int(str)/1000)
        result = datetime.fromtimestamp(timestamp)
    return result

