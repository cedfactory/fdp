import pandas as pd
from parse import parse
from stockstats import StockDataFrame as Sdf
from finta import TA
import ta
import numpy as np
from . import indicators_vsa as vsa
from . import indicators_flabeling as flabeling
from . import indicators_supertrend as supertrend
from . import indicators_tradingview as tv
from . import utils

def get_window_size(indicator):
    trend_parsed = parse('trend_{}d', indicator)
    sma_parsed = parse('sma_{}', indicator)
    ema_parsed = parse('ema_{}', indicator)
    wma_parsed = parse('wma_{}', indicator)

    if indicator in ["open", "close", "high", "low"]:
        return 0

    elif trend_parsed != None and trend_parsed[0].isdigit():
        return int(trend_parsed[0])

    elif sma_parsed != None and sma_parsed[0].isdigit():
        return int(sma_parsed[0])

    elif ema_parsed != None and ema_parsed[0].isdigit():
        return int(ema_parsed[0])

    elif wma_parsed != None and wma_parsed[0].isdigit():
        return int(wma_parsed[0])

    elif indicator in ['macd', 'macds', 'macdh']:
        return 26

    elif indicator == "bbands":
        return 20

    elif indicator in ["rsi_30", "cci_30", "dx_30"]:
        return 30
    
    elif indicator == 'williams_%r':
        return 14

    elif indicator in ['stoch_%k', 'stoch_%d']:
        return 14
        
    elif indicator == 'er':
        return 10
        
    elif indicator == 'stc':
        return 50
        
    elif indicator == 'atr':
        return 14
        
    elif indicator == 'adx':
        return 14
        
    elif indicator == 'roc':
        return 12

    elif indicator == 'mom':
        return 10

    elif indicator == 'simple_rtn':
        return 1

    elif indicator == 'labeling':
        return 20

    elif indicator.startswith('tv_'):
        return 0

    elif indicator.startswith('close_synthetic_'):
        return 0

    elif indicator == 'vsa':
        return 60

    elif indicator == "super_trend_direction":
        return 15

    print("unknown window size for ", indicator)
    return 0

def get_max_window_size(indicators):
    if len(indicators) == 0:
        return 0
    list_indicators = indicators
    if isinstance(list_indicators, dict):
        list_indicators = list_indicators.keys()

    return max([get_window_size(indicator) for indicator in indicators])

