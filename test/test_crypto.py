import pytest
import pandas as pd

from src import crypto

class TestCrypto:

    def test_get_list_symbols_hitbtc(self):
        symbols = crypto.get_list_symbols_hitbtc()
        assert(symbols == ["BTC/EURS", "ETH/EURS"])

    def test_get_list_symbols_bitmex(self):
        symbols = crypto.get_list_symbols_bitmex()
        assert(symbols == [])

    def test_get_list_symbols_binance(self):
        symbols = crypto.get_list_symbols_binance()
        assert(symbols == ["BNB/EUR", "BTC/EUR", "ETH/EUR"])

    def test_get_list_symbols_kraken(self):
        symbols = crypto.get_list_symbols_kraken()
        assert(symbols == ["BTC/EUR", "BTC/USD", "ETH/EUR", "ETH/USD", "ETHW/EUR", "ETHW/USD", "TBTC/EUR", "TBTC/USD", "WBTC/EUR", "WBTC/USD"])

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

    def test_get_symbol_ticker_ko_no_exchange(self):
        info = crypto.get_symbol_ticker("fake_exchange", "BTC/EURS")
        assert(info == {})

    def test_get_symbol_ticker_ko_no_symbol(self):
        info = crypto.get_symbol_ticker("bitmex", "fake_crypto")
        assert(info == {})

    def test_get_symbol_ohlcv(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "BTC/EURS", "2022-03-01", "2022-05-01")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 62)
        columns = ohlcv.columns.tolist()
        assert(columns == ["timestamp", "open", "high", "low", "close", "volume"])
        assert(ohlcv.iloc[0]["timestamp"] == 1646092800000)
        assert(ohlcv.iloc[0]["open"] == 38446.31)
        assert(ohlcv.iloc[0]["high"] == 39577.67)
        assert(ohlcv.iloc[0]["low"] == 38344.53)
        assert(ohlcv.iloc[0]["close"] == 39301.7)
        assert(ohlcv.iloc[0]["volume"] == 0.02559)
        assert(ohlcv.iloc[61]["timestamp"] == 1651363200000)
        assert(ohlcv.iloc[61]["open"] == 35819.56)
        assert(ohlcv.iloc[61]["high"] == 36777.42)
        assert(ohlcv.iloc[61]["low"] == 35601.47)
        assert(ohlcv.iloc[61]["close"] == 36583.49)
        assert(ohlcv.iloc[61]["volume"] == 15.42320)

    def test_get_symbol_ohlcv_with_timestamp(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "BTC/EURS", "1646092800000", "1651363200000")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 62)
        columns = ohlcv.columns.tolist()
        assert(columns == ["timestamp", "open", "high", "low", "close", "volume"])
        assert(ohlcv.iloc[0]["timestamp"] == 1646092800000)
        assert(ohlcv.iloc[0]["open"] == 38446.31000)
        assert(ohlcv.iloc[0]["high"] == 39577.67000)
        assert(ohlcv.iloc[0]["low"] == 38344.53000)
        assert(ohlcv.iloc[0]["close"] == 39301.70000)
        assert(ohlcv.iloc[0]["volume"] == 0.02559)
        assert(ohlcv.iloc[61]["timestamp"] == 1651363200000)
        assert(ohlcv.iloc[61]["open"] == 35819.56)
        assert(ohlcv.iloc[61]["high"] == 36777.42)
        assert(ohlcv.iloc[61]["low"] == 35601.47)
        assert(ohlcv.iloc[61]["close"] == 36583.49)
        assert(ohlcv.iloc[61]["volume"] == 15.42320)

    def test_get_symbol_ohlcv_with_data_before_existing(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "ETH/EURS", "2018-07-23", "2018-07-25", "1h")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 49)

    def test_get_symbol_ohlcv_limit_h(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "ETH/EURS", "2020-01-01 08:00:00", "2020-01-01 16:00:00", "1h")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 9)

    def test_get_symbol_ohlcv_limit_m(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "ETH/EURS", "2020-01-01 08:00:00", "2020-01-01 09:12:00", "1m")
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 73)
    '''
    def test_get_top_gainers(self):
        df = crypto.get_top_gainers("binance", 50)
        assert(isinstance(df, pd.DataFrame))
        assert(df.columns.to_list() == ['symbol', 'volume', 'change', 'rank'])
        symbols = df['symbol'].to_list()
        assert(len(symbols) > 1)
    '''
    def test_get_symbol_ohlcv_with_indicators(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "BTC/EURS", "2020-01-12", "2020-01-16", "1d", None, ["er"])
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 5)
        assert(ohlcv["er"][0] == pytest.approx(0.502285, 0.0001))
        assert(ohlcv["er"][1] == pytest.approx(0.432288, 0.0001))
        assert(ohlcv["er"][2] == pytest.approx(0.588735, 0.0001))
        assert(ohlcv["er"][3] == pytest.approx(0.565369, 0.0001))
        assert(ohlcv["er"][4] == pytest.approx(0.441592, 0.0001))
