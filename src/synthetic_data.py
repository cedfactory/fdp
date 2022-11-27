import pandas as pd
import numpy as np
from . import indicators as inc_indicators
from datetime import datetime, timedelta
import datetime

import math

class config_param:
    noise_amplitude = 0.1
    a = 0.001
    b = 10
    sinus_1_amplitude = 1
    sinus_1_height = 0
    sinus_2_amplitude = 1
    sinus_2_height = 0
    sinus_3_amplitude = 0.3
    sinus_3_height = 0
    sinus_4_amplitude = 1
    sinus_4_height = 0
    sinus_5_amplitude = 1
    sinus_5_height = 0
    OHLV = False

def fill_df_date(df1, df2):
    df2['time'] = df1.index
    return df2

def fill_df_sinusoid(df, column, amplitude=1, frequency=.1, phi=0, height = 0):
    x = np.arange(len(df))
    y = amplitude*np.sin(frequency*x+phi)+height
    df[column] = y
    return df

def fill_df_constant(amplitude, length):
    return amplitude * np.ones(length)

def fill_df_linear(df, column, a, b):
    x = np.arange(len(df))
    y = a*x + b
    df[column] = y
    return df

def fill_ohl(df):
    df['open'] = df['close'].shift()
    df['high'] = df['close'] + 0.1
    df['low'] = df['open'] - 0.1
    return df

def add_noise(y, amplitude):
    return np.array(y+amplitude*np.random.randn(len(y)))

def add_df_ohlv_noise(df, amplitude):
    df['close'] = np.array(df['close'] + abs(amplitude * np.random.randn(len(df))))
    df['open'] = df['close'].shift()

    df['high'] = np.array(df['close'] + abs(amplitude * np.random.randn(len(df))))
    df['low'] = np.array(df['open'] - abs(amplitude * np.random.randn(len(df))))

    df['high'] = np.where(df['close'] < df['open'],
                          df['open'] + df['open'] - df['low'],
                          df['high'])
    df['low'] = np.where(df['close'] < df['open'],
                         df['close'] + df['close'] - df['high'],
                         df['low'])
    return df

def get_df_range_time(start_date, end_date, interval):
    df_datetime = pd.DataFrame({'timestamp': pd.date_range(start=start_date, end=end_date, freq=interval)})
    return df_datetime

def build_synthetic_data(start_date, end_date, interval):
    df_range_time = get_df_range_time(start_date, end_date, interval)

    df_synthetic = pd.DataFrame(columns=['timestamp', 'sinus_1', 'sinus_2', 'linear_up', 'linear_down'])
    df_synthetic['timestamp'] = df_range_time['timestamp']

    freq = 100 * math.pi / len(df_synthetic)
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_1', config_param.sinus_1_amplitude, freq, 0, config_param.sinus_1_height)

    freq = 2 * math.pi / len(df_synthetic)
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_2', config_param.sinus_2_amplitude, freq, 0, config_param.sinus_2_height)

    freq = 100 * math.pi / len(df_synthetic)
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_3', config_param.sinus_3_amplitude, freq, 0, config_param.sinus_3_height)

    freq = 2 * math.pi / len(df_synthetic) / 2
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_4', config_param.sinus_4_amplitude, freq, 0, config_param.sinus_4_height)

    freq = 2 * math.pi / len(df_synthetic) / 2
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_5', config_param.sinus_5_amplitude, freq, 0, config_param.sinus_5_height)
    df_synthetic['sinus_5'] = 1 - df_synthetic['sinus_5']

    df_synthetic = fill_df_linear(df_synthetic, 'linear_up', config_param.a, config_param.b)

    df_synthetic = fill_df_linear(df_synthetic, 'linear_down', -config_param.a, config_param.b)
    
    return df_synthetic

def get_synthetic_data(exchange_name, data_type, start, end, interval, indicators):
    # request a start earlier according to what the indicators need
    start_with_period = start
    max_period = inc_indicators.get_max_window_size(indicators)
    if max_period != 0:
        if interval == "1d":
            start_with_period = start_with_period + datetime.timedelta(days=-max_period-1)
        elif interval == "1h":
            start_with_period = start_with_period + datetime.timedelta(hours=-max_period-1)
        elif interval == "1m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-max_period-1)

    df_synthetic = build_synthetic_data(start_with_period, end, interval)

    df_ohlv = pd.DataFrame(columns=['timestamp', 'close'])
    df_ohlv['timestamp'] = df_synthetic['timestamp']

    if 'SINGLESINUS1FLAT' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
    elif 'SINGLESINUS2FLAT' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + 10
    elif 'MIXEDSINUSFLAT' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + 10
    elif 'SINGLESINUS1UP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_up'] + 10
    elif 'SINGLESINUS2UP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['linear_up'] + 10
    elif 'MIXEDSINUSUP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + df_synthetic['linear_up'] + 10
    elif 'SINGLESINUS1DOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_down'] + 10
    elif 'SINGLESINUS2DOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['linear_down'] + 10
    elif 'MIXEDSINUSDOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + df_synthetic['linear_down'] + 10
    elif 'MIXEDSINUSUPDOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_3'] + df_synthetic['sinus_4'] + 10
    elif 'MIXEDSINUSDOWNUP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_3'] + df_synthetic['sinus_5'] + 10


    df_ohlv = fill_ohl(df_ohlv)

    df_ohlv.drop(0, inplace=True)
    df_ohlv.reset_index(inplace=True, drop=True)

    if 'NOISE' in data_type:
        df_ohlv = add_df_ohlv_noise(df_ohlv, config_param.noise_amplitude)

    # remove dupicates
    df_ohlv = df_ohlv[~df_ohlv.index.duplicated()]

    df_ohlv.set_index('timestamp', inplace=True)

    if len(indicators) != 0:
        indicator_params = {"symbol": data_type, "exchange": exchange_name}
        df_ohlv = inc_indicators.compute_indicators(df_ohlv, indicators, True, indicator_params)

    if max_period != 0:
        df_ohlv = df_ohlv.iloc[max_period:]

    return df_ohlv