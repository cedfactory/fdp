import pytest
import pandas as pd

from src import fdp

class TestFDP:

    def test_fdp_bitget(self):
        params = {"type": "ccxt", "id": "ccxt1", "exchange": "bitget"}
        my_fdp = fdp.FDPCCXT(params)

        res = my_fdp.get_symbol_ohlcv_last("BTC")

        assert(isinstance(res, pd.DataFrame))
