import pandas as pd
from parse import parse
from stockstats import StockDataFrame as Sdf
from finta import TA
import ta
from collections import OrderedDict
import numpy as np
from . import indicators_vsa as vsa
from . import indicators_flabeling as flabeling
from . import indicators_supertrend as supertrend
from . import indicators_tradingview as tv
from . import utils
from . import custom_indicators

def get_window_size(indicator):
    trend_parsed = parse('trend_{}d', indicator)
    sma_parsed = parse('sma_{}', indicator)
    ema_parsed = parse('ema_{}', indicator)
    wma_parsed = parse('wma_{}', indicator)

    if indicator in ["open", "close", "high", "low"]:
        return 1

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
    
    elif indicator == "rsi":
        return 14

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

    elif '_shift_' in indicator:
        lst_split = indicator.split("_")
        if len(lst_split) == 3:
            return int(lst_split[2])
        else:
            return 0

    elif indicator == 'vsa':
        return 60

    elif indicator == "super_trend_direction":
        return 15

    return 0

def get_max_window_size(indicators):
    if not indicators:  # Check for empty or None
        return 0

    if isinstance(indicators, list):
        return max(get_window_size(indicator) for indicator in indicators)

    elif isinstance(indicators, dict):
        window_sizes = []
        for indicator, parameters in indicators.items():
            if isinstance(parameters, dict):
                window_size = parameters.get("window_size", get_window_size(indicator))
                window_size = int(window_size) if isinstance(window_size, str) else window_size
            elif isinstance(parameters, int):
                window_size = parameters
            else:
                window_size = get_window_size(indicator)

            window_sizes.append(window_size)

        return max(window_sizes) if window_sizes else 0

    return 0

def get_feature_from_fdp_features(fdp_features):
    lst_features = []
    for feature in fdp_features:
        if len(fdp_features[feature]) == 0:
            lst_features.append(feature)
        elif fdp_features[feature] != None:
            lst_param = list(fdp_features[feature])
            if "id" in lst_param:
                id = "_" + fdp_features[feature]["id"]
            else:
                id = ""
            if "n" in lst_param:
                n = "n" + fdp_features[feature]["n"] + "_"
            else:
                n = ""
            if not feature.startswith("postprocess"):
                lst_features.append(fdp_features[feature]["indicator"] + id)
            if "output" in lst_param:
                for output in fdp_features[feature]["output"]:
                    lst_features.append(output + id)
            if "indicator" in fdp_features[feature] \
                    and fdp_features[feature]["indicator"] == "shift" \
                    and "input" in lst_param:
                for input in fdp_features[feature]["input"]:
                    lst_features.append(n + input + id)
    return lst_features

