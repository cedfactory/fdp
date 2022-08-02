import pytest
import pandas as pd
import json
#from dataclasses import dataclass

from src import api
from . import test_utils


class MockRequest:
    def __init__(self):
        self.method = ""
        self.args = {}
        self.form = {}

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

    def test_api_history_parse_parameters_get_ok(self):
        req = MockRequest
        req.method = "GET"
        req.args = {}
        req.args["exchange"] = "hitbtc"
        req.args["symbol"] = "ETH/EURS"
        req.args["start"] = "2022-02-01"
        history_params = api.api_history_parse_parameters(req)

        assert(history_params.get("status") == "ok")

    def test_api_history_parse_parameters_get_ko_exchange_not_specified(self):
        req = MockRequest
        req.method = "GET"
        req.args = {}
        req.args["symbol"] = "ETH/EURS"
        req.args["start"] = "2022-02-01"
        history_params = api.api_history_parse_parameters(req)

        assert(history_params.get("status") == "ko")
        assert(history_params.get("reason") == "exchange not specified")

    def test_api_history_parse_parameters_post_ok(self):
        req = MockRequest
        req.method = "POST"
        req.form = {}
        req.form["exchange"] = "hitbtc"
        req.form["symbol"] = "ETH/EURS"
        req.form["start"] = "2022-02-01"
        history_params = api.api_history_parse_parameters(req)

        assert(history_params.get("status") == "ok")

    def test_api_history_parse_parameters_post_ko_exchange_not_specified(self):
        req = MockRequest
        req.method = "POST"
        req.form = {}
        req.form["symbol"] = "ETH/EURS"
        req.form["start"] = "2022-02-01"
        history_params = api.api_history_parse_parameters(req)

        assert(history_params.get("status") == "ko")
        assert(history_params.get("reason") == "exchange not specified")

    def test_api_history(self):
        symbol = "BTC_EURS"
        params_history = {"str_exchange":"hitbtc", "str_symbol":symbol, "str_start":"2021-12-05", "str_end": "2022-01-05", "str_interval":"1d"}
        response = api.api_history(params_history)
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
        assert(len(ohlcv.index) == 31)

    def test_api_indicators(self):
        symbol = "BTC_EURS"
        indicators = ["close", "high", "ema_30"]
        params_history = {"str_exchange":"hitbtc", "str_symbol":symbol, "str_start":"2021-12-05", "str_end": "2022-01-05", "str_interval":"1d", "indicators":indicators}
        response = api.api_history(params_history)
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
        assert(len(ohlcv.index) == 31)
        assert(list(ohlcv.columns) == ["index", "high", "close", "ema_30"])

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
