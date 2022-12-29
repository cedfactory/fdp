import pandas as pd
import os, shutil
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
        return None
    if isinstance(str, datetime):
        return str

    if isinstance(str, int):
        return datetime.fromtimestamp(str/1000)

    try:
        result = datetime.strptime(str, "%Y-%m-%d")
        return result
    except ValueError:
        pass
    
    try:
        result = datetime.strptime(str, "%Y-%m-%d %H:%M:%S")
        return result
    except ValueError:
        pass

    try:
        timestamp = int(int(str)/1000)
        result = datetime.fromtimestamp(timestamp)
        return result
    except ValueError:
        pass

    return None

def max_from_dict_values(indicators):
    v = list(indicators.values())
    v = [0 if x is None else x for x in v]
    v = [int(x) for x in v]
    return max(v) + 1

def clear_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.makedirs(path)