def compute_indicators(df, indicators, keep_only_requested_indicators = False, params = None):
    if not isinstance(df, pd.DataFrame):
        return df

    # manage indicators as an array but it is converted into a dictionary
    if isinstance(indicators, list):
        indicators = dict.fromkeys(indicators, {})

    # call stockstats
    stock = Sdf.retype(df.copy())

    if isinstance(indicators, dict):
        keep_indicators = get_feature_from_fdp_features(indicators)
    else:
        keep_indicators = indicators

    # compute the indicators
    columns = list(df.columns)

    # be sure postprocess are treated at the end
    oindicators = OrderedDict()
    for indicator, parameters in indicators.items():
        if not indicator.startswith("postprocess"):
            oindicators[indicator] = parameters
    for indicator, parameters in indicators.items():
        if indicator.startswith("postprocess"):
            oindicators[indicator] = parameters
  

    for indicator, parameters in oindicators.items():
        if indicator in columns:
            continue
    
        # check if one deals with a postprocess
        if indicator.startswith("postprocess"):
            if "input" in parameters and "indicator" in parameters and "n" in parameters:
                indicator = parameters["indicator"]
                id = ""
                if "id" in parameters:
                    id = "_"+parameters["id"]
                n = parameters["n"]
                if isinstance(n, str):
                    n = int(n)
                input = [item+id for item in parameters["input"]]
                if isinstance(input, list):
                    if all(item in list(df.columns) for item in input):
                        df = utils.get_n_columns(df, input, n)

        # check if the indicator is overriden
        if "indicator" in parameters:
            indicator = parameters["indicator"]

        # prepare the suffix if an id is specified
        suffix = ""
        if 'id' in parameters:
            suffix = "_"+parameters["id"]

        trend_parsed = parse('trend_{}d', indicator)
        sma_parsed = parse('sma_{}', indicator)
        ema_parsed = parse('ema_{}', indicator)
        wma_parsed = parse('wma_{}', indicator)
        slope_parsed = parse('slope_{}', indicator)

        if trend_parsed != None and trend_parsed[0].isdigit():
            seq = int(trend_parsed[0])
            diff = df["close"] - df["close"].shift(seq)
            df["trend_"+str(seq)+"d"+ suffix] = diff.gt(0).map({False: 0, True: 1})

        elif indicator == "sma":
            seq = 10
            if "window_size" in parameters:
                seq = parameters["window_size"]
                if isinstance(seq, str):
                    seq = int(seq)
            df["sma"+ suffix] = TA.SMA(stock, seq).copy()

        elif indicator == "ema":
            period = 10
            if "window_size" in parameters:
                period = parameters["window_size"]
                if isinstance(period, str):
                    period = int(period)
            # df["ema"+ suffix] = TA.EMA(stock, period = period).copy()
            df["ema"+ suffix] = ta.trend.ema_indicator(close=df['close'], window=period).copy()

        elif indicator == 'willr':
            period = 14
            if "window_size" in parameters:
                period = parameters["window_size"]
                if isinstance(period, str):
                    period = int(period)
            df['willr'] = ta.momentum.williams_r(high=df['high'], low=df['low'], close=df['close'], lbp=period).copy()

        elif indicator == 'willr_trend':
            period = 14
            if "window_size" in parameters:
                period = parameters["window_size"]
                if isinstance(period, str):
                    period = int(period)

            predict_window = 4
            if "pred_window_size" in parameters:
                predict_window = parameters["pred_window_size"]
                if isinstance(predict_window, str):
                    predict_window = int(predict_window)

            df['willr_trend'] = ta.momentum.williams_r(high=df['high'], low=df['low'], close=df['close'], lbp=period).copy()

            df['willr_trend' + suffix] = df['willr_trend' + suffix].shift(-1)
            df.at[df.index[-1], "willr_trend" + suffix] = 0
            predict_val, coef = utils.predict_next_LinearRegression(df, 'willr_trend' + suffix, predict_window)

            df["willr_trend" + suffix] = utils.discret_coef(coef)

        elif indicator == "wma":
            period = 10
            if "window_size" in parameters:
                period = parameters["window_size"]
                if isinstance(period, str):
                    period = int(period)
            df["wma"+ suffix] = TA.WMA(stock, period = period).copy()

        elif sma_parsed != None and sma_parsed[0].isdigit():
            seq = int(sma_parsed[0])
            df["sma_"+str(seq)+ suffix] = TA.SMA(stock, seq).copy()

        elif ema_parsed != None and ema_parsed[0].isdigit():
            period = int(ema_parsed[0])
            df["ema_"+str(period)+ suffix] = TA.EMA(stock, period = period).copy()

        elif wma_parsed != None and wma_parsed[0].isdigit():
            period = int(wma_parsed[0])
            df["wma_"+str(period)+ suffix] = TA.WMA(stock, period = period).copy()

        elif slope_parsed != None and slope_parsed[0].isdigit():
            period = int(slope_parsed[0])
            df["slope_"+str(period)+ suffix] = df["close"].rolling(window=period).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])

        elif indicator == 'macd':
            df['macd' + suffix] = stock.get('macd').copy() # from stockstats
            #df['macd'] = TA.MACD(stock)['MACD'].copy() # from finta

        elif indicator == 'macds':
            df['macds' + suffix] = stock.get('macds').copy() # from stockstats

        elif indicator == 'macdh':
            df['macdh' + suffix] = stock.get('macdh').copy() # from stockstats

        elif indicator == 'bbands':
            bbands = TA.BBANDS(stock).copy()
            df = pd.concat([df, bbands], axis = 1)
            df.rename(columns={'BB_UPPER': 'bb_upper' + suffix}, inplace=True)
            df.rename(columns={'BB_MIDDLE': 'bb_middle' + suffix}, inplace=True)
            df.rename(columns={'BB_LOWER': 'bb_lower' + suffix}, inplace=True)

        elif indicator == 'rsi':
            rsi_window = 14
            if "window_size" in parameters:
                rsi_window = parameters["window_size"]
                if isinstance(rsi_window, str):
                    rsi_window = int(rsi_window)
            df['rsi' + suffix] = ta.momentum.rsi(close=df["close"], window=rsi_window)

        elif indicator == "trix":
            trix_obj = custom_indicators.Trix(
                close=df["close"],
                trix_length=parameters["trix_length"],
                trix_signal_length=parameters["trix_signal_length"],
                trix_signal_type=parameters["trix_signal_type"],
            )
            df["trix" + suffix] = trix_obj.get_trix_pct_line()
            df["trix_signal" + suffix] = trix_obj.get_trix_signal_line()
            df["trix_hist" + suffix] = df["trix" + suffix] - df["trix_signal" + suffix]
            if len(df["close"]) < parameters["long_ma_length"]:
                long_ma_length = len(df["close"])
            else:
                long_ma_length = parameters["long_ma_length"]
            df["long_ma" + suffix] = ta.trend.ema_indicator(
                df["close"], window=long_ma_length
            )

        elif indicator == 'stoch_rsi':
            rsi_window = 14
            smooth_k = 3
            smooth_d = 3
            if "stoch_rsi_window_size" in parameters:
                rsi_window = parameters["stoch_rsi_window_size"]
                if isinstance(rsi_window, str):
                    rsi_window = int(rsi_window)

            df['stoch_rsi' + suffix] = ta.momentum.stochrsi(close=df["close"]
                                                            , window=rsi_window) * 100
            df['stoch_rsi_k' + suffix] = ta.momentum.StochRSIIndicator(close=df["close"],
                                                                       window=rsi_window).stochrsi_k() * 100
            df['stoch_rsi_d' + suffix] = ta.momentum.StochRSIIndicator(close=df["close"],
                                                                       window=rsi_window).stochrsi_d() * 100
        elif indicator == 'stoch_rsi_pred':
            rsi_window = 14
            if "stoch_rsi_window_size" in parameters:
                rsi_window = parameters["stoch_rsi_window_size"]
                if isinstance(rsi_window, str):
                    rsi_window = int(rsi_window)
            
            predict_window = 4
            if "pred_window_size" in parameters:
                predict_window = parameters["pred_window_size"]
                if isinstance(predict_window, str):
                    predict_window = int(predict_window)
                    
            df['stoch_rsi_pred' + suffix] = ta.momentum.StochRSIIndicator(close=df["close"], window=rsi_window).stochrsi() * 100
            df['stoch_rsi_pred' + suffix] = df['stoch_rsi_pred' + suffix].shift(-1)
            df.at[df.index[-1], "stoch_rsi_pred" + suffix] = 0
            predict_val, coef = utils.predict_next_LinearRegression(df, 'stoch_rsi_pred' + suffix, predict_window)
            if predict_val < 0:
                predict_val = 0
            elif predict_val > 100:
                predict_val = 100
            df.at[df.index[-1], "stoch_rsi_pred" + suffix] = predict_val

        elif indicator == 'stoch_rsi_trend':
            rsi_window = 14
            if "stoch_rsi_window_size" in parameters:
                rsi_window = parameters["stoch_rsi_window_size"]
                if isinstance(rsi_window, str):
                    rsi_window = int(rsi_window)

            predict_window = 4
            if "pred_window_size" in parameters:
                predict_window = parameters["pred_window_size"]
                if isinstance(predict_window, str):
                    predict_window = int(predict_window)
                    
            df['stoch_rsi_trend' + suffix] = ta.momentum.StochRSIIndicator(close=df["close"],
                                                                           window=rsi_window).stochrsi() * 100
            df['stoch_rsi_k_trend' + suffix] = ta.momentum.StochRSIIndicator(close=df["close"],
                                                                             window=rsi_window).stochrsi_k() * 100
            df['stoch_rsi_d_trend' + suffix] = ta.momentum.StochRSIIndicator(close=df["close"],
                                                                             window=rsi_window).stochrsi_d() * 100
            df['stoch_rsi_trend' + suffix] = df['stoch_rsi_trend' + suffix].shift(-1)
            df['stoch_rsi_k_trend' + suffix] = df['stoch_rsi_k_trend' + suffix].shift(-1)
            df['stoch_rsi_d_trend' + suffix] = df['stoch_rsi_d_trend' + suffix].shift(-1)

            df.at[df.index[-1], "stoch_rsi_trend" + suffix] = 0
            predict_val, coef = utils.predict_next_LinearRegression(df, 'stoch_rsi_trend' + suffix, predict_window)
            df["stoch_rsi_trend" + suffix] = utils.discret_coef(coef)

            df.at[df.index[-1], "stoch_rsi_k_trend" + suffix] = 0
            predict_val, coef = utils.predict_next_LinearRegression(df, 'stoch_rsi_k_trend' + suffix, predict_window)
            df["stoch_rsi_k_trend" + suffix] = utils.discret_coef(coef)

            df.at[df.index[-1], "stoch_rsi_d_trend" + suffix] = 0
            predict_val, coef = utils.predict_next_LinearRegression(df, 'stoch_rsi_d_trend' + suffix, predict_window)
            df["stoch_rsi_d_trend" + suffix] = utils.discret_coef(coef)

        elif indicator == 'atr':
            atr_window = 14
            if "window_size" in parameters:
                atr_window = parameters["window_size"]
                if isinstance(atr_window, str):
                    atr_window = int(atr_window)
            df['atr' + suffix] = ta.volatility.AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=atr_window).average_true_range()

        elif indicator == 'ao':
            ao_window_1 = 6
            if "ao_window_1" in parameters:
                ao_window_1 = parameters["ao_window_1"]
                if isinstance(ao_window_1, str):
                    ao_window_1 = int(ao_window_1)

            ao_window_2 = 22
            if "ao_window_2" in parameters:
                ao_window_2 = parameters["ao_window_2"]
                if isinstance(ao_window_2, str):
                    ao_window_2 = int(ao_window_2)

            df['ao'] = ta.momentum.awesome_oscillator(df['high'], df['low'], window1=ao_window_1, window2=ao_window_2).copy()
        
        elif indicator == 'ao_trend':
            ao_window_1 = 6
            if "ao_window_1" in parameters:
                ao_window_1 = parameters["ao_window_1"]
                if isinstance(ao_window_1, str):
                    ao_window_1 = int(ao_window_1)

            ao_window_2 = 22
            if "ao_window_2" in parameters:
                ao_window_2 = parameters["ao_window_2"]
                if isinstance(ao_window_2, str):
                    ao_window_2 = int(ao_window_2)
                    
            predict_window = 4
            if "pred_window_size" in parameters:
                predict_window = parameters["pred_window_size"]
                if isinstance(predict_window, str):
                    predict_window = int(predict_window)

            df['ao_trend'] = ta.momentum.awesome_oscillator(df['high'], df['low'], window1=ao_window_1, window2=ao_window_2).copy()
            df['ao_trend' + suffix] = df['ao_trend' + suffix].shift(-1)
            df.at[df.index[-1], "ao_trend" + suffix] = 0
            predict_val, coef = utils.predict_next_LinearRegression(df, 'ao_trend' + suffix, predict_window)
            
            df["ao_trend" + suffix] = utils.discret_coef(coef)

        elif indicator == 'bollinger':
            bol_window = 100
            if "window_size" in parameters:
                bol_window = parameters["window_size"]
                if isinstance(bol_window, str):
                    bol_window = int(bol_window)
            bol_std = 2.25
            if "bol_std" in parameters:
                bol_std = parameters["bol_std"]
                if isinstance(bol_std, str):
                    bol_std = float(bol_std)
            long_ma_window = 500

            bol_band = ta.volatility.BollingerBands(close=df["close"], window=bol_window, window_dev=bol_std)
            df["lower_band"+ suffix] = bol_band.bollinger_lband()
            df["higher_band"+ suffix] = bol_band.bollinger_hband()
            df["ma_band"+ suffix] = bol_band.bollinger_mavg()
            df['long_ma' + suffix] = ta.trend.sma_indicator(close=df['close'], window=long_ma_window)

            df['bollinger' + suffix] = True # bollinger indicator trigger

        elif indicator == 'envelope':
            envelope_window = 5
            if "window_size" in parameters:
                envelope_window = parameters["ma_window_size"]
                if isinstance(envelope_window, str):
                    envelope_window = int(envelope_window)

            ma = "sma"
            if "ma" in parameters:
                ma = parameters["ma"]
                if not isinstance("ma", str):
                    ma = "sma"

            ma_offset_1 = 3
            ma_offset_2 = 5
            ma_offset_3 = 7
            if "ma_offset_1" in parameters:
                ma_offset_1 = parameters["ma_offset_1"]
                if isinstance(ma_offset_1, str):
                    ma_offset_1 = float(ma_offset_1)
            if "ma_offset_2" in parameters:
                ma_offset_2 = parameters["ma_offset_2"]
                if isinstance(ma_offset_2, str):
                    ma_offset_2 = float(ma_offset_2)
            if "ma_offset_3" in parameters:
                ma_offset_3 = parameters["ma_offset_3"]
                if isinstance(ma_offset_3, str):
                    ma_offset_3 = float(ma_offset_3)

            if ma == "sma":
                df["ma_base"+ suffix] = ta.trend.SMAIndicator(close=df["close"], window=envelope_window).sma_indicator()
                # df["ma_base"+ suffix] = ta.trend.sma_indicator(close=df["close"], window=envelope_window)
                # df["ma_base"+ suffix] = TA.SMA(df, envelope_window, "close")

            predict_val, coef = utils.predict_next_LinearRegression(df, "ma_base"+ suffix, envelope_window)
            df.at[df.index[-1], "ma_base" + suffix] = predict_val

            df["envelope_long_1"+ suffix] = df["ma_base"+ suffix] - df["ma_base"+ suffix] * ma_offset_1 / 100
            df["envelope_long_2"+ suffix] = df["ma_base"+ suffix] - df["ma_base"+ suffix] * ma_offset_2 / 100
            df["envelope_long_3"+ suffix] = df["ma_base"+ suffix] - df["ma_base"+ suffix] * ma_offset_3 / 100

            df["envelope_short_1"+ suffix] = df["ma_base"+ suffix] + df["ma_base"+ suffix] * ma_offset_1 / 100
            df["envelope_short_2"+ suffix] = df["ma_base"+ suffix] + df["ma_base"+ suffix] * ma_offset_2 / 100
            df["envelope_short_3"+ suffix] = df["ma_base"+ suffix] + df["ma_base"+ suffix] * ma_offset_3 / 100

            df['envelope' + suffix] = True # bollinger indicator trigger

        elif indicator == 'synthetic_bollinger':
            df.reset_index(inplace=True)
            # TEST SCENARIO
            df['close'] = 10
            df["lower_band"+ suffix] = 9
            df["higher_band"+ suffix] = 11
            df["ma_band"+ suffix] = 9.5
            df["long_ma"+ suffix] = 7

            t = 1000 + 50
            t_plus = 25
            df.at[t, "close"] = df["higher_band"+ suffix].iloc[t] + 0.01
            # OPEN LONG
            df['close'] = np.where(df.index >= t, df["higher_band"+ suffix] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["higher_band"+ suffix] + 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["higher_band"+ suffix] + 1.5, df['close'])
            # CLOSE LONG
            t = t + t_plus
            df['ma_band' + suffix] = np.where(df.index >= t, df["close"] + 1, df['ma_band' + suffix])

            # OPEN SHORT
            t = t + t_plus
            df['lower_band' + suffix] = np.where(df.index >= t, df["close"] + 0.6, df['lower_band' + suffix])
            df['long_ma+ suffix'] = np.where(df.index >= t, df["close"] + 0.3, df['long_ma' + suffix])

            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1.5, df['close'])
            t = t + t_plus
            # CLOSE SHORT
            df['ma_band' + suffix] = np.where(df.index >= t, df["close"] - 2.5, df['ma_band' + suffix])

            # OPEN LONG
            t = t + t_plus
            df['long_ma' + suffix] = np.where(df.index >= t, df["close"] - 0.3, df['long_ma' + suffix])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["higher_band"+ suffix] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] - 1.5, df['close'])
            # CLOSE LONG
            t = t + t_plus
            df['ma_band' + suffix] = np.where(df.index >= t, df["close"] + 2, df['ma_band' + suffix])

            t = t + t_plus
            df['higher_band' + suffix] = np.where(df.index >= t, df["higher_band"+ suffix] + 4, df['higher_band' + suffix])

            # OPEN SHORT
            t = t + t_plus
            df['lower_band' + suffix] = np.where(df.index >= t, df["close"] - 1, df['lower_band' + suffix])
            t = t + t_plus
            df['lower_band' + suffix] = np.where(df.index >= t, df["close"] + 1, df['lower_band' + suffix])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1.5, df['close'])
            # CLOSE SHORT BY MA_BAND ALREADY BELOW CLOSE

            # OPEN LONG
            t = t + t_plus
            df['higher_band' + suffix] = np.where(df.index >= t, df["higher_band"+ suffix] - 4, df['higher_band' + suffix])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 0.5, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1, df['close'])
            t = t + t_plus
            df['close'] = np.where(df.index >= t, df["close"] + 1.5, df['close'])

            # CLOSE LONG
            t = t + t_plus
            df['ma_band' + suffix] = np.where(df.index >= t, df["close"] + 0.5, df['ma_band' + suffix])

            # END OF SCENARIO
            df.set_index(['timestamp'], inplace=True, drop=True)
            df = utils.get_n_columns(df, ["ma_band"+ suffix, "lower_band"+ suffix, "higher_band"+ suffix, "close"], 1)

            df['syntheticbollinger' + suffix] = True  # bollinger indicator trigger

        elif indicator == 'cci_30':
            df['cci_30' + suffix] = stock.get('cci_30').copy()
        
        elif indicator == 'dx_30':
            df['dx_30' + suffix] = stock.get('dx_30').copy()
        
        elif indicator == 'williams_%r':
            df['williams_%r' + suffix] = TA.WILLIAMS(stock).copy()

        elif indicator == 'stoch_%k':
            df['stoch_%k' + suffix] = TA.STOCH(stock).copy()

        elif indicator == 'stoch_%d':
            df['stoch_%d' + suffix] = TA.STOCHD(stock).copy()
           
        elif indicator == 'er':
            df['er' + suffix] = TA.ER(stock).copy()
           
        elif indicator == 'stc':
            df['stc' + suffix] = TA.STC(stock).copy()
           
        elif indicator == 'adx':
            df['adx' + suffix] = TA.ADX(stock).copy()
           
        elif indicator == 'roc':
            df['roc' + suffix] = TA.ROC(stock).copy()

        elif indicator == 'mom':
            df['mom' + suffix] = TA.MOM(stock).copy()

        elif indicator == 'simple_rtn':
            df['simple_rtn' + suffix] = df['close'].pct_change()

        elif indicator == 'labeling':
            df = flabeling.data_labeling(df, params)

        elif indicator.startswith('tv_'):
            df[indicator] = tv.get_recommendation(df, indicator, params)

        # shift feature: column_shift_nb ex: close_shift_5
        elif '_shift_' in indicator:
            lst_split = indicator.split("_")
            df[indicator+ suffix] = df[lst_split[0]].shift(int(lst_split[2]), axis=0)

        elif indicator == 'vsa':
            days = [1, 2, 3, 5, 20, 40, 60]
            df = vsa.create_bunch_of_vsa_features(df, days)
            df['outcomes_vsa' + suffix] = df.close.pct_change(-1)

        elif indicator == "super_trend_direction":
            st = supertrend.SuperTrend(
                    df['high'], 
                    df['low'], 
                    df['close'], 
                    15, # self.st_short_atr_window
                    5 # self.st_short_atr_multiplier
                )
                
            df['super_trend_direction' + suffix] = st.super_trend_direction()
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
            df['super_trend_direction' + suffix] = super_trend.super_trend_direction()
            df['ema_short' + suffix] = ta.trend.ema_indicator(close=df['close'], window=short_ema_window)
            df['ema_long' + suffix] = ta.trend.ema_indicator(close=df['close'], window=long_ema_window)

            df = utils.get_n_columns(df, ["super_trend_direction"+ suffix, "ema_short"+ suffix, "ema_long"+ suffix], 1)
            df['superreversal' + suffix] = True  # super_reversal indicator trigger
            df['super_reversal' + suffix] = True  # super_reversal indicator trigger

        elif indicator == 'syntheticsuperreversal':
            df.reset_index(inplace=True)
            # TEST SCENARIO
            df['close'] = 5
            df["high"] = 10
            df["low"] = 17
            df["n1_ema_short"+ suffix] = 14
            df["n1_ema_long"+ suffix] = 15
            df["n1_super_trend_direction"+ suffix] = False

            # OPEN LONG AT t
            t = 100 + 400
            df['n1_ema_short' + suffix] = np.where(df.index >= t, df["n1_ema_long"+ suffix] + 1, df['n1_ema_short' + suffix])
            df['n1_super_trend_direction+ suffix'] = np.where(df.index >= t, True, df['n1_super_trend_direction' + suffix])
            df['low'] = np.where(df.index >= t, df["n1_ema_short"+ suffix] - 1, df['low'])

            df['close'] = np.where(df.index >= t + 10, df["close"] + 1, df['close'])

            # CLOSING SHORT
            t = t + 100
            df['n1_ema_short' + suffix] = np.where(df.index >= t, df["n1_ema_long"+ suffix] - 1, df['n1_ema_short' + suffix])
            df['n1_super_trend_direction' + suffix] = np.where(df.index >= t, False, df['n1_super_trend_direction' + suffix])
            df['high'] = np.where(df.index >= t, df["n1_ema_short"+ suffix] + 5, df['high'])

            # CLOSING SHORT
            t = t + 100
            df['n1_ema_short' + suffix] = np.where(df.index >= t, 20, df['n1_ema_short' + suffix])
            df['n1_ema_long' + suffix] = np.where(df.index >= t, df['n1_ema_short' + suffix] -1, df['n1_ema_long' + suffix])
            df['n1_super_trend_direction' + suffix] = np.where(df.index >= t, True, df['n1_super_trend_direction' + suffix])
            df['low'] = np.where(df.index >= t,  df['n1_ema_short' + suffix] -1, df['low'])

            # OPENING SHORT
            t = t + 100
            df['n1_ema_short' + suffix] = np.where(df.index >= t, 25, df['n1_ema_short' + suffix])
            df['n1_ema_long' + suffix] = np.where(df.index >= t, df['n1_ema_short' + suffix] +1, df['n1_ema_long' + suffix])
            df['n1_super_trend_direction' + suffix] = np.where(df.index >= t, False, df['n1_super_trend_direction' + suffix])
            df['high'] = np.where(df.index >= t,  df['n1_ema_short' + suffix] +2, df['high'])

            df['close'] = np.where(df.index >= t + 10, df["close"] - 1, df['close'])

            # CLOSING SHORT
            t = t + 100
            df['n1_ema_short' + suffix] = np.where(df.index >= t, 30, df['n1_ema_short' + suffix])
            df['n1_ema_long' + suffix] = np.where(df.index >= t, df['n1_ema_short' + suffix] -1, df['n1_ema_long' + suffix])
            df['n1_super_trend_direction' + suffix] = np.where(df.index >= t, True, df['n1_super_trend_direction' + suffix])
            df['low'] = np.where(df.index >= t,  df['n1_ema_short' + suffix] -1, df['low'])

            df["ema_short"+ suffix] = df["n1_ema_short"+ suffix]
            df["ema_long"+ suffix] =  df["n1_ema_long"+ suffix]
            df["super_trend_direction"+ suffix] =  df["n1_super_trend_direction"+ suffix]

            df['syntheticsuperreversal' + suffix] = True

            df.set_index(['timestamp'], inplace=True, drop=True)

    # keep only the requested indicators
    if keep_only_requested_indicators:
        for column in list(df.columns):
            if column not in keep_indicators:
                df.drop(columns=[column], inplace=True)

    # drop "timestamp" as it is redundant with index
    if "timestamp" in list(df.columns):
        df.drop(columns=["timestamp"], inplace=True)
    
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
