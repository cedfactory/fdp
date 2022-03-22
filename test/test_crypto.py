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
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "BTC/EURS")
        assert(isinstance(ohlcv, pd.DataFrame))

    def test_get_top_gainers(self):
        df = crypto.get_top_gainers(50)
        assert(isinstance(df, pd.DataFrame))
        assert(df.columns.to_list() == ['symbol', 'change1h', 'rank_change1h', 'change24h', 'rank_change24h'])
        symbols = df['symbol'].to_list()
        assert(len(symbols) > 1)
