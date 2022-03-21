import pandas as pd
import ccxt
import time
from datetime import datetime
from . import utils

'''
format for since : dd_mm_yyyy
'''
def _get_ohlcv(exchange, symbol, start, timeframe, length=100):
    if start != None:
        start = int(time.mktime(datetime.strptime(start, "%d_%m_%Y").timetuple()))*1000
    df = pd.DataFrame(exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=start, limit=length))
    df = df.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index, unit='ms')
    del df['timestamp']
    return df

def _custom_filter(symbol):
    #return symbol[-4:] == "/USD" and "BULL" not in symbol and "HALF" not in symbol and "EDGE" not in symbol and "BEAR" not in symbol
    #return ("BTC" in symbol or "ETH" in symbol or "BNB" in symbol) and ("EUR" in symbol or "USD" in symbol)
    return (symbol[-4:] in ["/EUR", "/USD"] or symbol[-5:] in ["/EURS"]) and ("BTC" in symbol or "ETH" in symbol or "BNB" in symbol)

def _get_exchange(exchange_market):
    exchange = None
    if exchange_market == "hitbtc":
        exchange = ccxt.hitbtc()
    elif exchange_market == "bitmex":
        exchange = ccxt.bitmex()
    elif exchange_market == "binance":
        exchange = ccxt.binance()
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

def get_symbol_ohlcv(exchange_market, symbol, start=None, timeframe="1d", length=100):
    # manage some errors
    if exchange_market == "hitbtc" and length > 1000:
        return "for hitbtc, length must be in [1, 1000]"

    exchange = _get_exchange(exchange_market)
    if exchange == None:
        return "exchange not found"

    exchange.load_markets()
    if symbol not in exchange.symbols or exchange.has['fetchOHLCV'] == False:
        return "symbol not found"

    ohlcv = _get_ohlcv(exchange, symbol, start, timeframe, length)
    return ohlcv
