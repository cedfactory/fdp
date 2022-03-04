import pandas as pd
import ccxt
from . import utils

def custom_filter(symbol):
    if(
        symbol[-4:] == "/USD"
        and "BULL" not in symbol
        and "HALF" not in symbol
        and "EDGE" not in symbol
        and "BEAR" not in symbol
    ):
        return True

def get_list_ftx():
    exchange = ccxt.ftx()
    symbols = exchange.symbols

    symbols = list(filter(custom_filter, symbols))

    df_symbol = pd.DataFrame(symbols, columns=['Symbols'])

    return df_symbol

def get_list_ftx_clean():
    exchange = ccxt.ftx()
    symbols = exchange.symbols
    df_list = {}

    symbols = list(filter(custom_filter, symbols))

    # Remove Crypto with low volume
    for symbol in symbols:
        ohlcv = get_ohlcv(symbol, "1h")
        if ohlcv["volume"].mean() > 10000:
            df_list[symbol] = ohlcv

    df_list_origin = df_list.copy()
    # Remove Crypto with missing data
    for symbol in df_list_origin:
        if len(df_list[symbol]) < 5000:
            del df_list[symbol]

    full_df = pd.DataFrame()
    for symbol in df_list:
        full_df[symbol] = df_list[symbol]['close']

    df_symbol = pd.DataFrame(full_df.columns, columns=['Symbols'])

    return df_symbol
