import pandas as pd
import numpy as np

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

def build_synthetic_data(df, start_date, end_date, interval):
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

def get_synthetic_data(df, data_type, start, end, interval):
    df_synthetic = build_synthetic_data(df, start, end, interval)

    if 'SINGLE_SINUS_1_FLAT' in data_type:
        df['close'] = df_synthetic['sinus_1'] + 10
    elif 'SINGLE_SINUS_2_FLAT' in data_type:
        df['close'] = df_synthetic['sinus_2'] + 10
    elif 'MIXED_SINUS_FLAT' in data_type:
        df['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + 10
    elif 'SINGLE_SINUS_1_UP' in data_type:
        df['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_up'] + 10
    elif 'SINGLE_SINUS_2_UP' in data_type:
        df['close'] = df_synthetic['sinus_2'] + df_synthetic['linear_up'] + 10
    elif 'MIXED_SINUS_UP' in data_type:
        df['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + df_synthetic['linear_up'] + 10
    elif 'SINGLE_SINUS_1_DOWN' in data_type:
        df['close'] = df_synthetic['sinus_1'] + df_synthetic['linear_down'] + 10
    elif 'SINGLE_SINUS_2_DOWN' in data_type:
        df['close'] = df_synthetic['sinus_2'] + df_synthetic['linear_down'] + 10
    elif 'MIXED_SINUS_DOWN' in data_type:
        df['close'] = df_synthetic['sinus_2'] + df_synthetic['sinus_3'] + df_synthetic['linear_down'] + 10
    elif 'MIXED_SINUS_UP_DOWN' in data_type:
        df['close'] = df_synthetic['sinus_3'] + df_synthetic['sinus_4'] + 10
    elif 'MIXED_SINUS_DOWN_UP' in data_type:
        df['close'] = df_synthetic['sinus_3'] + df_synthetic['sinus_5'] + 10

    df_ohlv = pd.DataFrame(columns=['timestamp', 'close'])
    df_ohlv['timestamp'] = df_synthetic['timestamp']
    df_ohlv['close'] = df['close']
    df = fill_ohl(df_ohlv)

    if 'NOISE' in data_type:
        df = add_df_ohlv_noise(df, config_param.noise_amplitude)

    return df