import pytest
import pandas as pd
import json

from src import api
from . import test_utils

class TestApi:

    def test_api_list_cac(self):
        response = api.api_list("w_cac")
        assert(response["status"] == "ok")
        assert("w_cac" in response["result"])
        assert(response["result"]["w_cac"]["status"] == "ok")
        
        symbols = response["result"]["w_cac"]["symbols"]
        df = pd.read_csv("./test/references/wiki_list_cac.csv")
        symbols_reference = df["symbol"].to_list()
        symbols_reference = ','.join(symbols_reference)
        assert(symbols == symbols_reference)

    def test_api_symbol(self):
        symbol = "ETH/EUR"
        response = api.api_symbol("crypto", "ftx", symbol)
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert(symbol in response["result"])
        assert(response["result"][symbol]["status"] == "ok")
        assert("status" in response["result"][symbol])
        assert(response["result"][symbol]["status"] == "ok")
        assert("info" in response["result"][symbol])
        assert(response["result"][symbol]["info"]["symbol"] == symbol)

    def test_api_history(self):
        symbol = "BTC_EURS"
        response = api.api_history("hitbtc", symbol, "05_12_2021", str_interval="1d", length=100)
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert(symbol in response["result"])
        assert(response["result"][symbol]["status"] == "ok")
        assert("status" in response["result"][symbol])
        assert(response["result"][symbol]["status"] == "ok")
        assert("info" in response["result"][symbol])
        df_data = response["result"][symbol]["info"]
        ohlcv = pd.read_json(df_data)
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 100)

    def test_api_indicators(self):
        symbol = "BTC_EURS"
        map_indicators = {"close" : None, "high" : None}
        response = api.api_indicators(map_indicators, "hitbtc", symbol, "05_12_2021", str_interval="1d", length=100)
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert(symbol in response["result"])
        assert(response["result"][symbol]["status"] == "ok")
        assert("status" in response["result"][symbol])
        assert(response["result"][symbol]["status"] == "ok")
        assert("info" in response["result"][symbol])
        df_data = response["result"][symbol]["info"]
        ohlcv = pd.read_json(df_data)
        assert(isinstance(ohlcv, pd.DataFrame))
        assert(len(ohlcv.index) == 100)
        assert(list(ohlcv.columns) == ["high", "close"])

    def test_api_recommendations_for_symbol(self):
        screener = "crypto"
        exchange = "ftx"
        symbol = "1INCHUSD"
        response = api.api_recommendations(screener, exchange, symbol, "1h")
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert(symbol in response["result"])
        assert(response["result"][symbol]["status"] == "ok")
        assert("status" in response["result"][symbol])
        assert(response["result"][symbol]["status"] == "ok")
        assert("RECOMMENDATION" in response["result"][symbol])
        assert(response["result"][symbol]["RECOMMENDATION"] in ["STRONG_BUY", "BUY", "NEUTRAL", "SELL", "STRONG_SELL"])

    def test_api_recommendations_for_exchange(self):
        screener = "crypto"
        exchange = "ftx"
        symbol = None
        response = api.api_recommendations(screener, exchange, symbol, "1h")
        arbitrary_symbol = "BNBUSD"
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert(arbitrary_symbol in response["result"])
        assert(response["result"][arbitrary_symbol]["status"] == "ok")
        assert("status" in response["result"][arbitrary_symbol])
        assert(response["result"][arbitrary_symbol]["status"] == "ok")
        assert("RECOMMENDATION" in response["result"][arbitrary_symbol])
        assert(response["result"][arbitrary_symbol]["RECOMMENDATION"] in ["STRONG_BUY", "BUY", "NEUTRAL", "SELL", "STRONG_SELL"])

    def test_api_portfolio(self):
        response = api.api_portfolio()
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert("symbols" in response["result"])
        df = pd.read_json(response["result"]["symbols"])
        assert(isinstance(df, pd.DataFrame))
