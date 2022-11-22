import pytest
import pandas as pd

from src import data_recorder

class TestCryptoCache:

    def test_crypto_cache(self):
        # context
        data = [["BTC/USDT","binance","2022-01-01 00:00:00","2022-02-01 00:00:00","1d"]]
        df_symbols_param = pd.DataFrame(data, columns=["symbol", "exchange_name", "start_date", "end_date", "interval"])
        features = {"close": None, "low": None, "high": None, "ema_5": None}

        # action
        cache = data_recorder.CryptoCache(df_symbols_param, "BTC/USDT", features)

        # expectations
        assert(cache.symbol == "BTC/USDT")
        assert(cache.exchange_name == "binance")
        assert(cache.interval == "1d")
        assert(len(cache.ohlcv) == 32)
        columns = cache.ohlcv.columns.tolist()
        assert(columns == ["high", "low", "close", "ema_5"])

        