import pandas as pd
import pytest
import numpy as np
import datetime
import os

from src import indicators

g_generate_references = False

class TestIndicators:

    def get_dataframe_from_csv(self, cvsfilename):
        dateparse = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')
        df = pd.read_csv(cvsfilename,parse_dates=[0],index_col=0,skiprows=0,date_parser=dateparse)
        df.dropna(inplace=True) # remove incoherent values (null, NaN, ...)
        df = indicators.normalize_column_headings(df)
        return df

    def test_number_colums(self):
        df = self.get_dataframe_from_csv("./test/data/google_stocks_data.csv")
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

    def test_super_trend_direction(self):
        df = self.get_dataframe_from_csv("./test/data/google_stocks_data.csv")
        df = df.head(200)
        df = indicators.compute_indicators(df, ['super_trend_direction'])
        df = indicators.remove_missing_values(df)
        df = indicators.normalize_column_headings(df)

        df.to_csv("./test/generated/findicators_super_trend_direction_generated.csv")
        expected_df = self.get_dataframe_from_csv("./test/references/findicators_super_trend_direction_reference.csv")
 
        array = df["super_trend_direction"].to_numpy()
        array_expected = expected_df["super_trend_direction"].to_numpy()
        assert((array==array_expected).all())

    def test_vsa(self):
        df = self.get_dataframe_from_csv("./test/data/google_stocks_data.csv")
        df = df.head(200)
        df = indicators.compute_indicators(df, ['vsa'])
        df = indicators.remove_missing_values(df)
        df = indicators.normalize_column_headings(df)

        df.to_csv("./test/generated/findicators_vsa_generated.csv")
        expected_df = self.get_dataframe_from_csv("./test/references/findicators_vsa_reference.csv")
 
        for column in ["vsa_volume_1d","vsa_price_spread_1d","vsa_close_loc_1d","vsa_close_change_1d","vsa_volume_2d","vsa_price_spread_2d","vsa_close_loc_2d","vsa_close_change_2d","vsa_volume_3d","vsa_price_spread_3d","vsa_close_loc_3d","vsa_close_change_3d","vsa_volume_5d","vsa_price_spread_5d","vsa_close_loc_5d","vsa_close_change_5d","vsa_volume_20d","vsa_price_spread_20d","vsa_close_loc_20d","vsa_close_change_20d","vsa_volume_40d","vsa_price_spread_40d","vsa_close_loc_40d","vsa_close_change_40d","vsa_volume_60d","vsa_price_spread_60d","vsa_close_loc_60d","vsa_close_change_60d","outcomes_vsa"]:
            array = df[column].to_numpy()
            array_expected = expected_df[column].to_numpy()
            assert(np.allclose(array, array_expected))

    def labeling_common(self, dict_params, ref_csvfile, ref_barriers_csvfile):
        df = self.get_dataframe_from_csv("./test/data/google_stocks_data.csv")
        df = df.head(150)
        df_labeling = indicators.compute_indicators(df, ['labeling'], False, dict_params)
        df_labeling = indicators.remove_features(df_labeling, ['high', 'low', 'open', 'volume', 'adj_close'])
        df_labeling = indicators.remove_missing_values(df_labeling)

        # final result
        if g_generate_references:
            df_labeling.to_csv(ref_csvfile)
        expected_df_labeling = self.get_dataframe_from_csv(ref_csvfile)

        for column in df_labeling.columns:
            array_expected = expected_df_labeling[column].to_numpy()
            if array_expected.dtype != object:
                array = df_labeling[column].to_numpy(dtype = array_expected.dtype)
                assert(np.allclose(array, array_expected))

        # barriers for debug
        gen_file = "./test/generated/labeling_barriers.csv"
        if g_generate_references:
            os.rename(gen_file, ref_barriers_csvfile)
        ref_df_barriers = self.get_dataframe_from_csv(ref_barriers_csvfile)
        gen_df_barriers = self.get_dataframe_from_csv(gen_file)

        for column in gen_df_barriers.columns:
            ref_array = ref_df_barriers[column].to_numpy()
            if ref_array.dtype != object:
                gen_array = gen_df_barriers[column].to_numpy(dtype = ref_array.dtype)
                assert(np.allclose(gen_array, ref_array))

    def test_labeling_close_unbalanced(self):
        dict_params = {'labeling_debug':True, 'labeling_t_final':10, 'labeling_upper_multiplier':"2.", 'labeling_lower_multiplier':"2."}
        ref_csvfile = "./test/references/findicators_data_labeling_reference.csv"
        ref_barriers_csvfile = "./test/references/findicators_data_labeling_barriers_reference.csv"
        self.labeling_common(dict_params, ref_csvfile, ref_barriers_csvfile)

    def test_labeling_high_low_unbalanced(self):
        dict_params = {'labeling_debug':True, 'use_high_low':'1', 'labeling_t_final':10, 'labeling_upper_multiplier':"2.", 'labeling_lower_multiplier':"2."}
        ref_csvfile = "./test/references/findicators_data_labeling_high_low_reference.csv"
        ref_barriers_csvfile = "./test/references/findicators_data_labeling_high_low_barriers_reference.csv"
        self.labeling_common(dict_params, ref_csvfile, ref_barriers_csvfile)

    def test_labeling_close_balanced(self):
        dict_params = {'labeling_debug':True, "use_balanced_upper_multiplier":1, 'labeling_t_final':10, 'labeling_upper_multiplier':"2.", 'labeling_lower_multiplier':"2.",  "labeling_label_below":"0", "labeling_label_middle":"0", "labeling_label_above":"1"}
        ref_csvfile = "./test/references/findicators_data_labeling_close_balanced_reference.csv"
        ref_barriers_csvfile = "./test/references/findicators_data_labeling_close_balanced_barriers_reference.csv"
        self.labeling_common(dict_params, ref_csvfile, ref_barriers_csvfile)

    def test_labeling_high_low_balanced(self):
        dict_params = {'labeling_debug':True, 'use_high_low':'1', "use_balanced_upper_multiplier":1, 'labeling_t_final':10, 'labeling_upper_multiplier':"2.", 'labeling_lower_multiplier':"2.",  "labeling_label_below":"0", "labeling_label_middle":"0", "labeling_label_above":"1"}
        ref_csvfile = "./test/references/findicators_data_labeling_high_low_balanced_reference.csv"
        ref_barriers_csvfile = "./test/references/findicators_data_labeling_high_low_balanced_barriers_reference.csv"
        self.labeling_common(dict_params, ref_csvfile, ref_barriers_csvfile)

    def test_shift(self):
        data = {'close':[20., 21., 23., 19., 18., 24., 25., 26., 16.]}
        df = pd.DataFrame(data)

        df = indicators.shift(df, "close", 2)

        array = df.loc[:,'close'].values
        assert(np.array_equal(array, [np.NaN, np.NaN, 20., 21., 23., 19., 18., 24., 25.], equal_nan=True))

    def test_temporal_indicators(self):
        idx = pd.Index(pd.date_range("19991231", periods=10), name='Date')
        df = pd.DataFrame([1]*10, columns=["Foobar"], index=idx)
        df = indicators.add_temporal_indicators(df, "Date")
        df = indicators.normalize_column_headings(df)

        expected_df = self.get_dataframe_from_csv("./test/references/findicators_temporal_indicators_reference.csv")
        assert(df.equals(expected_df))