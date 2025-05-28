import math
import numpy as np
import pandas as pd
import ta
import math
import requests

import talib
import pandas_ta as pandas_ta


def get_n_columns(df, columns, n=1):
    dt = df.copy()
    for col in columns:
        dt["n" + str(n) + "_" + col] = dt[col].shift(n)
    return dt


def chop(high, low, close, window=14):
    ''' Choppiness indicator
    '''
    tr1 = pd.DataFrame(high - low).rename(columns={0: 'tr1'})
    tr2 = pd.DataFrame(abs(high - close.shift(1))
                       ).rename(columns={0: 'tr2'})
    tr3 = pd.DataFrame(abs(low - close.shift(1))
                       ).rename(columns={0: 'tr3'})
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').dropna().max(axis=1)
    atr = tr.rolling(1).mean()
    highh = high.rolling(window).max()
    lowl = low.rolling(window).min()
    chop_serie = 100 * np.log10((atr.rolling(window).sum()) /
                                (highh - lowl)) / np.log10(window)
    return pd.Series(chop_serie, name="CHOP")


def fear_and_greed(close):
    ''' Fear and greed indicator
    '''
    response = requests.get("https://api.alternative.me/fng/?limit=0&format=json")
    dataResponse = response.json()['data']
    fear = pd.DataFrame(dataResponse, columns=['timestamp', 'value'])

    fear = fear.set_index(fear['timestamp'])
    fear.index = pd.to_datetime(fear.index, unit='s')
    del fear['timestamp']
    df = pd.DataFrame(close, columns=['close'])
    df['fearResult'] = fear['value']
    df['FEAR'] = df['fearResult'].ffill()
    df['FEAR'] = df.FEAR.astype(float)
    return pd.Series(df['FEAR'], name="FEAR")

