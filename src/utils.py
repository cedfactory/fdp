import pandas as pd
import numpy as np
import os, shutil
import time
from inspect import getframeinfo, stack
from datetime import datetime, timedelta
from datetime import datetime, timezone
from sklearn.linear_model import LinearRegression

from datetime import datetime, timezone, timedelta
import pytz

import xml.etree.ElementTree as ET
import logging


def xml_to_list(file_path):
    """
    Read an XML file (with <items><item> structure) and convert it into
    a list of {'symbol': ..., 'timeframe': ...} dictionaries.
    """
    try:
        tree = ET.parse(file_path)
    except FileNotFoundError as e:
        logging.error("File not found: %s", file_path)
        # Return an empty list to indicate no data could be read
        return []
    except ET.ParseError as e:
        logging.error("Failed to parse XML file '%s': %s", file_path, e)
        # Return an empty list if XML is malformed
        return []

    # If parse succeeded, get the root element
    root = tree.getroot()
    result_list = []

    # Iterate over each <item> element in the root
    for item_elem in root.findall('item'):
        # Find sub-elements and get their text (if not found, use None or skip)
        symbol_elem = item_elem.find('symbol')
        timeframe_elem = item_elem.find('timeframe')
        if symbol_elem is None or timeframe_elem is None:
            # Skip this item if required sub-elements are missing
            logging.warning("Skipping an <item> with missing <symbol> or <timeframe>")
            continue
        # Construct dictionary for the item
        entry = {
            'symbol': symbol_elem.text if symbol_elem.text is not None else "",
            'timeframe': timeframe_elem.text if timeframe_elem.text is not None else ""
        }
        result_list.append(entry)

    return result_list

def convert_symbol_to_bitget(symbol, margin="USDT"):
    """
    Convert a symbol like 'BTC/USDT' to the Bitget futures symbol format.

    margin: "USDT" or "COIN"
    """
    base, quote = symbol.split("/")

    if margin.upper() == "USDT":
        # e.g. 'BTC/USDT' -> 'BTCUSDT_UMCBL'
        return base + quote + "_UMCBL"
    else:
        # e.g. 'BTC/USD' -> 'BTCUSD_DMCBL' for coin-margined
        return base + quote + "_DMCBL"


def get_date_range(start, end, timeframe, length=100):
    """
    If no start/end is provided, generate them by subtracting `length` intervals from now.
    Otherwise, parse start/end from strings and expand end by `length` intervals (so it's inclusive).
    """

    # 1) If start/end is not provided, auto-generate them
    if (not start or start == 'None') and (not end or end == 'None'):
        end = datetime.now().replace(second=0, microsecond=0)

        if timeframe == "1d":
            # Round to 00:00:00
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)
            start = end + timedelta(days=-length)

        elif timeframe == "1h":
            # Round to XX:00:00
            end = end.replace(minute=0, second=0, microsecond=0)
            start = end + timedelta(hours=-length)

        elif timeframe == "1m":
            # Round to XX:XX:00
            end = end.replace(second=0, microsecond=0)
            start = end + timedelta(minutes=-length)

        elif timeframe == "5m":
            # Round to a multiple of 5 minutes (optional)
            # end = end.replace(minute=(end.minute // 5) * 5, second=0, microsecond=0)
            end = end.replace(second=0, microsecond=0)
            start = end + timedelta(minutes=-length * 5)

        elif timeframe == "15m":
            # Round to a multiple of 15 minutes (optional)
            # end = end.replace(minute=(end.minute // 15) * 15, second=0, microsecond=0)
            end = end.replace(second=0, microsecond=0)
            start = end + timedelta(minutes=-length * 15)

        elif timeframe == "30m":
            # Round to a multiple of 30 minutes (optional)
            # end = end.replace(minute=(end.minute // 30) * 30, second=0, microsecond=0)
            end = end.replace(second=0, microsecond=0)
            start = end + timedelta(minutes=-length * 30)

        elif timeframe == "2h":
            # Round to nearest multiple of 2 hours (optional)
            # end = end.replace(hour=(end.hour // 2) * 2, minute=0, second=0, microsecond=0)
            end = end.replace(minute=0, second=0, microsecond=0)
            start = end + timedelta(hours=-length * 2)

        elif timeframe == "4h":
            # Round to nearest multiple of 4 hours (optional)
            # end = end.replace(hour=(end.hour // 4) * 4, minute=0, second=0, microsecond=0)
            end = end.replace(minute=0, second=0, microsecond=0)
            start = end + timedelta(hours=-length * 4)

        else:
            # Default fallback if needed
            pass

    # 2) If start/end is provided, parse them and adjust end forward by `length` intervals
    else:
        start = convert_string_to_datetime(start)
        end = convert_string_to_datetime(end)

        # As we want the end date included, we add the delta
        if timeframe == "1d":
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)
            end += timedelta(days=length)

        elif timeframe == "1h":
            end = end.replace(minute=0, second=0, microsecond=0)
            end += timedelta(hours=length)

        elif timeframe == "1m":
            end = end.replace(second=0, microsecond=0)
            end += timedelta(minutes=length)

        elif timeframe == "5m":
            # Round down or simply remove seconds
            end = end.replace(second=0, microsecond=0)
            end += timedelta(minutes=length * 5)

        elif timeframe == "15m":
            end = end.replace(second=0, microsecond=0)
            end += timedelta(minutes=length * 15)

        elif timeframe == "30m":
            end = end.replace(second=0, microsecond=0)
            end += timedelta(minutes=length * 30)

        elif timeframe == "2h":
            end = end.replace(minute=0, second=0, microsecond=0)
            end += timedelta(hours=length * 2)

        elif timeframe == "4h":
            end = end.replace(minute=0, second=0, microsecond=0)
            end += timedelta(hours=length * 4)

        else:
            # Default fallback if needed
            pass

    return start, end

