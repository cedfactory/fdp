import pandas as pd
import numpy as np
import ccxt
import time
from datetime import datetime, timedelta
from datetime import date
import datetime
from . import utils
from . import indicators as inc_indicators
import concurrent.futures

'''
format for since : yyyy-mm-dd
'''
def _get_ohlcv(exchange, symbol, start, end=None, timeframe="1d", limit=None):
    if exchange == None or symbol == None or start == None:
        return None
    #print("start : ", start)
    #print("end : ", end)

    since = int(start.timestamp())*1000
    if end != None:
        delta = end - start
        if timeframe == "1d":
            limit = delta.days # days
        elif timeframe == "1h":
            limit = int(delta.total_seconds() / 3600)
        elif timeframe == "1m":
            limit = int(delta.total_seconds() / 60)

    #print("limit : ", limit)
    if limit == None:
        return None

    intervals = []
    if timeframe == "1d" or timeframe == "1h" or timeframe == "1m" : # split into requests with limit = 5000
        if timeframe == "1d":
            offset = 5000 * 24 * 60 * 60 * 1000
        if timeframe == "1h":
            offset = 5000 * 60 * 60 * 1000
        if timeframe == "1m":
            offset = 5000 * 60 * 1000
        while limit > 5000:
            since_next = since + offset
            intervals.append({'since': since, 'limit': 5000})
            since = since_next
            limit = limit - 5000
        intervals.append({'since': since, 'limit': limit})
    #print(intervals)

    '''
    df_result = pd.DataFrame()
    for interval in intervals:
        df = pd.DataFrame(exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=interval["since"], limit=interval["limit"]))
        df = df.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        df = df.set_index(df['timestamp'])
        df.index = pd.to_datetime(df.index, unit='ms')
        del df['timestamp']
        df_result = pd.concat([df_result, df])
    '''

    everything_ok = True
    df_results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(exchange.fetch_ohlcv, symbol, timeframe, interval["since"], interval["limit"]): interval["since"] for interval in intervals}
        for future in concurrent.futures.as_completed(futures):
            current_since = futures[future]
            res = future.result()
            df = pd.DataFrame(res)
            #if df.empty:
            #    everything_ok = False
            df_results[current_since] = df

    if not everything_ok:
        return None

    ordered_df_results = [df_results[interval['since']] for interval in intervals]
    df_result = pd.concat(ordered_df_results)
    df_result = df_result.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
    if df_result.empty:
        return "no data"
    df_result = df_result.set_index(df_result['timestamp'])
    df_result.index = pd.to_datetime(df_result.index, unit='ms')
    #del df_result['timestamp']

    return df_result


def _custom_filter(symbol):
    return (symbol[-4:] in ["/EUR", "/USD"] or symbol[-5:] in ["/EURS"]) and ("BTC" in symbol or "ETH" in symbol or "BNB" in symbol)

def _get_exchange(exchange_market):
    exchange = None
    if exchange_market == "hitbtc":
        exchange = ccxt.hitbtc()
    elif exchange_market == "bitmex":
        exchange = ccxt.bitmex()
    elif exchange_market == "binance":
        exchange = ccxt.binance()
    elif exchange_market == "kraken":
        exchange = ccxt.kraken()
    elif exchange_market == "ftx":
        exchange = ccxt.ftx()
    return exchange

def get_exchange_and_markets(exchange_name):
    exchange = _get_exchange(exchange_name)
    if exchange == None:
        return None, {}

    markets = exchange.load_markets()
    return exchange, markets

def get_list_symbols(exchange_name):
    exchange, markets = get_exchange_and_markets(exchange_name)
    if bool(exchange) == False:
        return []

    symbols = exchange.symbols
    symbols = list(filter(_custom_filter, symbols))

    return symbols

def get_dataframe_symbols(exchange):
    symbols = get_list_symbols(exchange)
    n = len(symbols)
    df = utils.make_df_stock_info(symbols, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)

    return df

def get_list_symbols_hitbtc():
    return get_list_symbols("hitbtc")

def get_list_symbols_bitmex():
    return get_list_symbols("bitmex")