class Ichimoku():
    def __init__(
            self,
            data,
            conversion_line_period,
            base_line_periods,
            lagging_span,
            displacement,
            ssl_atr_period
    ):
        self.data = data
        self.conversion_line_period = conversion_line_period
        self.base_line_periods = base_line_periods
        self.lagging_span = lagging_span
        self.displacement = displacement
        self.ssl_atr_period = ssl_atr_period

        # Input data
        self.high = self.data['high'].to_numpy()  # Ensure data is in NumPy format
        self.low = self.data['low'].to_numpy()
        self.close = self.data['close'].to_numpy()

        self._run()

    def _run(self):
        ssl_down, ssl_up = self.ssl_atr(period=self.ssl_atr_period)

        self.ssl_ok = (ssl_up > ssl_down).astype(int)
        self.ssl_bear = (ssl_up < ssl_down).astype(int)

        self.ichimoku()

    def ssl_atr(self, period=7):
        # Calculate ATR (Average True Range) with a window of 14
        atr = talib.ATR(self.high, self.low, self.close, timeperiod=14)

        # Calculate SMA of high and low with the given period
        sma_high = talib.SMA(self.high, timeperiod=period) + atr
        sma_low = talib.SMA(self.low, timeperiod=period) - atr

        # Determine HLV (High-Low Value)
        hlv = np.where(self.close > sma_high, 1, np.where(self.close < sma_low, -1, np.nan))

        # Convert HLV to DataFrame and forward-fill NaN values
        hlv = pd.Series(hlv, index=self.data.index).ffill()

        # Calculate SSL Down and SSL Up
        ssl_down = np.where(hlv < 0, sma_high, sma_low)
        ssl_up = np.where(hlv < 0, sma_low, sma_high)

        # Return the resulting DataFrames for SSL Down and SSL Up
        return pd.Series(ssl_down, index=self.data.index), pd.Series(ssl_up, index=self.data.index)

    def ichimoku(self):
        # Extract parameters from the class instance
        conv_period = self.conversion_line_period
        base_period = self.base_line_periods
        lag_span = self.lagging_span
        displacement = self.displacement

        # Convert data to Pandas Series for rolling operations
        high = pd.Series(self.high)
        low = pd.Series(self.low)
        close = pd.Series(self.close)

        # Compute Ichimoku components
        self.tenkan_sen = (high.rolling(window=conv_period).max() + low.rolling(window=conv_period).min()) / 2
        self.kijun_sen = (high.rolling(window=base_period).max() + low.rolling(window=base_period).min()) / 2
        self.senkou_span_a = ((self.tenkan_sen + self.kijun_sen) / 2).shift(displacement)
        self.senkou_span_b = ((high.rolling(window=lag_span).max() + low.rolling(window=lag_span).min()) / 2).shift(
            displacement)
        self.chikou_span = close.shift(-displacement)

        # Future cloud indicators
        self.future_green = (self.senkou_span_a > self.senkou_span_b).astype(int)
        self.future_red = (self.senkou_span_a < self.senkou_span_b).astype(int)

        # Cloud boundaries
        self.cloud_top = self.senkou_span_a.combine(self.senkou_span_b, np.maximum)
        self.cloud_bottom = self.senkou_span_a.combine(self.senkou_span_b, np.minimum)

        # Calculate Ichimoku bullish signal
        ichimoku_ok = (
                (self.tenkan_sen > self.kijun_sen) &
                (close > self.cloud_top) &
                (self.future_green > 0) &
                (self.chikou_span > self.cloud_top.shift(-displacement))
        ).astype(int)

        # Calculate Ichimoku bearish signal
        ichimoku_bear = (
                (self.tenkan_sen < self.kijun_sen) &
                (close < self.cloud_bottom) &
                (self.future_red > 0) &
                (self.chikou_span < self.cloud_bottom.shift(-displacement))
        ).astype(int)

        # Validate Ichimoku data
        self.ichimoku_valid = (~self.senkou_span_b.isna()).astype(int)

        # Align indices
        ichimoku_ok = pd.Series(ichimoku_ok.values, index=self.ssl_ok.index)
        ichimoku_bear = pd.Series(ichimoku_bear.values, index=self.ssl_bear.index)

        # Combine Ichimoku and SSL signals for bullish trend pulse
        self.trend_pulse = (
                (ichimoku_ok > 0) &
                (self.ssl_ok > 0)
        ).astype(int)

        # Combine Ichimoku and SSL signals for bearish trend pulse
        self.bear_trend_pulse = (
                (ichimoku_bear > 0) &
                (self.ssl_bear > 0)
        ).astype(int)

        # Reindex to match the main data's index
        self.ichimoku_valid.index = self.data.index
        self.ichimoku_valid = self.ichimoku_valid.reindex(self.data.index, method='ffill')
        self.trend_pulse = self.trend_pulse.reindex(self.data.index, method='ffill')
        self.bear_trend_pulse = self.bear_trend_pulse.reindex(self.data.index, method='ffill')

    def get_ichimoku_valid(self) -> pd.Series:
        return pd.Series(self.ichimoku_valid, name="ichimoku_valid")

    def get_trend_pulse(self) -> pd.Series:
        return pd.Series(self.trend_pulse, name="trend_pulse")

    def get_bear_trend_pulse(self) -> pd.Series:
        return pd.Series(self.bear_trend_pulse, name="bear_trend_pulse")