def compute_indicators(df, indicators, keep_only_requested_indicators = False, params = None):
    if not isinstance(df, pd.DataFrame):
        return df

    # manage indicators as an array but it is converted into a dictionary
    if isinstance(indicators, list):
        indicators = dict.fromkeys(indicators)

    # call stockstats
    stock = Sdf.retype(df.copy())

    # compute the indicators
    columns = list(df.columns)
    for indicator, parameters in indicators.items():
        if indicator in columns:
            continue

        trend_parsed = parse('trend_{}d', indicator)
        sma_parsed = parse('sma_{}', indicator)
        ema_parsed = parse('ema_{}', indicator)
        wma_parsed = parse('wma_{}', indicator)
        slope_parsed = parse('slope_{}', indicator)

        if trend_parsed != None and trend_parsed[0].isdigit():
            seq = int(trend_parsed[0])
            diff = df["close"] - df["close"].shift(seq)
            df["trend_"+str(seq)+"d"] = diff.gt(0).map({False: 0, True: 1})

        elif sma_parsed != None and sma_parsed[0].isdigit():
            seq = int(sma_parsed[0])
            df["sma_"+str(seq)] = TA.SMA(stock, seq).copy()

        elif ema_parsed != None and ema_parsed[0].isdigit():
            period = int(ema_parsed[0])
            df["ema_"+str(period)] = TA.EMA(stock, period = period).copy()

        elif wma_parsed != None and wma_parsed[0].isdigit():
            period = int(wma_parsed[0])
            df["wma_"+str(period)] = TA.WMA(stock, period = period).copy()

        elif slope_parsed != None and slope_parsed[0].isdigit():
            period = int(slope_parsed[0])
            df["slope_"+str(period)] = df["close"].rolling(window=period).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])

        elif indicator == 'macd':
            df['macd'] = stock.get('macd').copy() # from stockstats
            #df['macd'] = TA.MACD(stock)['MACD'].copy() # from finta

        elif indicator == 'macds':
            df['macds'] = stock.get('macds').copy() # from stockstats

        elif indicator == 'macdh':
            df['macdh'] = stock.get('macdh').copy() # from stockstats

        elif indicator == 'bbands':
            bbands = TA.BBANDS(stock).copy()
            df = pd.concat([df, bbands], axis = 1)
            df.rename(columns={'BB_UPPER': 'bb_upper'}, inplace=True)
            df.rename(columns={'BB_MIDDLE': 'bb_middle'}, inplace=True)
            df.rename(columns={'BB_LOWER': 'bb_lower'}, inplace=True)

        elif indicator == 'bollinger':
            bol_window = 100
            bol_std = 2.25
            long_ma_window = 500

            bol_band = ta.volatility.BollingerBands(close=df["close"], window=bol_window, window_dev=bol_std)
            df["lower_band"] = bol_band.bollinger_lband()
            df["higher_band"] = bol_band.bollinger_hband()
            df["ma_band"] = bol_band.bollinger_mavg()
            df['long_ma'] = ta.trend.sma_indicator(close=df['close'], window=long_ma_window)

            df = utils.get_n_columns(df, ["ma_band", "lower_band", "higher_band", "close"], 1)

            df['bollinger'] = True # bollinger indicator trigger

        elif indicator == 'synthetic_bollinger':
            df.reset_index(inplace=True)
            # TEST SCENARIO
            df['close'] = 10
            df["lower_band"] = 9
            df["higher_band"] = 11
            df["ma_band"] = 9.5
            df["long_ma"] = 7

            t = 1000 + 50
            t_plus = 25
            df.at[t, "close"] = df["higher_band"].iloc[t] + 0.01
            # OPEN LONG
            df['close'] = np.where(df.index >= t, df["higher_band"] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["higher_band"] + 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["higher_band"] + 1.5, df['close'])
            # CLOSE LONG
            t = t + t_plus
            df['ma_band'] = np.where(df.index >= t, df["close"] + 1, df['ma_band'])

            # OPEN SHORT
            t = t + t_plus
            df['lower_band'] = np.where(df.index >= t, df["close"] + 0.6, df['lower_band'])
            df['long_ma'] = np.where(df.index >= t, df["close"] + 0.3, df['long_ma'])

            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1.5, df['close'])
            t = t + t_plus
            # CLOSE SHORT
            df['ma_band'] = np.where(df.index >= t, df["close"] - 2.5, df['ma_band'])

            # OPEN LONG
            t = t + t_plus
            df['long_ma'] = np.where(df.index >= t, df["close"] - 0.3, df['long_ma'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["higher_band"] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1.5, df['close'])
            # CLOSE LONG
            t = t + t_plus
            df['ma_band'] = np.where(df.index >= t, df["close"] + 2, df['ma_band'])

            t = t + t_plus
            df['higher_band'] = np.where(df.index >= t, df["higher_band"] + 4, df['higher_band'])

            # OPEN SHORT
            t = t + t_plus
            df['lower_band'] = np.where(df.index >= t, df["close"] - 1, df['lower_band'])
            t = t + t_plus
            df['lower_band'] = np.where(df.index >= t, df["close"] + 1, df['lower_band'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1.5, df['close'])
            # CLOSE SHORT BY MA_BAND ALREADY BELOW CLOSE

            # OPEN LONG
            t = t + t_plus
            df['higher_band'] = np.where(df.index >= t, df["higher_band"] - 4, df['higher_band'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1.5, df['close'])

            # CLOSE LONG
            t = t + t_plus
            df['ma_band'] = np.where(df.index >= t, df["close"] + 0.5, df['ma_band'])

            # END OF SCENARIO
            df.set_index(['timestamp'], inplace=True, drop=True)
            df = utils.get_n_columns(df, ["ma_band", "lower_band", "higher_band", "close"], 1)

            df['syntheticbollinger'] = True  # bollinger indicator trigger

        elif indicator == 'rsi_30':
            df['rsi_30'] = stock.get('rsi_30').copy()
        
        elif indicator == 'cci_30':
            df['cci_30'] = stock.get('cci_30').copy()
        
        elif indicator == 'dx_30':
            df['dx_30'] = stock.get('dx_30').copy()
        
        elif indicator == 'williams_%r':
            df['williams_%r'] = TA.WILLIAMS(stock).copy()

        elif indicator == 'stoch_%k':
            df['stoch_%k'] = TA.STOCH(stock).copy()

        elif indicator == 'stoch_%d':
            df['stoch_%d'] = TA.STOCHD(stock).copy()
           
        elif indicator == 'er':
            df['er'] = TA.ER(stock).copy()
           
        elif indicator == 'stc':
            df['stc'] = TA.STC(stock).copy()
           
        elif indicator == 'atr':
            df['atr'] = TA.ATR(stock).copy()
           
        elif indicator == 'adx':
            df['adx'] = TA.ADX(stock).copy()
           
        elif indicator == 'roc':
            df['roc'] = TA.ROC(stock).copy()

        elif indicator == 'mom':
            df['mom'] = TA.MOM(stock).copy()

        elif indicator == 'simple_rtn':
            df['simple_rtn'] = df['close'].pct_change()

        elif indicator == 'labeling':
            df = flabeling.data_labeling(df, params)

        elif indicator.startswith('tv_'):
            df[indicator] = tv.get_recommendation(df, indicator, params)

        # shift feature: column_shift_nb ex: close_shift_5
        elif '_shift_' in indicator:
            lst_split = indicator.split("_")
            df[indicator] = df[lst_split[0]].shift(int(lst_split[2]), axis=0)

        elif indicator == 'vsa':
            days = [1, 2, 3, 5, 20, 40, 60]
            df = vsa.create_bunch_of_vsa_features(df, days)
            df['outcomes_vsa'] = df.close.pct_change(-1)

        elif indicator == "super_trend_direction":
            st = supertrend.SuperTrend(
                    df['high'], 
                    df['low'], 
                    df['close'], 
                    15, # self.st_short_atr_window
                    5 # self.st_short_atr_multiplier
                )
                
            df['super_trend_direction'] = st.super_trend_direction()
            #df['super_trend_direction'] = df['super_trend_direction'].shift(1)

        elif indicator == "super_reversal":
            short_ema_window = 5
            long_ema_window = 15
            # -- Populate indicators --
            super_trend = supertrend.SuperTrend(
                df['high'],
                df['low'],
                df['close'],
                long_ema_window,
                short_ema_window
            )
            df['super_trend_direction'] = super_trend.super_trend_direction()
            df['ema_short'] = ta.trend.ema_indicator(close=df['close'], window=short_ema_window)
            df['ema_long'] = ta.trend.ema_indicator(close=df['close'], window=long_ema_window)

            df = utils.get_n_columns(df, ["super_trend_direction", "ema_short", "ema_long"], 1)
            df['superreversal'] = True  # super_reversal indicator trigger
            df['super_reversal'] = True  # super_reversal indicator trigger

        elif indicator == 'syntheticsuperreversal':
            df.reset_index(inplace=True)
            # TEST SCENARIO
            df['close'] = 5
            df["high"] = 10
            df["low"] = 17
            df["n1_ema_short"] = 14
            df["n1_ema_long"] = 15
            df["n1_super_trend_direction"] = False

            # OPEN LONG AT t
            t = 100 + 400
            df['n1_ema_short'] = np.where(df.index >= t, df["n1_ema_long"] + 1, df['n1_ema_short'])
            df['n1_super_trend_direction'] = np.where(df.index >= t, True, df['n1_super_trend_direction'])
            df['low'] = np.where(df.index >= t, df["n1_ema_short"] - 1, df['low'])

            df['close'] = np.where(df.index >= t + 10, df["close"] + 1, df['close'])

            # CLOSING SHORT
            t = t + 100
            df['n1_ema_short'] = np.where(df.index >= t, df["n1_ema_long"] - 1, df['n1_ema_short'])
            df['n1_super_trend_direction'] = np.where(df.index >= t, False, df['n1_super_trend_direction'])
            df['high'] = np.where(df.index >= t, df["n1_ema_short"] + 5, df['high'])

            # CLOSING SHORT
            t = t + 100
            df['n1_ema_short'] = np.where(df.index >= t, 20, df['n1_ema_short'])
            df['n1_ema_long'] = np.where(df.index >= t, df['n1_ema_short'] -1, df['n1_ema_long'])
            df['n1_super_trend_direction'] = np.where(df.index >= t, True, df['n1_super_trend_direction'])
            df['low'] = np.where(df.index >= t,  df['n1_ema_short'] -1, df['low'])

            # OPENING SHORT
            t = t + 100
            df['n1_ema_short'] = np.where(df.index >= t, 25, df['n1_ema_short'])
            df['n1_ema_long'] = np.where(df.index >= t, df['n1_ema_short'] +1, df['n1_ema_long'])
            df['n1_super_trend_direction'] = np.where(df.index >= t, False, df['n1_super_trend_direction'])
            df['high'] = np.where(df.index >= t,  df['n1_ema_short'] +2, df['high'])

            df['close'] = np.where(df.index >= t + 10, df["close"] - 1, df['close'])

            # CLOSING SHORT
            t = t + 100
            df['n1_ema_short'] = np.where(df.index >= t, 30, df['n1_ema_short'])
            df['n1_ema_long'] = np.where(df.index >= t, df['n1_ema_short'] -1, df['n1_ema_long'])
            df['n1_super_trend_direction'] = np.where(df.index >= t, True, df['n1_super_trend_direction'])
            df['low'] = np.where(df.index >= t,  df['n1_ema_short'] -1, df['low'])

            df["ema_short"] = df["n1_ema_short"]
            df["ema_long"] =  df["n1_ema_long"]
            df["super_trend_direction"] =  df["n1_super_trend_direction"]

            df['syntheticsuperreversal'] = True

            df.set_index(['timestamp'], inplace=True, drop=True)

    # keep only the requested indicators
    if keep_only_requested_indicators:
        for column in list(df.columns):
            if column not in indicators:
                df.drop(columns=[column], inplace=True)

    return df
    
def make_date(df, date_field):
    "Make sure `df[date_field]` is of the right date type."
    field_dtype = df[date_field].dtype
    if isinstance(field_dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
        field_dtype = np.datetime64
    if not np.issubdtype(field_dtype, np.datetime64):
        df[date_field] = pd.to_datetime(df[date_field], infer_datetime_format=True)

def add_temporal_indicators(df, field_name, time=False):
    "Helper function that adds columns relevant to a date in the column `field_name` of `df`."

    # Change all column headings to be lower case, and remove spacing
    df.columns = [str(x).lower().replace(' ', '_') for x in df.columns]

    if field_name not in df.columns and field_name != df.index.name:
        print("[add_temporal_indicators] {} is not present among the columns {} or in the index {}".format(field_name, df.columns, df.index.name))
        return df

    # if the datefield is the index of the dataframe, we create a temporary column
    field_to_drop = False
    if field_name == df.index.name:
        field_name = 'DateTmp'
        df[field_name] = df.index
        field_to_drop = True

    make_date(df, field_name)

    field = df[field_name]
    prefix = "" #ifnone(prefix, re.sub('[Dd]ate$', '', field_name))
    attr = ['Year', 'Month', 'Week', 'Day', 'Dayofweek', 'Dayofyear', 'Is_month_end', 'Is_month_start',
            'Is_quarter_end', 'Is_quarter_start', 'Is_year_end', 'Is_year_start']
    if time: attr = attr + ['Hour', 'Minute', 'Second']
    # Pandas removed `dt.week` in v1.1.10
    week = field.dt.isocalendar().week.astype(field.dt.day.dtype) if hasattr(field.dt, 'isocalendar') else field.dt.week
    for n in attr: df[prefix + n] = getattr(field.dt, n.lower()) if n != 'Week' else week
    mask = ~field.isna()
    df[prefix + 'Elapsed'] = np.where(mask, field.values.astype(np.int64) // 10 ** 9, np.nan)
    if field_to_drop: df.drop(field_name, axis=1, inplace=True)

    return df

def remove_features(df, features):
    for feature in features:
        try:
            df.drop(feature, axis=1, inplace=True)
        except KeyError as feature:
            print("{}. Columns are {}".format(feature, df.columns))
    return df

def normalize_column_headings(df):
    # Change all column headings to be lower case, and remove spacing
    df.columns = [str(x).lower().replace(' ', '_') for x in df.columns]
    return df

def get_trend_info(df):
    tmp = pd.concat([df['close']], axis=1, keys=['close'])
    tmp = compute_indicators(tmp, ["trend_1d"])
    tmp['shift_trend_1d'] = tmp['trend_1d'].shift(-1)
    tmp.dropna(inplace=True)

    tmp['true_positive'] = np.where((tmp['trend_1d'] == 1) & (tmp['shift_trend_1d'] == 1), 1, 0)
    tmp['true_negative'] = np.where((tmp['trend_1d'] == 0) & (tmp['shift_trend_1d'] == 0), 1, 0)
    tmp['false_positive'] = np.where((tmp['trend_1d'] == 1) & (tmp['shift_trend_1d'] == 0), 1, 0)
    tmp['false_negative'] = np.where((tmp['trend_1d'] == 0) & (tmp['shift_trend_1d'] == 1), 1, 0)

    # how many times the trend is up
    trend_counted = tmp['trend_1d'].value_counts(normalize=True)
    trend_ratio = 100 * trend_counted[1]

    # how many times trend today = trend tomorrow
    true_positive = 100*tmp['true_positive'].value_counts(normalize=True)[1]
    true_negative = 100*tmp['true_negative'].value_counts(normalize=True)[1]
    false_positive = 100*tmp['false_positive'].value_counts(normalize=True)[1]
    false_negative = 100*tmp['false_negative'].value_counts(normalize=True)[1]

    return trend_ratio, true_positive, true_negative, false_positive, false_negative

def get_stats_for_trend_up(df, n_forward_days):
    tmp = df.copy()

    indicator = "trend_"+str(n_forward_days)+"d"
    if indicator not in tmp.columns:
        tmp = compute_indicators(tmp, [indicator])

    # how many times the trend is up for d+n_forward_days
    trend_counted = tmp[indicator].value_counts(normalize=True)
    trend_ratio = 100 * trend_counted[1]

    return trend_ratio

def get_stats_on_trend_today_equals_trend_tomorrow(df):
    tmp = pd.concat([df['close']], axis=1, keys=['close'])
    tmp = compute_indicators(tmp, ["trend_1d"])
    tmp['shift_trend'] = tmp["trend_1d"].shift(-1)
    tmp.dropna(inplace=True)

    tmp['true_positive'] = np.where((tmp["trend_1d"] == 1) & (tmp['shift_trend'] == 1), 1, 0)
    tmp['true_negative'] = np.where((tmp["trend_1d"] == 0) & (tmp['shift_trend'] == 0), 1, 0)
    tmp['false_positive'] = np.where((tmp["trend_1d"] == 1) & (tmp['shift_trend'] == 0), 1, 0)
    tmp['false_negative'] = np.where((tmp["trend_1d"] == 0) & (tmp['shift_trend'] == 1), 1, 0)

    # how many times trend today = trend tomorrow
    true_positive = 100*tmp['true_positive'].value_counts(normalize=True)[1]
    true_negative = 100*tmp['true_negative'].value_counts(normalize=True)[1]
    false_positive = 100*tmp['false_positive'].value_counts(normalize=True)[1]
    false_negative = 100*tmp['false_negative'].value_counts(normalize=True)[1]

    return true_positive, true_negative, false_positive, false_negative

def shift(df, indicator, shift):
    if isinstance(shift, str):
        shift = int(shift)
    
    df[indicator] = df[indicator].shift(shift)
    return df

def remove_missing_values(df):
    df['inf'] = 0
    for col in df.columns:
        df['inf'] = np.where((df[col] == np.inf) | (df[col] == -np.inf), 1, df['inf'])

    df = df.drop(df[df.inf == 1].index)
    df = df.drop(['inf'], axis=1)

    df.replace([np.inf, -np.inf], np.nan)
    # Drop the NaNs
    df.dropna(axis=0, how='any', inplace=True)

    return df


def remove_duplicates(df):
    df.drop_duplicates(inplace=True)
    return df
