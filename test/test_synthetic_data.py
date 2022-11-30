
import pandas as pd
import pytest

from src import synthetic_data,utils

class TestSyntheticData:

    def test_build_synthetic_data(self):
        # action
        df = synthetic_data.build_synthetic_data("2019-10-16", "2019-10-21", "1d")

        # expectations
        assert(isinstance(df,pd.DataFrame))
        assert(len(df.index) == 6)
        # check the columns names
        columns = df.columns.tolist()
        assert(any(column in ['time', 'sinus_1', 'sinus_2', 'linear_up', 'linear_down', 'sinus_3', 'sinus_4', 'sinus_5'] for column in columns))

    def test_get_synthetic_data(self):
        # context
        start = utils.convert_string_to_datetime("2019-10-16")
        end = utils.convert_string_to_datetime("2019-10-21")
        
        # action
        df = synthetic_data.get_synthetic_data("binance", "SINGLESINUS1FLAT", "2019-10-16", "2019-10-21", "1d", ["open", "close", "high", "low"])

        # expectations
        assert(isinstance(df, pd.DataFrame))
        columns = df.columns.tolist()
        assert(len(df.index) == 5)
        # check the columns names
        columns = df.columns.tolist()
        assert(any(column in ["close", "open", "high", "low"] for column in columns))
        assert(df["close"][0] == pytest.approx(10.866025))
        assert(df["close"][1] == pytest.approx(9.133975))