class ZeroLagMa():
    def __init__(
            self,
            close: pd.Series,
            ma_type,
            high_offset,
            low_offset,
            zema_len_buy,
            zema_len_sell
    ):
        self.close = close.copy()
        self.ma_type = ma_type
        self.high_offset = float(high_offset)
        self.low_offset = float(low_offset)
        self.zema_len_buy = int(zema_len_buy)
        self.zema_len_sell = int(zema_len_sell)
        self._run()

    def _run(self):
        if self.ma_type == "ZLEMA":
            zlema_buy = talib.EMA(self.close, timeperiod=self.zema_len_buy)
            self.zerolag_ma_buy_adj = zlema_buy * self.low_offset
            zlema_sell = talib.EMA(self.close, timeperiod=self.zema_len_sell)
            self.zerolag_ma_sell_adj = zlema_sell * self.high_offset

        elif self.ma_type == "ZLMA":
            zlma_buy = pandas_ta.zlma(self.close)
            self.zerolag_ma_buy_adj = zlma_buy * self.low_offset
            # zlma_sell = pandas_ta.zlma(self.close)
            zlma_sell = zlma_buy
            self.zerolag_ma_sell_adj = zlma_sell * self.high_offset

        elif self.ma_type == "TEMA":
            tema_buy = talib.TEMA(self.close, timeperiod=self.zema_len_buy)
            self.zerolag_ma_buy_adj = tema_buy * self.low_offset
            tema_sell = talib.TEMA(self.close, timeperiod=self.zema_len_sell)
            self.zerolag_ma_sell_adj = tema_sell * self.high_offset

        elif self.ma_type == "DEMA":
            dema_buy = talib.DEMA(self.close, timeperiod=self.zema_len_buy)
            self.zerolag_ma_buy_adj = dema_buy * self.low_offset
            dema_sell = talib.DEMA(self.close, timeperiod=self.zema_len_sell)
            self.zerolag_ma_sell_adj = dema_sell * self.high_offset

        elif self.ma_type == "ALMA":
            # Calculate the ALMA with custom parameters:
            # length: number of periods (e.g., 10)
            # sigma: smooth factor (e.g., 6)
            # offset: weight offset (e.g., 0.85)
            # df.ta.alma(length=10, sigma=6, offset=0.85, append=True)
            alma_buy = pandas_ta.alma(self.close, length=self.zema_len_buy)
            self.zerolag_ma_buy_adj = alma_buy * self.low_offset
            alma_sell = pandas_ta.alma(self.close, length=self.zema_len_sell)
            self.zerolag_ma_sell_adj = alma_sell * self.high_offset

        elif self.ma_type == "KAMA":
            kama_buy = talib.KAMA(self.close, timeperiod=self.zema_len_buy)
            self.zerolag_ma_buy_adj = kama_buy * self.low_offset
            kama_sell = talib.KAMA(self.close, timeperiod=self.zema_len_sell)
            self.zerolag_ma_sell_adj = kama_sell * self.high_offset

        elif self.ma_type == "HMA":
            hma_buy = pandas_ta.hma(self.close)
            hma_buy = hma_buy.dropna()
            hma_sell = hma_buy

            self.zerolag_ma_buy_adj = hma_buy * float(self.low_offset)
            self.zerolag_ma_sell_adj = hma_sell * float(self.high_offset)

    def get_zerolag_ma_buy_adj(self) -> pd.Series:
        return pd.Series(self.zerolag_ma_buy_adj, name="zerolag_ma_buy_adj")

    def get_zerolag_ma_sell_adj(self) -> pd.Series:
        return pd.Series(self.zerolag_ma_sell_adj, name="zerolag_ma_sell_adj")

class Trix():
    """ Trix indicator

        Args:
            close(pd.Series): dataframe 'close' columns,
            trix_length(int): the window length for each mooving average of the trix,
            trix_signal_length(int): the window length for the signal line
    """

    def __init__(
            self,
            close: pd.Series,
            trix_length: int = 9,
            trix_signal_length: int = 21,
            trix_signal_type: str = "sma"  # or ema
    ):
        self.close = close
        self.trix_length = trix_length
        self.trix_signal_length = trix_signal_length
        self.trix_signal_type = trix_signal_type
        self._run()

    def _run(self):
        self.trix_line = ta.trend.ema_indicator(
            ta.trend.ema_indicator(
                ta.trend.ema_indicator(
                    close=self.close, window=self.trix_length),
                window=self.trix_length), window=self.trix_length)

        self.trix_pct_line = self.trix_line.pct_change() * 100

        if self.trix_signal_type == "sma":
            self.trix_signal_line = ta.trend.sma_indicator(
                close=self.trix_pct_line, window=self.trix_signal_length)
        elif self.trix_signal_type == "ema":
            self.trix_signal_line = ta.trend.ema_indicator(
                close=self.trix_pct_line, window=self.trix_signal_length)

        self.trix_histo = self.trix_pct_line - self.trix_signal_line

    def get_trix_line(self) -> pd.Series:
        return pd.Series(self.trix_line, name="trix_line")

    def get_trix_pct_line(self) -> pd.Series:
        return pd.Series(self.trix_pct_line, name="trix_pct_line")

    def get_trix_signal_line(self) -> pd.Series:
        return pd.Series(self.trix_signal_line, name="trix_signal_line")

    def get_trix_histo(self) -> pd.Series:
        return pd.Series(self.trix_histo, name="trix_histo")


