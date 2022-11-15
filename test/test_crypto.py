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
        columns = ohlcv.columns.tolist()
        assert(columns == ["timestamp", "open", "high", "low", "close", "volume"])
        assert(ohlcv.iloc[0]["timestamp"] == 1646092800000)
        assert(ohlcv.iloc[0]["open"] == 38446.31)
        assert(ohlcv.iloc[0]["high"] == 39577.67)
        assert(ohlcv.iloc[0]["low"] == 38344.53)
        assert(ohlcv.iloc[0]["close"] == 39301.7)
        assert(ohlcv.iloc[0]["volume"] == 0.02559)
        assert(ohlcv.iloc[60]["timestamp"] == 1651276800000)
        assert(ohlcv.iloc[60]["open"] == 36750.07)
        assert(ohlcv.iloc[60]["high"] == 36901.75)
        assert(ohlcv.iloc[60]["low"] == 35760.06)
        assert(ohlcv.iloc[60]["close"] == 35836.63)
        assert(ohlcv.iloc[60]["volume"] == 23.71129)

    def test_get_symbol_ohlcv_with_timestamp(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "BTC/EURS", "1646092800000", "1651363200000")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 61)
        columns = ohlcv.columns.tolist()
        assert(columns == ["timestamp", "open", "high", "low", "close", "volume"])
        assert(ohlcv.iloc[0]["timestamp"] == 1646092800000)
        assert(ohlcv.iloc[0]["open"] == 38446.31000)
        assert(ohlcv.iloc[0]["high"] == 39577.67000)
        assert(ohlcv.iloc[0]["low"] == 38344.53000)
        assert(ohlcv.iloc[0]["close"] == 39301.70000)
        assert(ohlcv.iloc[0]["volume"] == 0.02559)
        assert(ohlcv.iloc[60]["timestamp"] == 1651276800000)
        assert(ohlcv.iloc[60]["open"] == 36750.07)
        assert(ohlcv.iloc[60]["high"] == 36901.75)
        assert(ohlcv.iloc[60]["low"] == 35760.06)
        assert(ohlcv.iloc[60]["close"] == 35836.63)
        assert(ohlcv.iloc[60]["volume"] == 23.71129)

    def test_get_symbol_ohlcv_with_data_before_existing(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "ETH/EURS", "2018-07-23", "2018-07-25", "1h")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 48)

    def test_get_symbol_ohlcv_limit_h(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "ETH/EURS", "2020-01-01 08:00:00", "2020-01-01 16:00:00", "1h")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 8)

    def test_get_symbol_ohlcv_limit_m(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "ETH/EURS", "2020-01-01 08:00:00", "2020-01-01 09:12:00", "1m")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 72)

    def test_get_top_gainers(self):
        df = crypto.get_top_gainers("binance", 50)
        assert(isinstance(df, pd.DataFrame))
        assert(df.columns.to_list() == ['symbol', 'volume', 'change', 'rank'])
        symbols = df['symbol'].to_list()
        assert(len(symbols) > 1)