def get_list_symbols_binance():
    return get_list_symbols("binance")

def get_list_symbols_ftx():
    return get_list_symbols("ftx")

def get_symbol_ticker(exchange_market, symbol):
    exchange = _get_exchange(exchange_market)
    if exchange == None:
        return []

    exchange.load_markets()
    if symbol not in exchange.symbols:
        return {}

    ticker = exchange.fetch_ticker(symbol)
    return ticker

def get_symbol_ohlcv(exchange_name, symbol, start=None, end=None, timeframe="1d", length=None, indicators={}):
    # manage some errors
    if exchange_name == "hitbtc" and length and length > 1000:
        return "for hitbtc, length must be in [1, 1000]"

    exchange = _get_exchange(exchange_name)
    if exchange == None:
        return "exchange not found"

    exchange.load_markets()
    if symbol not in exchange.symbols or exchange.has['fetchOHLCV'] == False:
        print("symbol not found: ", symbol)
        return "symbol not found"
    
    start = utils.convert_string_to_datetime(start)
    end = utils.convert_string_to_datetime(end)

    # as we want the end date included, one adds a delta
    if timeframe == "1d":
        end += datetime.timedelta(days=1)
    elif timeframe == "1h":
        end += datetime.timedelta(hours=1)
    elif timeframe == "1m":
        end += datetime.timedelta(minutes=1)

    # request a start earlier according to what the indicators need
    start_with_period = start
    max_period = inc_indicators.get_max_window_size(indicators)
    if max_period != 0:
        if timeframe == "1d":
            start_with_period = start_with_period + datetime.timedelta(days=-max_period)
        elif timeframe == "1h":
            start_with_period = start_with_period + datetime.timedelta(hours=-max_period)
        elif timeframe == "1m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-max_period)

    ohlcv = _get_ohlcv(exchange, symbol, start_with_period, end, timeframe, length)
    if not isinstance(ohlcv, pd.DataFrame):
        return ohlcv

    # remove dupicates
    ohlcv = ohlcv[~ohlcv.index.duplicated()]

    # add potential missing dates
    map_timeframe_freq = {"1h": "H", "1d": "D", "1m": "min"}
    freq = map_timeframe_freq[timeframe]
    if end == None and length == None:
        end = date.today()
        end = end.strftime("%Y-%m-%d")

    expected_range = pd.date_range(start=start_with_period, end=end, freq=freq, closed="left")
    ohlcv.index = pd.DatetimeIndex(ohlcv.index)
    ohlcv = ohlcv.reindex(expected_range, fill_value=np.nan)

    if len(indicators) != 0:
        indicator_params = {"symbol": symbol, "exchange": exchange_name}
        ohlcv = inc_indicators.compute_indicators(ohlcv, indicators, True, indicator_params)

    if max_period != 0:
        ohlcv = ohlcv.iloc[max_period:]

    return ohlcv

###
### gainers
###
def get_top_gainers(exchange_name, n):
    exchange, markets = get_exchange_and_markets(exchange_name)
    symbols = exchange.symbols

    # filters on symbols ending with "/USDT"
    end = "/USDT"
    symbols = [symbol for symbol in symbols if (symbol[-len(end):] == end and "BULL" not in symbol and "HALF" not in symbol and "EDGE" not in symbol and "BEAR" not in symbol)]

    # get info for each symbol
    volume_threshold = 10000
    df = pd.DataFrame(columns=["symbol", "volume", "change"])
    with concurrent.futures.ThreadPoolExecutor(30) as executor:
        futures = {executor.submit(exchange.fetch_ticker, symbol): symbol for symbol in symbols}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            volume = float(result["info"]["volume"])
            if volume > volume_threshold:
                entry = pd.DataFrame.from_dict({
                    "symbol": [result["symbol"]],
                    "volume": [volume],
                    "change": [result["change"]]
                })
                df = pd.concat([df, entry], ignore_index=True)

    # sort symbols according descending change
    df.sort_values(by=["change"], ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
    df["rank"] = df.index
    df = df.head(n)

    return df
