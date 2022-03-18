import pytest
import pandas as pd

from src import api
from . import test_utils

class TestApi:

    def test_api_list_cac(self):
        response = api.api_list("w_cac")
        assert(response["status"] == "ok")
        assert("w_cac" in response["result"])
        assert(response["result"]["w_cac"]["status"] == "ok")
        
        df_data = response["result"]["w_cac"]["dataframe"]
        df = pd.read_json(df_data)
        test_utils.check_expectations(df, "wiki_list_cac.csv")

    def test_api_value(self):
        symbol = "AI.PA"
        response = api.api_value(symbol)
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
        response = api.api_history("hitbtc", symbol, "05_12_2021", 100)
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

    def test_api_recommendations(self):
        screener = "crypto"
        exchange = "ftx"
        symbol = "1INCHUSD"
        response = api.api_recommendations(screener, exchange, symbol, "1h")
        print(response)
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert(symbol in response["result"])
        assert(response["result"][symbol]["status"] == "ok")
        assert("status" in response["result"][symbol])
        assert(response["result"][symbol]["status"] == "ok")
        assert("RECOMMENDATION" in response["result"][symbol])
        assert(response["result"][symbol]["RECOMMENDATION"] in ["STRONG_BUY", "BUY", "NEUTRAL", "SELL", "STRONG_SELL"])
