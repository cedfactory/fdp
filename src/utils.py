import pandas as pd
import numpy as np
import os, shutil
from inspect import getframeinfo, stack
from datetime import datetime

from sklearn.linear_model import LinearRegression

import datetime
import utils  # assumed from your code

def get_date_range(start, end, timeframe, length=100):
    """
    If no start/end is provided, generate them by subtracting `length` intervals from now.
    Otherwise, parse start/end from strings and expand end by `length` intervals (so it's inclusive).
    """

    # 1) If start/end is not provided, auto-generate them
    if (not start or start == 'None') and (not end or end == 'None'):
        end = datetime.datetime.now().replace(second=0, microsecond=0)

        if timeframe == "1d":
            # Round to 00:00:00
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)
            start = end + datetime.timedelta(days=-length)

        elif timeframe == "1h":
            # Round to XX:00:00
            end = end.replace(minute=0, second=0, microsecond=0)
            start = end + datetime.timedelta(hours=-length)

        elif timeframe == "1m":
            # Round to XX:XX:00
            end = end.replace(second=0, microsecond=0)
            start = end + datetime.timedelta(minutes=-length)

        elif timeframe == "5m":
            # Round to a multiple of 5 minutes (optional)
            # end = end.replace(minute=(end.minute // 5) * 5, second=0, microsecond=0)
            end = end.replace(second=0, microsecond=0)
            start = end + datetime.timedelta(minutes=-length * 5)

        elif timeframe == "15m":
            # Round to a multiple of 15 minutes (optional)
            # end = end.replace(minute=(end.minute // 15) * 15, second=0, microsecond=0)
            end = end.replace(second=0, microsecond=0)
            start = end + datetime.timedelta(minutes=-length * 15)

        elif timeframe == "30m":
            # Round to a multiple of 30 minutes (optional)
            # end = end.replace(minute=(end.minute // 30) * 30, second=0, microsecond=0)
            end = end.replace(second=0, microsecond=0)
            start = end + datetime.timedelta(minutes=-length * 30)

        elif timeframe == "2h":
            # Round to nearest multiple of 2 hours (optional)
            # end = end.replace(hour=(end.hour // 2) * 2, minute=0, second=0, microsecond=0)
            end = end.replace(minute=0, second=0, microsecond=0)
            start = end + datetime.timedelta(hours=-length * 2)

        elif timeframe == "4h":
            # Round to nearest multiple of 4 hours (optional)
            # end = end.replace(hour=(end.hour // 4) * 4, minute=0, second=0, microsecond=0)
            end = end.replace(minute=0, second=0, microsecond=0)
            start = end + datetime.timedelta(hours=-length * 4)

        else:
            # Default fallback if needed
            pass

    # 2) If start/end is provided, parse them and adjust end forward by `length` intervals
    else:
        start = utils.convert_string_to_datetime(start)
        end = utils.convert_string_to_datetime(end)

        # As we want the end date included, we add the delta
        if timeframe == "1d":
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)
            end += datetime.timedelta(days=length)

        elif timeframe == "1h":
            end = end.replace(minute=0, second=0, microsecond=0)
            end += datetime.timedelta(hours=length)

        elif timeframe == "1m":
            end = end.replace(second=0, microsecond=0)
            end += datetime.timedelta(minutes=length)

        elif timeframe == "5m":
            # Round down or simply remove seconds
            end = end.replace(second=0, microsecond=0)
            end += datetime.timedelta(minutes=length * 5)

        elif timeframe == "15m":
            end = end.replace(second=0, microsecond=0)
            end += datetime.timedelta(minutes=length * 15)

        elif timeframe == "30m":
            end = end.replace(second=0, microsecond=0)
            end += datetime.timedelta(minutes=length * 30)

        elif timeframe == "2h":
            end = end.replace(minute=0, second=0, microsecond=0)
            end += datetime.timedelta(hours=length * 2)

        elif timeframe == "4h":
            end = end.replace(minute=0, second=0, microsecond=0)
            end += datetime.timedelta(hours=length * 4)

        else:
            # Default fallback if needed
            pass

    return start, end

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
