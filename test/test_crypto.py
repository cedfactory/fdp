import pytest
import pandas as pd

from src import crypto

class TestCrypto:

    def test_get_dataframe_symbols(slef):
        df_symbols = crypto.get_dataframe_symbols("binance")
        assert(len(df_symbols.index) == 3)

    def test_get_list_symbols(self):
        symbols = crypto.get_list_symbols("hitbtc")
        assert(len(symbols) == 2)

    def test_get_list_symbols_bad_exchange(self):
        symbols = crypto.get_list_symbols("foobar")
        assert(len(symbols) == 0)

    def test_get_symbol_ticker(self):
        info = crypto.get_symbol_ticker("hitbtc", "BTC/EURS")
        assert("symbol" in info)
        assert(info["symbol"] == "BTC/EURS")

    def test_get_symbol_ohlcv(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "BTC/EURS", "2022-03-01", "2022-05-01")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 61)

    def test_get_symbol_ohlcv_with_data_before_existing(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "ETH/EURS", "2018-07-23", "2018-07-25", "1h")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 48)

    def test_get_top_gainers(self):
        df = crypto.get_top_gainers("binance", 50)
        assert(isinstance(df, pd.DataFrame))
        assert(df.columns.to_list() == ['symbol', 'volume', 'change', 'rank'])
        symbols = df['symbol'].to_list()
        assert(len(symbols) > 1)
