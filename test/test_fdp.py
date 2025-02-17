import pytest
import pandas as pd

from src import fdp

class TestFDP:

    def test_fdp_bitget(self):
        my_fdp = fdp.FDP({"exchange_name": "bitget"})

        res = my_fdp.get_symbol_ohlcv_last("BTC")

        assert(isinstance(res, pd.DataFrame))
