import pandas as pd
import numpy as np
import ccxt
import time
from datetime import datetime, timedelta
from datetime import datetime, timezone
from datetime import date
import datetime
from . import utils
from . import indicators as inc_indicators
import concurrent.futures
from . import ws_global

import requests

def _get_ohlcv_bitget_v1(symbol, timeframe="1h", limit=100):
    """
    Fetch the latest 'limit' OHLCV candles for a given futures symbol, product type, and timeframe
    from Bitget's Futures Market API.

    Args:
        symbol (str): Trading symbol (e.g., "BTCUSDT").
        timeframe (str): Candle timeframe (e.g., "1d", "1h", etc.). Default is "1d".
        limit (int): Number of candles to fetch.

    Returns:
        list: A list of candles (each typically a list or dict depending on API response),
              or None if an error occurred.
    """

    # if we receive BTC/USDT, we convert it into BTCUSDT
    symbol = symbol.replace("/", "")

    base_url = "https://api.bitget.com"
    endpoint = "/api/v2/mix/market/candles"
    url = base_url + endpoint

    # Map common timeframe abbreviations to the API-required format.
    timeframe_mapping = {
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1H",
        "4h": "4H",
        "6h": "6H",
        "12h": "12H",
        "1d": "1D",
        "1w": "1W",
        "1M": "1Mutc"
    }
    period = timeframe_mapping.get(timeframe, timeframe)

    params = {
        "symbol": symbol,
        "granularity": period,
        "limit": str(limit),
        "productType": "USDT-FUTURES"  # added productType parameter for futures
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for unsuccessful responses
        data = response.json()
        if data.get("code") != "00000":
            raise Exception(f"API error: {data.get('msg', 'Unknown error')} (code: {data.get('code')})")

        candle_data = data.get("data", [])
        # Assuming each candle is in the format:
        # [timestamp, open, high, low, close, volume]
        df = pd.DataFrame(candle_data, columns=["timestamp", "open", "high", "low", "close", "volume", "volume_2"])
        df = df.drop(columns=['volume_2'])
        df = df.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        cols = ["open", "high", "low", "close", "volume"]
        df[cols] = df[cols].astype(float)

        if df.empty:
            return "no data"
        df = df.set_index(df['timestamp'])
        df.index = df.index.str.replace(r'0{3}$', '', regex=True)
        df.index = pd.to_datetime(df.index.astype(int), unit='s', utc=True, errors='coerce')

        return df
    except Exception as e:
        print("Error fetching futures OHLCV data:", e)
        return None

def _get_ohlcv_bitget_v2(symbol, timeframe="1h", limit=100):
        # symbol = utils.convert_symbol_to_bitget(symbol)
        symbol = symbol.replace("/", "")

        base_url = "https://api.bitget.com"
        endpoint = "/api/v2/mix/market/candles"

        url = base_url + endpoint

        granularity_mapping = {
            "1m": "1m",
            "3m": "3m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1H",
            "4h": "4H",
            "6h": "6H",
            "12h": "12H",
            "1d": "1D",
            "1w": "1W"
        }

        params = {
            "symbol": symbol,
            "productType": "USDT-FUTURES",
            "granularity": granularity_mapping[timeframe],
            "limit": str(limit)
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises an HTTPError for unsuccessful responses
            candle_data = response.json()

            # Assuming each candle is in the format:
            # [timestamp, open, high, low, close, volume]
            df = pd.DataFrame(candle_data["data"], columns=["timestamp", "open", "high", "low", "close", "volume", "volume_2"])
            df = df.drop(columns=['volume_2'])
            df = df.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
            cols = ["open", "high", "low", "close", "volume"]
            df[cols] = df[cols].astype(float)
            cols = ["timestamp"]

            if df.empty:
                return "no data"
            df = df.set_index(df['timestamp'])
            df.index = df.index.str.replace(r'0{3}$', '', regex=True)
            df.index = pd.to_datetime(df.index.astype(int), unit='s', utc=True, errors='coerce')
            return df
        except Exception as e:
            print("Error fetching futures OHLCV data:", e)
            return None

def _get_ohlcv_bitget(symbol, timeframe, limit, version="V2"):
    if version == "V2":
        return _get_ohlcv_bitget_v2(symbol, timeframe, limit)
    else:
        return _get_ohlcv_bitget_v1(symbol, timeframe, limit)

def _get_ohlcv_bitget(symbol, timeframe, limit):
    """
    DEBUG CEDE
    last_dt = utils.get_last_tick_datetime(timeframe)
    released_dt = utils.get_released_tick_datetime(timeframe)
    print("now (UTC):", datetime.datetime.now(datetime.timezone.utc))
    print("now:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("last_dt: ", last_dt)
    print("released_dt: ", released_dt)
    """
    released_dt = utils.get_released_tick_datetime(timeframe)
    df_ws_ohlv = ws_global.ws_candle.get_ohlcv(symbol, timeframe, limit)

    checks = {
        "is_not_none": df_ws_ohlv is not None,
        "is_dataframe": isinstance(df_ws_ohlv, pd.DataFrame),
        "limit": False,
        "tick_in": False,
    }

    if checks["is_not_none"]:
        checks["limit"] = len(df_ws_ohlv) >= limit
        checks["tick_in"] = utils.is_released_tick_in_df(df_ws_ohlv, timeframe)

    if all(checks.values()):
        df_ws_ohlv = df_ws_ohlv.loc[:released_dt]
        ws_global.ws_traces_increment_success()
        df_ws_ohlv["source"] = "WS"
        return df_ws_ohlv

    error_map = {
        "_NONE": not checks["is_not_none"],
        "_NOT_DF": not checks["is_dataframe"],
        "_LIMIT": not checks["limit"],
        "_NO_TICK": not checks["tick_in"],
    }

    error_code = next((code for code, failed in error_map.items() if failed), None)
    ws_global.ws_traces_increment_failure(
        is_not_none=checks["is_not_none"],
        is_dataframe=checks["is_dataframe"],
        limit=checks["limit"],
        tick_in=checks["tick_in"],
    )

    df_api_ohlv = _get_ohlcv_bitget_v2(symbol, timeframe, limit)
    df_api_ohlv = df_api_ohlv.loc[:released_dt]
    df_ws_ohlv["source"] = "API" + error_code
    if isinstance(df_api_ohlv, pd.DataFrame):
        return df_api_ohlv

    return None

def _get_ohlcv(exchange, symbol, start, end=None, timeframe="1h", limit=100):
    return _get_ohlcv_bitget(symbol, timeframe, limit)

def _get_ohlcv_legacy(exchange, symbol, start, end=None, timeframe="1d", limit=None):

    if exchange == None or symbol == None or start == None:
        return None

    since = int(start.timestamp()) * 1000

    if end is not None:
        delta = end - start
        if timeframe == "1d":
            limit = delta.days  # days
        elif timeframe == "1h":
            limit = int(delta.total_seconds() / 3600)  # hours
        elif timeframe == "2h":
            limit = int(delta.total_seconds() / (2 * 3600))  # 2-hour intervals
        elif timeframe == "4h":
            limit = int(delta.total_seconds() / (4 * 3600))  # 4-hour intervals
        elif timeframe == "1m":
            limit = int(delta.total_seconds() / 60)  # minutes
        elif timeframe == "5m":
            limit = int(delta.total_seconds() / (5 * 60))  # 5-minute intervals
        elif timeframe == "15m":
            limit = int(delta.total_seconds() / (15 * 60))  # 15-minute intervals
        elif timeframe == "30m":
            limit = int(delta.total_seconds() / (30 * 60))  # 30-minute intervals

    if limit == None:
        return None

    intervals = []
    # offset is a param depending on the exchanger properties
    # binance offset = 1000
    if timeframe in ["1d", "1h", "1m", "5m", "15m", "30m", "2h", "4h"]:  # split into requests with limit = 5000
        if timeframe == "1d":
            offset = 1000 * 24 * 60 * 60 * 1000  # 1 day in milliseconds
        elif timeframe == "1h":
            offset = 1000 * 60 * 60 * 1000  # 1 hour in milliseconds
        elif timeframe == "2h":
            offset = 2 * 1000 * 60 * 60 * 1000  # 2 hours in milliseconds
        elif timeframe == "4h":
            offset = 4 * 1000 * 60 * 60 * 1000  # 4 hours in milliseconds
        elif timeframe == "1m":
            offset = 1000 * 60 * 1000  # 1 minute in milliseconds
        elif timeframe == "5m":
            offset = 5 * 1000 * 60 * 1000  # 5 minutes in milliseconds
        elif timeframe == "15m":
            offset = 15 * 1000 * 60 * 1000  # 15 minutes in milliseconds
        elif timeframe == "30m":
            offset = 30 * 1000 * 60 * 1000  # 30 minutes in milliseconds

        # Split into requests with limit = 5000
        while limit > 1000:
            since_next = since + offset
            intervals.append({'since': since, 'limit': 1000})
            since = since_next
            limit = limit - 1000
        intervals.append({'since': since, 'limit': limit})

    everything_ok = True
    df_results = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(exchange.fetch_ohlcv, symbol, timeframe, interval["since"], interval["limit"]): interval["since"] for interval in intervals}
        for future in concurrent.futures.as_completed(futures):
            current_since = futures[future]
            res = future.result()
            df = pd.DataFrame(res)
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
    elif exchange_market == "bitget":
        exchange = ccxt.bitget()
    elif exchange_market == "coinbase":
        exchange = ccxt.coinbase()
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

def get_list_symbols_kraken():
    return get_list_symbols("kraken")

def get_list_symbols_bitget():
    return get_list_symbols("bitget")

def get_list_symbols_coinbase():
    return get_list_symbols("coinbase")

def get_symbol_ticker(exchange_market, symbol):
    exchange = _get_exchange(exchange_market)
    if exchange == None:
        return {}

    exchange.load_markets()
    if symbol not in exchange.symbols:
        return {}

    ticker = exchange.fetch_ticker(symbol)
    return ticker

def get_symbol_ohlcv(exchange_name, symbol, start=None, end=None, timeframe="1d", length=None, indicators={}, exchange=None):

    # hack : find a better way
    if exchange_name == "bitget":
        symbol = symbol + "/USDT"

    # manage some errors
    if exchange_name == "hitbtc" and length and length > 1000:
        return "for hitbtc, length must be in [1, 1000]"

    if exchange == None:
        exchange = _get_exchange(exchange_name)
        if exchange == None:
            return "exchange not found"
        exchange.load_markets()

    # CEDE DEBUG:
    # lst_symbol = []
    # for exchange_symbol in exchange.symbols:
    #     if symbol in exchange_symbol:
    #         lst_symbol.append(exchange_symbol)
    # print(lst_symbol)

    if symbol not in exchange.symbols or exchange.has['fetchOHLCV'] == False:
        print("symbol not found: ", symbol)
        return "symbol not found"

    start, end = utils.get_date_range(start, end, timeframe, length)

    # request a start earlier according to what the indicators need
    start_with_period = start
    max_period = inc_indicators.get_max_window_size(indicators) + 1 # MODIF CEDE to be confirmed by CL
    #max_period = utils.max_from_dict_values(indicators)
    if max_period != 0:
        if timeframe == "1d":
            start_with_period = start_with_period + datetime.timedelta(days=-max_period)
        elif timeframe == "1h":
            start_with_period = start_with_period + datetime.timedelta(hours=-max_period)
        elif timeframe == "2h":
            start_with_period = start_with_period + datetime.timedelta(hours=-2 * max_period)
        elif timeframe == "4h":
            start_with_period = start_with_period + datetime.timedelta(hours=-4 * max_period)
        elif timeframe == "1m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-max_period)
        elif timeframe == "5m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-5 * max_period)
        elif timeframe == "15m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-15 * max_period)
        elif timeframe == "30m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-30 * max_period)

    ohlcv = _get_ohlcv(exchange, symbol, start_with_period, end, timeframe, length)
    if not isinstance(ohlcv, pd.DataFrame):
        return ohlcv

    # remove dupicates
    ohlcv = ohlcv[~ohlcv.index.duplicated()]

    if len(indicators) != 0:
        indicator_params = {"symbol": symbol, "exchange": exchange_name}
        ohlcv = inc_indicators.compute_indicators(ohlcv, indicators, True, indicator_params)

    if max_period != 0:
        ohlcv = ohlcv.iloc[max_period-1:-1] # WARNING CEDE to get the second to last candle instead of the last

    # ohlcv.interpolate(inplace=True) # CEDE WORKAROUND TO BE DISCUSSED WITH CL
    return ohlcv

def get_symbol_ohlcv_last(exchange_name, symbol, start=None, end=None, timeframe="1d", length=1, indicators={}, exchange=None, candle_stick="released"):

    # hack : find a better way
    if exchange_name == "bitget":
        symbol = symbol + "/USDT"

    # manage some errors
    if exchange_name == "hitbtc" and length and length > 1000:
        return "for hitbtc, length must be in [1, 1000]"

    '''if exchange == None:
        exchange = _get_exchange(exchange_name)
        if exchange == None:
            return "exchange not found"
        exchange.load_markets()

    if symbol not in exchange.symbols or exchange.has['fetchOHLCV'] == False:
        print("symbol not found: ", symbol)
        return "symbol not found"
    '''

    start, end = utils.get_date_range(start, end, timeframe, length)

    # request a start earlier according to what the indicators need
    start_with_period = start
    max_period = inc_indicators.get_max_window_size(indicators) + 1
    #max_period = utils.max_from_dict_values(indicators)
    if max_period != 0:
        if timeframe == "1d":
            start_with_period = start_with_period + datetime.timedelta(days=-max_period)
        elif timeframe == "1h":
            start_with_period = start_with_period + datetime.timedelta(hours=-max_period)
        elif timeframe == "2h":
            start_with_period = start_with_period + datetime.timedelta(hours=-2 * max_period)
        elif timeframe == "4h":
            start_with_period = start_with_period + datetime.timedelta(hours=-4 * max_period)
        elif timeframe == "1m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-max_period)
        elif timeframe == "5m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-5 * max_period)
        elif timeframe == "15m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-15 * max_period)
        elif timeframe == "30m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-30 * max_period)

    ohlcv = _get_ohlcv(exchange, symbol, start_with_period, end, timeframe, length)
    if not isinstance(ohlcv, pd.DataFrame):
        return ohlcv

    # remove dupicates
    ohlcv = ohlcv[~ohlcv.index.duplicated()]

    if len(indicators) != 0:
        indicator_params = {"symbol": symbol, "exchange": exchange_name}
        ohlcv = inc_indicators.compute_indicators(ohlcv, indicators, True, indicator_params)

    ohlcv = ohlcv.iloc[[-1]]
    # CEDE DEBUG
    print("ohlcv: ", ohlcv.to_string())
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
