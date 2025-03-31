import pytest
import pandas as pd
import threading
import time
from src import fdp_manager

class TestFDPManager:

    def test_fdp_manager(self):
        # context
        params = [
                {"type": "url", "url": "localhost:5000"},
                {"type": "ccxt", "exchange": "bitget"},
                {"type": "ws", "exchange": "bitget", "symbols": "BTC", "timeframe": "1h"},
                {"type": "api", "exchange": "bitget"}
            ]

        # action
        my_fdp_manager = fdp_manager.FDPManager(params)

        # expectations
        assert(len(my_fdp_manager.lstSources) == 2)

    def test_fdp_manager_request(self):
        # context
        params = [
                {"type": "ccxt", "id": "ccxt1", "exchange": "bitget"},
                {"type": "url", "id": "url1", "url": "localhost:5000"},
                {"type": "ws", "id": "ws1", "exchange": "bitget", "symbols": "BTC", "timeframe": "1h"},
                {"type": "api", "id": "api1", "exchange": "bitget"}
            ]
        my_fdp_manager = fdp_manager.FDPManager(params)

        # action
        params = {
            "exchange": "bitget",
            "symbol": "XRP",
            "interval": "1h",
            "candle_stick": "released",
            "start": None,
            "end": None
        }
        result = my_fdp_manager.request("last", params)

        # expectations
        assert(isinstance(result, pd.DataFrame))

    def test_fdp_manager_request_too_many(self):
        # context
        fdps_params = [
            {"type": "ccxt", "id": "ccxt1", "exchange": "bitget"},
            {"type": "ccxt", "id": "ccxt2", "exchange": "bitget"},
        ]
        my_fdp_manager = fdp_manager.FDPManager(fdps_params)

        # action
        params = {
            "exchange": "bitget",
            "symbol": "XRP",
            "interval": "1h",
            "candle_stick": "released",
            "start": None,
            "end": None
        }

        threads = []
        for _ in range(15):
            t = threading.Thread(target=my_fdp_manager.request, args=("last", params))
            t.daemon = True
            t.start()
            threads.append(t)

        # expectations
        print("Done")

    def test_fdp_manager_bitget_ws_ticker(self):
        # context
        params = [
                {"type": "ws_ticker", "id": "ws1", "exchange": "bitget", "symbols": "BTC", "timeframe": "1m"}
            ]
        my_fdp_manager = fdp_manager.FDPManager(params)

        # action
        params = {
            "exchange": "bitget",
            "symbol": "XRP",
            "interval": "1m",
            "candle_stick": "released",
            "start": None,
            "end": None
        }
        time.sleep(1)
        result = my_fdp_manager.request("last", params, "ws1")
        print(result)

        # expectations
        assert(isinstance(result, pd.DataFrame))

        # cleaning
        my_fdp_manager.stop()
