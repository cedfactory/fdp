import pytest
import time
import pandas as pd
from src import bitget_ws_ticker, bitget_ws_account_tickers

class TestBitgetWS:

    def test_bitget_ws_ticker(self):
        # context
        params = {"id": "ws1"}
        ws = bitget_ws_ticker.FDPWSTicker(params)
        time.sleep(1)

        # action
        result = ws.request("last", params)
        print(result)

        # expectations
        assert(isinstance(result, pd.DataFrame))

        # cleaning
        ws.stop()

    def test_bitget_ws_account_tickers(self):
        # context
        params = {"tickers": ["BTCUSDT"],
                    "api_key": "XXX",
                    "api_secret": "XXX",
                    "api_passphrase": "XXX"}
        ws = bitget_ws_account_tickers.FDPWSAccountTickers(params)

        # action
        time.sleep(1)
        result = ws.get_state()
        print("result : ", result)

        # expectations
        #assert(isinstance(result, pd.DataFrame))

        # cleaning
        ws.stop()
