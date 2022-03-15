import pytest
import pandas as pd

from src import crypto

class TestCrypto:

    def test_get_list_symbols(self):
        symbols = crypto.get_list_symbols("hitbtc")
        assert(len(symbols) == 19)

    def test_get_symbol_ticker(self):
        info = crypto.get_symbol_ticker("hitbtc", "BTC/EURS")
        assert("symbol" in info)
        assert(info["symbol"] == "BTC/EURS")

    def test_get_symbol_ohlcv(self):
        ohlcv = crypto.get_symbol_ohlcv("hitbtc", "BTC/EURS")
        assert(isinstance(ohlcv, pd.DataFrame))