def print_exception_info(exception):
    caller = getframeinfo(stack()[2][0])
    print("[{}:{}] - {}".format(caller.filename, caller.lineno, exception))


def make_df_stock_info(list_stock, list_company_name, list_isin, list_sectors, list_industry, list_country,
                       list_exchange):
    return (pd.DataFrame({'symbol': list_stock,
                          'name': list_company_name,
                          'isin': list_isin,
                          'sector': list_sectors,
                          'industry': list_industry,
                          'country': list_country,
                          'exchange': list_exchange,
                          }))


def convert_string_to_datetime(string):
    if string == None:
        return None
    if isinstance(string, datetime):
        return string

    if isinstance(string, int):
        return datetime.fromtimestamp(string / 1000)

    try:
        result = datetime.strptime(string, "%Y-%m-%d")
        return result
    except ValueError:
        pass

    try:
        if "." in string:
            string = string.split(".")[0]
        result = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return result
    except ValueError:
        pass

    try:
        timestamp = int(int(string) / 1000)
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
        dt["n" + str(n) + "_" + col] = dt[col].shift(n)
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

def dict_lists_equal(lst1, lst2):
    normalized_lst1 = [normalize(d) for d in lst1]
    normalized_lst2 = [normalize(d) for d in lst2]
    return all(d in normalized_lst2 for d in normalized_lst1) and all(d in normalized_lst1 for d in normalized_lst2)

def normalize(d):
    # Create a copy so the original dict isn't modified.
    nd = d.copy()
    if nd.get("channel") == "account":
        # For account, map 'param' to 'coin' if present.
        if "param" in nd:
            nd["coin"] = nd.pop("param")
    else:
        # For non-account channels, map 'param' to 'inst_id' if present.
        if "param" in nd:
            nd["inst_id"] = nd.pop("param")
    return nd

