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

    def test_remove_rows_where_recommendation_not_in_filter(self):
        df_symbol = pd.DataFrame({
        'RECOMMENDATION_15m': ['BUY', 'BUY', 'NEUTRAL', 'STRONG_BUY', 'BUY', 'NEUTRAL'],
        'RECOMMENDATION_30m': ['BUY', 'SELL', 'BUY', 'STRONG_BUY', 'STRONG_BUY', 'NEUTRAL'],
        'RECOMMENDATION_1h': ['BUY', 'STRONG_BUY', 'STRONG_BUY', 'STRONG_SELL', 'STRONG_BUY', 'SELL'],
        'foobar': ['NEUTRAL', 'NEUTRAL', 'SELL', 'SELL', 'STRONG_SELL', 'BUY'],
        'value': [1, 2, 3, 4, 5, 6],
        })
        filter = ['BUY', 'STRONG_BUY']
        df_symbol = crypto.remove_rows_where_recommendation_not_in_filter(df_symbol, filter)
        assert(len(df_symbol.index) == 2)
