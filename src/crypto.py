import pandas as pd
import ccxt
from . import utils

def _get_ohlcv(exchange, symbol, tf, limit=100):
    df = pd.DataFrame(exchange.fetch_ohlcv(symbol, tf, limit=limit))
    df = df.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index, unit='ms')
    del df['timestamp']
    return df

def _custom_filter(symbol):
    #return symbol[-4:] == "/USD" and "BULL" not in symbol and "HALF" not in symbol and "EDGE" not in symbol and "BEAR" not in symbol
    return ("BTC" in symbol or "ETH" in symbol) and ("EUR" in symbol or "USD" in symbol)

def _get_exchange(exchange_market):
    exchange = None
    if exchange_market == "hitbtc":
        exchange = ccxt.hitbtc()
    elif exchange_market == "bitmex":
        exchange = ccxt.bitmex()
    return exchange

def get_list_symbols(exchange_market):
    exchange = _get_exchange(exchange_market)
    if exchange == None:
        return []

    exchange.load_markets()
    symbols = exchange.symbols
    symbols = list(filter(_custom_filter, symbols))

    n = len(symbols)
    df = utils.make_df_stock_info(symbols, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n, [''] * n)

    return df

def get_list_symbols_hitbtc():
    return get_list_symbols("hitbtc")

def get_list_symbols_bitmex():
    return get_list_symbols("bitmex")

def get_symbol_ticker(exchange_market, symbol):
    exchange = _get_exchange(exchange_market)
    if exchange == None:
        return []

    exchange.load_markets()
    if symbol not in exchange.symbols:
        return {}

    ticker = exchange.fetch_ticker(symbol)
    return ticker

def get_symbol_ohlcv(exchange_market, symbol, period="1d", length=200):
    exchange = _get_exchange(exchange_market)
    if exchange == None:
        return {}

    exchange.load_markets()
    if symbol not in exchange.symbols or exchange.has['fetchOHLCV'] == False:
        return {}

    ohlcv = _get_ohlcv(exchange, symbol, period, length)
    return ohlcv