def get_last_tick_datetime(timeframe: str, now: datetime = None) -> datetime:
    """
    Return the start of the current bar as a timezone-aware UTC datetime.
    """
    # Always work in UTC
    if now is None:
        now = datetime.now(timezone.utc)
    else:
        # If naive, assume UTC; if aware, convert to UTC
        now = now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now.astimezone(timezone.utc)

    unit = timeframe[-1]
    value = int(timeframe[:-1])

    if unit == "m":
        floored_minute = (now.minute // value) * value
        return now.replace(minute=floored_minute, second=0, microsecond=0)
    elif unit == "h":
        floored_hour = (now.hour // value) * value
        return now.replace(hour=floored_hour, minute=0, second=0, microsecond=0)
    else:
        raise ValueError(f"Unsupported timeframe unit: {unit!r}")

def get_released_tick_datetime(timeframe: str, now: datetime = None) -> datetime:
    """
    Return the start of the *previous* bar as a timezone-aware UTC datetime,
    based on the given timeframe.
    """
    last_tick = get_last_tick_datetime(timeframe, now)
    unit = timeframe[-1]
    value = int(timeframe[:-1])

    if unit == "m":
        delta = timedelta(minutes=value)
    elif unit == "h":
        delta = timedelta(hours=value)
    else:
        raise ValueError(f"Unsupported timeframe unit: {unit!r}")

    return last_tick - delta

def is_last_tick_in_df(df: pd.DataFrame, timeframe: str, now: datetime = None) -> bool:
    """
    True if the current bar’s start timestamp (UTC) is in df.index.
    """
    # Normalize index to UTC
    if df.index.tzinfo is None:
        idx = df.index.tz_localize('UTC')
    else:
        idx = df.index.tz_convert('UTC')

    last_tick = get_last_tick_datetime(timeframe, now)
    return pd.Timestamp(last_tick) in idx

def is_released_tick_in_df(df: pd.DataFrame, timeframe: str, now: datetime = None) -> bool:
    """
    True if the *previous* bar’s start timestamp (UTC) is in df.index.
    """
    # Normalize index to UTC
    if df.index.tzinfo is None:
        idx = df.index.tz_localize('UTC')
    else:
        idx = df.index.tz_convert('UTC')

    released_tick = get_released_tick_datetime(timeframe, now)
    return pd.Timestamp(released_tick) in idx

class traces_cpt:
    def __init__(self):
        self.success = 0
        self.failure = 0
        self.failure_is_not_none = 0
        self.failure_is_dataframe = 0
        self.failure_under_limit = 0
        self.failure_no_tick_in = 0
        self.percentage_of_failure = 0.0
        self.percentage_of_failure_is_not_none = 0.0
        self.percentage_of_failure_is_dataframe = 0.0
        self.percentage_of_failure_under_limit = 0.0
        self.percentage_of_failure_no_tick_in = 0.0
        self.start_time = None  # Time of the first event
        self.last_print_time = None  # Time when stats were last printed



    def _update_percentage(self):
        total = self.success + self.failure
        self.percentage_of_failure = (self.failure / total * 100) if total > 0 else 0.0
        self.percentage_of_failure_is_not_none = (self.failure_is_not_none / self.failure * 100) if self.failure > 0 else 0.0
        self.percentage_of_failure_is_dataframe = (self.failure_is_dataframe / self.failure * 100) if self.failure > 0 else 0.0
        self.percentage_of_failure_under_limit = (self.failure_under_limit / self.failure * 100) if self.failure > 0 else 0.0
        self.percentage_of_failure_no_tick_in = (self.failure_no_tick_in / self.failure * 100) if self.failure > 0 else 0.0


    def _maybe_print(self):
        current_time = time.time()
        total = self.success + self.failure

        # Initialize last_print_time if it's not set yet
        if self.last_print_time is None:
            self.last_print_time = current_time

        # Check if total is a multiple of 10000 or if an hour has passed since last print
        if total % 1000 == 0 or (current_time - self.last_print_time >= 3600):
            self.print_stat()
            self.last_print_time = current_time  # Update the last printed time

    def increment_success(self):
        if self.start_time is None:
            self.start_time = time.time()
        self.success += 1
        self._update_percentage()
        self._maybe_print()

    def increment_failure(self,
                          is_not_none=False,
                          is_dataframe=False,
                          limit=False,
                          tick_in=False):
        if self.start_time is None:
            self.start_time = time.time()
        self.failure += 1

        # define a mapping of your boolean flags to the corresponding counter names
        flag_to_counter = {
            is_not_none: "failure_is_not_none",
            is_dataframe: "failure_is_dataframe",
            limit: "failure_under_limit",
            tick_in: "failure_no_tick_in",
        }

        # iterate once, bumping only the ones whose flag is True
        for flag, counter_name in flag_to_counter.items():
            if flag:
                setattr(self, counter_name, getattr(self, counter_name) + 1)

        self._update_percentage()
        self._maybe_print()

    def _format_duration(self, seconds):
        days, rem = divmod(seconds, 86400)  # 86400 seconds in a day
        hours, rem = divmod(rem, 3600)  # 3600 seconds in an hour
        minutes, seconds = divmod(rem, 60)
        if days > 0:
            return f"{int(days)}d:{int(hours)}h:{int(minutes)}m:{seconds:.2f}s"
        elif hours > 0:
            return f"{int(hours)}h:{int(minutes)}m:{seconds:.2f}s"
        elif minutes > 0:
            return f"{int(minutes)}m:{seconds:.2f}s"
        else:
            return f"{seconds:.2f}s"

    def print_stat(self):
        elapsed = time.time() - self.start_time if self.start_time else 0.0
        formatted_elapsed = self._format_duration(elapsed)
        print(
            f"Success: {self.success}, Failure: {self.failure}, "
            f"Percentage of Failure: {self.percentage_of_failure:.2f}%, "
            f"Duration: {formatted_elapsed}"
        )

    def get_status(self):
        return {
            "percentage_of_failure": self.percentage_of_failure,
            "percentage_of_failure_is_not_none": self.percentage_of_failure_is_not_none,
            "percentage_of_failure_is_dataframe": self.percentage_of_failure_is_dataframe,
            "percentage_of_failure_under_limit": self.percentage_of_failure_under_limit,
            "percentage_of_failure_no_tick_in": self.percentage_of_failure_no_tick_in,
            "success": self.success,
            "failure": self.failure
        }