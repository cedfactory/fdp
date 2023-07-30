
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src import synthetic_data,utils
import pytest


class TestSyntheticData:

    def test_fill_geometric_brownian_motion(self):
        # context
        df_range_time = pd.DataFrame({"timestamp": pd.date_range(start="2022/01/01", end="2022/04/01", freq="1d")})

        df_synthetic = pd.DataFrame(columns=['timestamp', 'sinus_1', 'sinus_2', 'linear_up', 'linear_down'])
        df_synthetic['timestamp'] = df_range_time['timestamp']

        # action
        df = synthetic_data.fill_geometric_brownian_motion(df_synthetic, "gbm", 5, 1000., 0., .4)

        # output
        '''
        plt.plot(df["gbm0"])
        plt.plot(df["gbm1"])
        #plt.legend(np.round(sigma, 2))
        plt.xlabel("$t$")
        plt.ylabel("$x$")
        plt.title(
            "Realizations of Geometric Brownian Motion with different variances\n $\mu=1$"
        )
        plt.show()
        '''

        # expectations
        assert (isinstance(df, pd.DataFrame))
        assert ("gbm0" in df.columns)

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
        return
        # context
        start = utils.convert_string_to_datetime("2019-10-16")
        end = utils.convert_string_to_datetime("2019-10-21")
        
        # action
        # TODO : check indicators structure
        df = synthetic_data.get_synthetic_data("bitget", "SYNTHETICSINGLESINUS1FLAT", start, end, "1d", {"id1":"open", "id2":"close", "id3":"high", "id4":"low"})

        # expectations
        assert(isinstance(df, pd.DataFrame))
        columns = df.columns.tolist()
        assert(len(df.index) == 6)
        # TODO check the columns names
        #columns = df.columns.tolist()
        #assert(any(column in ["close", "open", "high", "low"] for column in columns))
        #assert(df["close"][0] == pytest.approx(10.866025))
        #assert(df["close"][1] == pytest.approx(9.133975))

