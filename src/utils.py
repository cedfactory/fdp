import pandas as pd
import numpy as np
import os, shutil
from inspect import getframeinfo, stack
from datetime import datetime, timedelta

from sklearn.linear_model import LinearRegression

def parse_params_to_str(params):
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'

    return url[0:-1]

def get_start_datetime(end, interval, length):
    # Map the interval to a timedelta object
    if interval.endswith('m'):
        # Interval is in minutes
        minutes = int(interval[:-1])
        delta = timedelta(minutes=minutes)
    elif interval.endswith('h'):
        # Interval is in hours
        hours = int(interval[:-1])
        delta = timedelta(hours=hours)
    else:
        raise ValueError("Unsupported interval format")

    # Calculate the total duration by multiplying delta by length
    total_duration = delta * length

    # Calculate the start datetime
    start = end - total_duration

    return start

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
        if "." in str:
            str = str.split(".")[0]
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
    v = [0 if isinstance(x, str) else x for x in v]
    v = [int(x) for x in v]
    return max(v) + 1

def clear_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.makedirs(path)

def get_n_columns(df, columns, n=1):
    dt = df.copy()
    for col in columns:
        dt["n"+str(n)+"_"+col] = dt[col].shift(n)
    return dt

def predict_next_LinearRegression(df, str_col, pred_window):
    df_y = pd.DataFrame()
    df_y[str_col] = df[str_col]
    df_y.dropna(inplace=True)
    df_y = df_y.iloc[-(pred_window - 1):-1]
    df_y.reset_index(inplace=True, drop=True)
    y = df_y.to_numpy()

    df_x = df_y.copy()
    df_x.reset_index(inplace=True)
    df_x.drop(columns=[str_col], inplace=True)
    x = df_x.to_numpy()

    model = LinearRegression()
    model.fit(x, y)

    # predict y from the data
    x_new = np.linspace(0, y.shape[0], y.shape[0] + 1)
    y_new = model.predict(x_new[:, np.newaxis])

    return y_new[len(y_new) - 1][0], model.coef_[0][0]

def discret_coef(coef):
    if coef > 0:
        return "UP"
    elif coef < 0:
        return "DOWN"
    elif coef == 0:
        return "FLAT"
