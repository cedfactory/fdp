import pytest
import time
import pandas as pd
from src import bitget_ws_candle

class TestBitgetWS:

    def test_bitget_ws_ticker(self):
        # context
        params = {"id": "ws1"}
        ws = bitget_ws_candle.WSCandle(params)
        time.sleep(1)

        # action
        result = ws.request("last", params)
        print(result)

        # expectations
        assert(isinstance(result, pd.DataFrame))

        # cleaning
        ws.stop()
