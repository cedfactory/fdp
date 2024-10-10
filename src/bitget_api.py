import requests
import json
import utils
import pandas as pd
from datetime import datetime
import consts

def _request_with_params(url):

    response = requests.get(url)

    return response.content.decode("utf-8")

def format_symbol(symbol):
    # Remove the slash and append '_UMCBL'
    return symbol.replace('/', '') + '_UMCBL'

def convert_to_timestamp(obj):
    if isinstance(obj, datetime):
        # Convert datetime to timestamp and format as string without .0
        return str(int(obj.timestamp()) * 1000)
    else:
        # Assume it's a timestamp and convert it to datetime
        return datetime.fromtimestamp(int(obj) * 1000)

def history_mark_candles(symbol, granularity, startTime='', endTime=''):
    params = {}
    if symbol and granularity:
        params["symbol"] = symbol
        params["granularity"] = granularity
        params["startTime"] = startTime
        params["endTime"] = endTime

        url = consts.API_URL \
              + consts.MIX_MARKET_V1_URL + "/history-index-candles" + "?symbol=" + format_symbol(symbol) \
              + "&granularity=" + granularity \
              + "&startTime=" + convert_to_timestamp(startTime)  \
              + "&endTime=" + convert_to_timestamp(endTime)

        return _request_with_params(url)
    else:
        return "pls check args"


def convert_timestamp(ts):
    return datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')


def process_data(result):
    data = json.loads(result)

    # Step 3: Process the data (convert timestamp, format numbers, etc.)
    processed_data = []
    for entry in data:
        timestamp = int(entry[0])  # Convert the timestamp from string to integer
        open_price = float(entry[1])
        high_price = float(entry[2])
        low_price = float(entry[3])
        close_price = float(entry[4])

        # Create a dictionary or any structure you need
        processed_entry = {
            "timestamp": timestamp,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price
        }

        # Append to the list of processed data
        processed_data.append(processed_entry)

    df_result = pd.DataFrame(processed_data)
    return df_result

