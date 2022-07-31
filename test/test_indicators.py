import pandas as pd
import pytest
import numpy as np
import datetime

from src import indicators

class TestIndicators:

    def get_dataframe(self):
        dateparse = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')
        df = pd.read_csv("./test/data/google_stocks_data.csv",parse_dates=[0],index_col=0,skiprows=0,date_parser=dateparse)
        df.dropna(inplace=True) # remove incoherent values (null, NaN, ...)
        df = indicators.normalize_column_headings(df)
        return df

    def test_number_colums(self):
        df = self.get_dataframe()
        assert(len(list(df.columns)) == 6)

        # first set of technical indicators
        technical_indicators = ["macd", "macds", "macdh", "rsi_30", "cci_30", "dx_30", "williams_%r", "stoch_%k", "stoch_%d", "er"]
        df = indicators.compute_indicators(df, technical_indicators)
        assert(len(list(df.columns)) == 16)

        df = indicators.remove_features(df, technical_indicators)
        assert(len(list(df.columns)) == 6)

        # second set of technical indicators
        technical_indicators = ["trend_1d", "sma_12", "ema_9", "bbands", "stc", "atr", "adx", "roc", "wma_5", "mom", "simple_rtn"]
        df = indicators.compute_indicators(df, technical_indicators)
        assert(len(list(df.columns)) == 19)

        technical_indicators.remove("bbands")
        technical_indicators.extend(["bb_upper", "bb_middle", "bb_lower"])
        df = indicators.remove_features(df, technical_indicators)
        assert(len(list(df.columns)) == 6)

        df = indicators.remove_features(df, ["open", "high"])
        assert(len(list(df.columns)) == 4)

        df = indicators.remove_features(df, ["fakecolumn", "low"])
        assert(len(list(df.columns)) == 3)

    def test_get_trend_close(self):
        data = {'close':[20, 21, 23, 19, 18, 24, 25, 26, 16, -10, -15, -18, -15, -8]}
        df = pd.DataFrame(data)
        df = indicators.compute_indicators(df, ["trend_1d","trend_4d"])
        trend1 = df.loc[:,'trend_1d'].values
        equal = np.array_equal(trend1, [0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1])
        assert(equal)
        trend4 = df.loc[:,'trend_4d'].values
        equal = np.array_equal(trend4, [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1])
        assert(equal)

    def test_get_trend_ratio(self):
        data = {'close':[20, 21, 23, 19, 18, 24, 25, 26, 27, 28]}
        df = pd.DataFrame(data)
        trend_ratio, true_positive, true_negative, false_positive, false_negative = indicators.get_trend_info(df)
        assert(trend_ratio == pytest.approx(66.666, 0.001))
        assert(true_positive == pytest.approx(55.555, 0.001))
        assert(true_negative == pytest.approx(11.111, 0.001))
        assert(false_positive == pytest.approx(11.111, 0.001))
        assert(false_negative == pytest.approx(22.222, 0.001))

    def test_get_stats_for_trend_up(self):
        data = {'close':[20, 21, 23, 19, 18, 24, 25, 26, 27, 28]}
        df = pd.DataFrame(data)
        trend_ratio = indicators.get_stats_for_trend_up(df, 1)
        assert(trend_ratio == 70.)

    def test_get_stats_on_trend_today_equals_trend_tomorrow(self):
        data = {'close':[20, 21, 23, 19, 18, 24, 25, 26, 27, 28]}
        df = pd.DataFrame(data)
        true_positive, true_negative, false_positive, false_negative = indicators.get_stats_on_trend_today_equals_trend_tomorrow(df)
        assert(true_positive == pytest.approx(55.5555, 0.001))
        assert(true_negative == pytest.approx(11.111, 0.001))
        assert(false_positive == pytest.approx(11.111, 0.001))
        assert(false_negative == pytest.approx(22.222, 0.001))
