import pytest
import pandas as pd

from src import fdp_manager

class TestFDPManager:

    def test_fdp_manager(self):
        # context
        fdps = [{"id": "fdp1", "src": "localhost:5000"}, {"id": "fdp2", "src": "FDP"}]
        params = {"fdps": fdps}

        # action
        my_fdp_manager = fdp_manager.FDPManager(params)

        # expectations
        assert(len(my_fdp_manager.sources) == 2)

    def test_fdp_manager_request(self):
        # context
        fdps_params = {"fdps": [{"id": "fdp1", "src": "localhost:5000"}, {"id": "fdp2", "src": "FDP"}]}
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
        result = my_fdp_manager.request("fdp2", "last", params)

        # expectations
        assert(isinstance(result, pd.DataFrame))