class VMC():
    """ VuManChu Cipher B + Divergences

        Args:
            high(pandas.Series): dataset 'High' column.
            low(pandas.Series): dataset 'Low' column.
            close(pandas.Series): dataset 'Close' column.
            wtChannelLen(int): n period.
            wtAverageLen(int): n period.
            wtMALen(int): n period.
            rsiMFIperiod(int): n period.
            rsiMFIMultiplier(int): n period.
            rsiMFIPosY(int): n period.
    """

    def __init__(
            self: pd.Series,
            open: pd.Series,
            high: pd.Series,
            low: pd.Series,
            close: pd.Series,
            wtChannelLen: int = 9,
            wtAverageLen: int = 12,
            wtMALen: int = 3,
            rsiMFIperiod: int = 60,
            rsiMFIMultiplier: int = 150,
            rsiMFIPosY: int = 2.5
    ) -> None:
        self._high = high
        self._low = low
        self._close = close
        self._open = open
        self._wtChannelLen = wtChannelLen
        self._wtAverageLen = wtAverageLen
        self._wtMALen = wtMALen
        self._rsiMFIperiod = rsiMFIperiod
        self._rsiMFIMultiplier = rsiMFIMultiplier
        self._rsiMFIPosY = rsiMFIPosY

        self._run()
        self.wave_1()

    def _run(self) -> None:
        self.hlc3 = (self._close + self._high + self._low)
        self._esa = ta.trend.ema_indicator(
            close=self.hlc3, window=self._wtChannelLen)
        self._de = ta.trend.ema_indicator(
            close=abs(self.hlc3 - self._esa), window=self._wtChannelLen)
        self._rsi = ta.trend.sma_indicator(self._close, self._rsiMFIperiod)
        self._ci = (self.hlc3 - self._esa) / (0.015 * self._de)

    def wave_1(self) -> pd.Series:
        """VMC Wave 1

        Returns:
            pandas.Series: New feature generated.
        """
        wt1 = ta.trend.ema_indicator(self._ci, self._wtAverageLen)
        return pd.Series(wt1, name="wt1")

    def wave_2(self) -> pd.Series:
        """VMC Wave 2

        Returns:
            pandas.Series: New feature generated.
        """
        wt2 = ta.trend.sma_indicator(self.wave_1(), self._wtMALen)
        return pd.Series(wt2, name="wt2")

    def money_flow(self) -> pd.Series:
        """VMC Money Flow

        Returns:
            pandas.Series: New feature generated.
        """
        mfi = ((self._close - self._open) /
               (self._high - self._low)) * self._rsiMFIMultiplier
        rsi = ta.trend.sma_indicator(mfi, self._rsiMFIperiod)
        money_flow = rsi - self._rsiMFIPosY
        return pd.Series(money_flow, name="money_flow")


def heikinAshiDf(df):
    df['HA_Close'] = (df.open + df.high + df.low + df.close) / 4
    ha_open = [(df.open[0] + df.close[0]) / 2]
    [ha_open.append((ha_open[i] + df.HA_Close.values[i]) / 2)
     for i in range(0, len(df) - 1)]
    df['HA_Open'] = ha_open
    df['HA_High'] = df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    df['HA_Low'] = df[['HA_Open', 'HA_Close', 'low']].min(axis=1)
    return df


