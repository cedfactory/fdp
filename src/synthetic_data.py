import pandas as pd
import numpy as np
from . import indicators as inc_indicators
from . import utils
from . import config
from datetime import datetime, timedelta
import datetime

import math

class config_param:
    noise_amplitude = 0.1
    a = 0.1
    b = 10
    slow = 30
    fast = 1.1
    sinus_1_amplitude = 5
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
    if a < 0:
        min_val = min(y)
        if min_val < 0:
            min_val = abs(min_val) + 1
            y = y + min_val
    y = y - min(y) + 1
    df[column] = y
    return df

def fill_df_combined_linear(df, column, a, b):
    x = np.arange(len(df))
    x_half = int(len(x)/2)
    y = a*x + b
    if a < 0:
        min_val = min(y)
        if min_val < 0:
            min_val = abs(min_val) + 1
            y = y + min_val
    b_half = y[x_half]
    y = y[:x_half]
    z = -a*x + b_half
    z = z[:x_half + 1]
    y = [*y, *z]
    y = y - min(y) + 1
    if len(y) != len(df):
        y = y[:len(df)]
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

    freq = 20 * math.pi / len(df_synthetic)
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_1', config_param.sinus_1_amplitude, freq, 0, config_param.sinus_1_height)

    freq = 2 * math.pi / len(df_synthetic)
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_2', config_param.sinus_2_amplitude, freq, 0, config_param.sinus_2_height)

    freq = 20 * math.pi / len(df_synthetic)
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_3', config_param.sinus_3_amplitude, freq, 0, config_param.sinus_3_height)

    freq = 2 * math.pi / len(df_synthetic) / 2
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_4', config_param.sinus_4_amplitude, freq, 0, config_param.sinus_4_height)

    freq = 4 * math.pi / len(df_synthetic)
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_6', config_param.sinus_2_amplitude, freq, 0, config_param.sinus_2_height)

    freq = 2 * math.pi / len(df_synthetic) / 2
    df_synthetic = fill_df_sinusoid(df_synthetic, 'sinus_5', config_param.sinus_5_amplitude, freq, 0, config_param.sinus_5_height)
    df_synthetic['sinus_5'] = 1 - df_synthetic['sinus_5']

    df_synthetic = fill_df_linear(df_synthetic, 'linear_up', config_param.a, config_param.b)
    df_synthetic = fill_df_linear(df_synthetic, 'linear_down', -config_param.a, config_param.b)

    df_synthetic = fill_df_linear(df_synthetic, 'linear_up_slow', config_param.a / config_param.slow, config_param.b)
    df_synthetic = fill_df_linear(df_synthetic, 'linear_down_slow', -config_param.a / config_param.slow, config_param.b)

    df_synthetic = fill_df_linear(df_synthetic, 'linear_up_fast', config_param.a * config_param.fast, config_param.b)
    df_synthetic = fill_df_linear(df_synthetic, 'linear_down_fast', -config_param.a * config_param.fast, config_param.b)

    df_synthetic = fill_df_combined_linear(df_synthetic, 'linear_down_up', -config_param.a, config_param.b)
    df_synthetic = fill_df_combined_linear(df_synthetic, 'linear_up_down', config_param.a, config_param.b)


    return df_synthetic

