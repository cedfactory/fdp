
import pandas as pd
import pytest

from src import synthetic_data

class TestSyntheticData:

    def test_build_synthetic_data(self):
        # context
        df = pd.DataFrame({"date":pd.date_range("2019-10-16", periods=5)})

        # action
        df = synthetic_data.build_synthetic_data(df)

        # expectations
        assert(isinstance(df,pd.DataFrame))

        # check the columns names
        columns = df.columns.tolist()
        assert(any(column in ['time', 'sinus_1', 'sinus_2', 'linear_up', 'linear_down', 'sinus_3', 'sinus_4', 'sinus_5'] for column in columns))

    def test_get_synthetic_data(self):
        # context
        df = pd.DataFrame({"date":pd.date_range("2019-10-16", periods=50)})

        # action
        df = synthetic_data.get_synthetic_data(df, "close_synthetic_SINGLE_SINUS_2_FLAT", None)
        assert(isinstance(df, pd.DataFrame))
        columns = df.columns.tolist()

        # check the columns names
        columns = df.columns.tolist()
        assert(any(column in ["date", "close_synthetic_SINGLE_SINUS_2_FLAT"] for column in columns))
        assert(df["close_synthetic_SINGLE_SINUS_2_FLAT"][0] == 10)
        assert(df["close_synthetic_SINGLE_SINUS_2_FLAT"][1] == pytest.approx(10.125333))