class SmoothedHeikinAshi():
    def __init__(self, open, high, low, close, smooth1=5, smooth2=3):
        self.open = open.copy()
        self.high = high.copy()
        self.low = low.copy()
        self.close = close.copy()
        self.smooth1 = smooth1
        self.smooth2 = smooth2
        self._run()

    def _calculate_ha_open(self):
        ha_open = pd.Series(np.nan, index=self.open.index)
        start = 0
        for i in range(1, len(ha_open)):
            if np.isnan(self.smooth_open.iloc[i]):
                continue
            else:
                ha_open.iloc[i] = (self.smooth_open.iloc[i] + self.smooth_close.iloc[i]) / 2
                start = i
                break

        for i in range(start + 1, len(ha_open)):
            ha_open.iloc[i] = (ha_open.iloc[i - 1] + self.ha_close.iloc[i - 1]) / 2

        return ha_open

    def _run(self):
        self.smooth_open = ta.trend.ema_indicator(self.open, self.smooth1)
        self.smooth_high = ta.trend.ema_indicator(self.high, self.smooth1)
        self.smooth_low = ta.trend.ema_indicator(self.low, self.smooth1)
        self.smooth_close = ta.trend.ema_indicator(self.close, self.smooth1)

        self.ha_close = (self.smooth_open + self.smooth_high + self.smooth_low + self.smooth_close) / 4
        self.ha_open = self._calculate_ha_open()

        self.smooth_ha_close = ta.trend.ema_indicator(self.ha_close, self.smooth2)
        self.smooth_ha_open = ta.trend.ema_indicator(self.ha_open, self.smooth2)

    def smoothed_ha_close(self):
        return self.smooth_ha_close

    def smoothed_ha_open(self):
        return self.smooth_ha_open


def volume_anomality(df, volume_window=10):
    dfInd = df.copy()
    dfInd["VolAnomaly"] = 0
    dfInd["PreviousClose"] = dfInd["close"].shift(1)
    dfInd['MeanVolume'] = dfInd['volume'].rolling(volume_window).mean()
    dfInd['MaxVolume'] = dfInd['volume'].rolling(volume_window).max()
    dfInd.loc[dfInd['volume'] > 1.5 * dfInd['MeanVolume'], "VolAnomaly"] = 1
    dfInd.loc[dfInd['volume'] > 2 * dfInd['MeanVolume'], "VolAnomaly"] = 2
    dfInd.loc[dfInd['volume'] >= dfInd['MaxVolume'], "VolAnomaly"] = 3
    dfInd.loc[dfInd['PreviousClose'] > dfInd['close'],
    "VolAnomaly"] = (-1) * dfInd["VolAnomaly"]
    return dfInd["VolAnomaly"]


class SuperTrend():
    def __init__(
            self,
            high,
            low,
            close,
            atr_window=10,
            atr_multi=3
    ):
        self.high = high
        self.low = low
        self.close = close
        self.atr_window = atr_window
        self.atr_multi = atr_multi
        self._run()

    def _run(self):
        # calculate ATR
        price_diffs = [self.high - self.low,
                       self.high - self.close.shift(),
                       self.close.shift() - self.low]
        true_range = pd.concat(price_diffs, axis=1)
        true_range = true_range.abs().max(axis=1)
        # default ATR calculation in supertrend indicator
        atr = true_range.ewm(alpha=1 / self.atr_window, min_periods=self.atr_window).mean()
        # atr = ta.volatility.average_true_range(high, low, close, atr_period)
        # df['atr'] = df['tr'].rolling(atr_period).mean()

        # HL2 is simply the average of high and low prices
        hl2 = (self.high + self.low) / 2
        # upperband and lowerband calculation
        # notice that final bands are set to be equal to the respective bands
        final_upperband = upperband = hl2 + (self.atr_multi * atr)
        final_lowerband = lowerband = hl2 - (self.atr_multi * atr)

        # initialize Supertrend column to True
        supertrend = [True] * len(self.close)

        for i in range(1, len(self.close)):
            curr, prev = i, i - 1

            # if current close price crosses above upperband
            if self.close[curr] > final_upperband[prev]:
                supertrend[curr] = True
            # if current close price crosses below lowerband
            elif self.close[curr] < final_lowerband[prev]:
                supertrend[curr] = False
            # else, the trend continues
            else:
                supertrend[curr] = supertrend[prev]

                # adjustment to the final bands
                if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                    final_lowerband[curr] = final_lowerband[prev]
                if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                    final_upperband[curr] = final_upperband[prev]

            # to remove bands according to the trend direction
            if supertrend[curr] == True:
                final_upperband[curr] = np.nan
            else:
                final_lowerband[curr] = np.nan

        self.st = pd.DataFrame({
            'Supertrend': supertrend,
            'Final Lowerband': final_lowerband,
            'Final Upperband': final_upperband
        })

    def super_trend_upper(self):
        return self.st['Final Upperband']

    def super_trend_lower(self):
        return self.st['Final Lowerband']

    def super_trend_direction(self):
        return self.st['Supertrend']