def get_synthetic_data(exchange_name, data_type, start, end, interval, indicators):
    # request a start earlier according to what the indicators need
    start_with_period = start
    max_period = utils.max_from_dict_values(indicators)
    if max_period != 0:
        if interval == "1d":
            start_with_period = start_with_period + datetime.timedelta(days=-max_period)
        elif interval == "1h":
            start_with_period = start_with_period + datetime.timedelta(hours=-max_period)
        elif interval == "1m":
            start_with_period = start_with_period + datetime.timedelta(minutes=-max_period)

    df_synthetic = build_synthetic_data(start_with_period, end, interval)

    df_ohlv = pd.DataFrame(columns=['timestamp', 'close'])
    df_ohlv['timestamp'] = df_synthetic['timestamp']

    if 'SYNTHETICSINGLESINUS1FLAT' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
    elif 'SYNTHETICSINGLESINUS2FLAT' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + 10
    elif 'SYNTHETICSINGLESINUS6FLAT' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_6'] + 10
    elif 'SYNTHETICMIXEDSINUSFLAT' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + 10
    elif 'SYNTHETICSINGLESINUS1UP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_up'] + 10
    elif 'SYNTHETICSINGLESINUS2UP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['linear_up'] + 10
    elif 'SYNTHETICMIXEDSINUSUP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + df_synthetic['linear_up'] + 10
    elif 'SYNTHETICSINGLESINUS1DOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_down'] + 10
    elif 'SYNTHETICSINGLESINUS2DOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['linear_down'] + 10
    elif 'SYNTHETICMIXEDSINUSDOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + df_synthetic['linear_down'] + 10
    elif 'SYNTHETICMIXEDSINUSUPDOWN' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_3'] + df_synthetic['sinus_4'] + 10
    elif 'SYNTHETICMIXEDSINUSDOWNUP' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_3'] + df_synthetic['sinus_5'] + 10
    elif 'SYNTHETICSINGLELINEARUP' in data_type:
        df_ohlv['close'] = df_synthetic['linear_up'] + 10
    elif 'SYNTHETICSINGLELINEARDOWN' in data_type:
        df_ohlv['close'] = df_synthetic['linear_up'] + 10
    elif 'SYNTHETICMIXEDLINEARUPDOWN' in data_type:
        df_ohlv['close'] = df_synthetic['linear_up_down'] + 10
    elif 'SYNTHETICMIXEDLINEARDOWNUP' in data_type:
        df_ohlv['close'] = df_synthetic['linear_down_up'] + 10
    # GRID TRADING STRATEGY SCENARIOS
    elif 'SYNTHETICGRIDTRADING1' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
    elif 'SYNTHETICGRIDTRADING2' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_up_slow'] + 10
    elif 'SYNTHETICGRIDTRADING3' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_down_slow'] + 10
    elif 'SYNTHETICGRIDTRADING4' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + df_synthetic['sinus_6'] + 10
    elif 'SYNTHETICGRIDTRADING5' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
        z = 601
        x = df_ohlv['close'].values[z]
        y = df_synthetic['linear_down'].values[z]
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_down'] +x -y, df_ohlv['close'])
        df_ohlv['close'] = np.where(df_ohlv['close'] <= 0.5, 0.5, df_ohlv['close'])
    elif 'SYNTHETICGRIDTRADING6' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
        z = 640
        x = df_ohlv['close'].values[z]
        y = df_synthetic['linear_up'].values[z]
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_up'] +x -y, df_ohlv['close'])
    elif 'SYNTHETICGRIDTRADING7' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
        z = 213
        x = df_ohlv['close'].values[z]
        y = df_synthetic['linear_down'].values[z]
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_down'] +x -y, df_ohlv['close'])
        df_ohlv['close'] = np.where(df_ohlv['close'] <= 0.5, 0.5, df_ohlv['close'])
        z = 259 + 65 # + (369 - 259)
        y = df_synthetic['linear_up'].values[z]
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_up'] + 0.5 -y, df_ohlv['close'])
        z = 369
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['sinus_1'] + 10, df_ohlv['close'])
    elif 'SYNTHETICGRIDTRADING8' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
        z = 250
        x = df_ohlv['close'].values[z]
        y = df_synthetic['linear_up'].values[z]
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_up'] + x - y, df_ohlv['close'])
        df_ohlv['close'] = np.where(df_ohlv['close'] >= 25, 25, df_ohlv['close'])
        z = 400 + (541 - 500) + 20
        w = df_synthetic['linear_down'].values[z] - 25
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_down'] - w, df_ohlv['close'])
        z = 541 + 20
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['sinus_1'] + 10, df_ohlv['close'])
    elif 'SYNTHETICGRIDTRADING9' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
        z = 291
        x = df_ohlv['close'].values[z]
        y = df_synthetic['linear_down_fast'].values[z]
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_down_fast'] + x - y, df_ohlv['close'])
        df_ohlv['close'] = np.where(df_ohlv['close'] <= 0.5, 0.5, df_ohlv['close'])
        z1 = 332
        w = df_synthetic['linear_up_fast'].values[z1]
        df_ohlv['close'] = np.where(df_ohlv.index >= z1, df_synthetic['linear_up_fast'] - w + 0.5, df_ohlv['close'])
        z2 = 373
        df_ohlv['close'] = np.where(df_ohlv.index >= z2, df_synthetic['sinus_1'] + 10, df_ohlv['close'])
        z3 = 485
        x3 = df_ohlv['close'].values[z3]
        w3 = df_synthetic['linear_up_fast'].values[z3]
        df_ohlv['close'] = np.where(df_ohlv.index >= z3, df_synthetic['linear_up_fast'] + x3 - w3, df_ohlv['close'])
        z4 = z3 + z1 - z
        x4 = df_ohlv['close'].values[z4]
        w4 = df_synthetic['linear_down_fast'].values[z4]
        df_ohlv['close'] = np.where(df_ohlv.index >= z4, df_synthetic['linear_down_fast'] + x4 - w4, df_ohlv['close'])
        z5 = 567
        df_ohlv['close'] = np.where(df_ohlv.index >= z5, df_synthetic['sinus_1'] + 10, df_ohlv['close'])
        df_ohlv['close'] = np.where(df_ohlv['close'] <= 2.5, 2.5, df_ohlv['close'])
        df_ohlv['close'] = np.where(df_ohlv['close'] >= 17, 17, df_ohlv['close'])
    elif 'SYNTHETICGRIDTRADING10' in data_type:
        df_ohlv['close'] = df_synthetic['sinus_1'] + 10
        z = 617
        x = df_ohlv['close'].values[z]
        y = df_synthetic['linear_up'].values[z]
        df_ohlv['close'] = np.where(df_ohlv.index >= z, df_synthetic['linear_up'] + x - y, df_ohlv['close'])

    # END OF SCENARIOS
    df_ohlv = fill_ohl(df_ohlv)

    df_ohlv.drop(0, inplace=True)
    df_ohlv.reset_index(inplace=True, drop=True)

    if config.noise:
        df_ohlv = add_df_ohlv_noise(df_ohlv, config_param.noise_amplitude)

    # remove dupicates
    df_ohlv = df_ohlv[~df_ohlv.index.duplicated()]

    df_ohlv.set_index('timestamp', inplace=True)

    if len(indicators) != 0:
        indicator_params = {"symbol": data_type, "exchange": exchange_name}
        df_ohlv = inc_indicators.compute_indicators(df_ohlv, indicators, True, indicator_params)

    if max_period != 0:
        df_ohlv = df_ohlv.iloc[max_period - 1:]

    return df_ohlv