class MaSlope():
    """ Slope adaptative moving average
    """

    def __init__(
            self,
            close: pd.Series,
            high: pd.Series,
            low: pd.Series,
            long_ma: int = 200,
            major_length: int = 14,
            minor_length: int = 6,
            slope_period: int = 34,
            slope_ir: int = 25
    ):
        self.close = close
        self.high = high
        self.low = low
        self.long_ma = long_ma
        self.major_length = major_length
        self.minor_length = minor_length
        self.slope_period = slope_period
        self.slope_ir = slope_ir
        self._run()

    def _run(self):
        minAlpha = 2 / (self.minor_length + 1)
        majAlpha = 2 / (self.major_length + 1)
        # df = pd.DataFrame(data = [self.close, self.high, self.low], columns = ['close','high','low'])
        df = pd.DataFrame(data={"close": self.close, "high": self.high, "low": self.low})
        df['hh'] = df['high'].rolling(window=self.long_ma + 1).max()
        df['ll'] = df['low'].rolling(window=self.long_ma + 1).min()
        df = df.fillna(0)
        df.loc[df['hh'] == df['ll'], 'mult'] = 0
        df.loc[df['hh'] != df['ll'], 'mult'] = abs(2 * df['close'] - df['ll'] - df['hh']) / (df['hh'] - df['ll'])
        df['final'] = df['mult'] * (minAlpha - majAlpha) + majAlpha

        ma_first = (df.iloc[0]['final'] ** 2) * df.iloc[0]['close']

        col_ma = [ma_first]
        for i in range(1, len(df)):
            ma1 = col_ma[i - 1]
            col_ma.append(ma1 + (df.iloc[i]['final'] ** 2) * (df.iloc[i]['close'] - ma1))

        df['ma'] = col_ma
        pi = math.atan(1) * 4
        df['hh1'] = df['high'].rolling(window=self.slope_period).max()
        df['ll1'] = df['low'].rolling(window=self.slope_period).min()
        df['slope_range'] = self.slope_ir / (df['hh1'] - df['ll1']) * df['ll1']
        df['dt'] = (df['ma'].shift(2) - df['ma']) / df['close'] * df['slope_range']
        df['c'] = (1 + df['dt'] * df['dt']) ** 0.5
        df['xangle'] = round(180 * np.arccos(1 / df['c']) / pi)
        df.loc[df['dt'] > 0, "xangle"] = - df['xangle']
        self.df = df
        # print(df)

    def ma_line(self) -> pd.Series:
        """ ma_line

            Returns:
                pd.Series: ma_line
        """
        return self.df['ma']

    def x_angle(self) -> pd.Series:
        """ x_angle

            Returns:
                pd.Series: x_angle
        """
        return self.df['xangle']

class TrendIndicator():
    def __init__(
            self,
            close: pd.Series,
            open: pd.Series,
            low: pd.Series,
            high: pd.Series,
            volume: pd.Series,
            trend_type,
    ):
        self.close = close
        self.open = open
        self.low = low
        self.high = high
        self.volume = volume
        self.trend_type = trend_type
        self._run()

    def _run(self):
        if self.trend_type == 'TSI':
            # True Strength Index (TSI)
            df_tsi = pandas_ta.tsi(self.close, long=25, short=13)
            # Dynamically grab the first two columns regardless of their names
            raw_tsi_col, signal_tsi_col = df_tsi.columns[:2]
            # Create a trend difference column
            df_tsi['trend_diff'] = df_tsi[raw_tsi_col] - df_tsi[signal_tsi_col]

            # Create a trend column: 1 if uptrend (raw TSI > signal), -1 if downtrend
            trend_array = np.where(df_tsi[raw_tsi_col] > df_tsi[signal_tsi_col], 1, -1)

        elif self.trend_type == 'FISHER':
            # Fisher Transform
            df_fisher = pandas_ta.fisher(self.high, self.low, length=9)

            # Dynamically grab the first two columns regardless of their names
            raw_fisher_col, signal_fisher_col = df_fisher.columns[:2]

            # Create a trend difference column
            df_fisher['trend_diff'] = df_fisher[raw_fisher_col] - df_fisher[signal_fisher_col]

            # Create a trend column: 1 if uptrend (raw Fisher > signal Fisher), -1 if downtrend
            trend_array = np.where(df_fisher[raw_fisher_col] > df_fisher[signal_fisher_col], 1, -1)

        elif self.trend_type == 'KALMAN':
            # Kalman Filter: often you compare the price to the filter output.
            s_Kalman = self.kalman_filter_numpy(self.close)
            # Bullish if the current close is above the Kalman filter value, bearish otherwise.
            trend_array = np.where(self.close > s_Kalman, 1, -1)

        elif self.trend_type == 'SAR':
            # Compute Parabolic SAR using TA-Lib.
            s_SAR = talib.SAR(self.high, self.low, acceleration=0.02, maximum=0.2)
            # For SAR, if the close is above the SAR value, the trend is bullish; if below, bearish.
            trend_array = np.where(self.close > s_SAR, 1, -1)

        elif self.trend_type == 'PRICE_ACTION':
            # Compute highest and lowest window over 10 periods
            self.s_highest_window = self.high.rolling(window=10).max()
            self.s_lowest_window = self.low.rolling(window=10).min()

            # Identify buy and sell signals
            self.buy_signal = self.close > self.s_highest_window.shift(1)
            self.sell_signal = self.close < self.s_lowest_window.shift(1)

            # Create trend array based on price action
            trend_array = np.zeros(len(self.buy_signal), dtype=int)
            trend_array[self.buy_signal] = 1  # Uptrend when close breaks highest_window
            trend_array[self.sell_signal] = -1  # Downtrend when close breaks lowest_window

        self.trend_series = pd.Series(trend_array, index=self.close.index)

    def get_trend(self) -> pd.Series:
        return self.trend_series

    def get_s_highest_window(self) -> pd.Series:
        return self.s_highest_window

    def get_s_lowest_window(self) -> pd.Series:
        return self.s_lowest_window

    def get_high_tf_close(self) -> pd.Series:
        return self.close

    def kalman_filter_numpy(self, series, process_variance=1e-5, measurement_variance=1e-1):
        x = series.values  # Convert to a Numpy array
        n = x.size
        estimates = np.empty(n)

        # Initialize with the first observation
        estimates[0] = x[0]
        posteri_estimate = x[0]
        posteri_error_estimate = 1.0

        for t in range(1, n):
            # Prediction step
            priori_estimate = posteri_estimate
            priori_error_estimate = posteri_error_estimate + process_variance

            # Update step
            blending_factor = priori_error_estimate / (priori_error_estimate + measurement_variance)
            posteri_estimate = priori_estimate + blending_factor * (x[t] - priori_estimate)
            posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

            estimates[t] = posteri_estimate

        return pd.Series(estimates, index=series.index)



class ATR():
    def __init__(
            self,
            df
    ):
        self.df = df
        self._run()

    def _run(self):
        self.df['ATR'] = self.df.ta.atr(length=14)

        # If you want a different period, just change `length`:
        self.df['ATR_21'] = self.df.ta.atr(length=21)

        # And if you’d like to inspect other ATR variants:
        #   ma=True uses a simple MA instead of Wilder smoothing
        self.df['ATR_SMA'] = self.df.ta.atr(length=14, mamode='sma')


    def get_atr_14(self) -> pd.Series:
        return self.df.ATR

    def get_atr_21(self) -> pd.Series:
        return self.df.ATR_21

    def get_atr_sma(self) -> pd.Series:
        return self.df.ATR_SMA
















