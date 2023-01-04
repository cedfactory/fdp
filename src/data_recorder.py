import pandas as pd
import json
from datetime import datetime

from . import utils
from . import crypto
from . import config
from . import synthetic_data

class CryptoCache():
    def __init__(self, df, symbol, indicators, directory):
        self.symbol = symbol
        self.exchange_name = df.loc[df['symbol'] == symbol, 'exchange_name'].iloc[0]
        self.interval = df.loc[df['symbol'] == symbol, 'interval'].iloc[0]
        self.start_date = datetime.strptime(df.loc[df['symbol'] == symbol, 'start_date'].iloc[0], "%Y-%m-%d %H:%M:%S")
        self.end_date = datetime.strptime(df.loc[df['symbol'] == symbol, 'end_date'].iloc[0], "%Y-%m-%d %H:%M:%S")

        if config.SYMBOL_SYNTHETIC in self.symbol:
            self.ohlcv = synthetic_data.get_synthetic_data(self.exchange_name, self.symbol, self.start_date, self.end_date, self.interval, indicators)
        else:
            self.ohlcv = crypto.get_symbol_ohlcv(self.exchange_name, self.symbol, self.start_date, self.end_date, self.interval, None,indicators)

        # Trace for debug and adjust synthetics parameters
        if config.trace_ohlcv and 'close' in self.ohlcv.columns.tolist():
            df_plot = pd.DataFrame()
            df_plot["close"] = self.ohlcv['close']
            df_plot.reset_index(drop=True, inplace=True)
            ax = df_plot.plot.line()
            ax.figure.savefig(directory + self.symbol + '.png')

        # Trace for debug and adjust bollinger synthetics parameters
        if config.trace_ohlcv \
                and 'close' in self.ohlcv.columns.tolist() \
                and ('bollinger' in self.ohlcv.columns.tolist() or 'syntheticbollinger' in self.ohlcv.columns.tolist()):
            df_plot = pd.DataFrame()
            df_plot["close"] = self.ohlcv['close']
            df_plot["lower_band"] = self.ohlcv['lower_band']
            df_plot["higher_band"] = self.ohlcv['higher_band']
            df_plot["ma_band"] = self.ohlcv['ma_band']
            df_plot["long_ma"] = self.ohlcv['long_ma']

            df_plot.reset_index(drop=True, inplace=True)

            ax = df_plot.plot.line()

            # Add a legend
            pos = ax.get_position()
            ax.set_position([pos.x0, pos.y0, pos.width * 0.9, pos.height])
            ax.legend(loc='center right', bbox_to_anchor=(1.25, 0.5))

            ax.figure.savefig(directory + 'bollinger_' + self.symbol + '.png')

class DataRecorder():
    def __init__(self, csvfilename, indicatorfilename, params=None):
        self.df_symbols_param = pd.read_csv('./' + csvfilename)

        with open(indicatorfilename) as f:
            data = f.read()
        self.indicators = json.loads(data)

        self.lst_symbols = self.df_symbols_param["symbol"].tolist()
        self.data = {}

        if config.trace_ohlcv:
            self.directory = './plot/'
            utils.clear_directory(self.directory)

        for symbol in self.lst_symbols:
            self.data[symbol] = CryptoCache(self.df_symbols_param, symbol, self.indicators, self.directory)

    def get_symbol_ohlcv(self, exchange_name, symbol, start, end, timeframe, length, indicators):
        data = self.data[symbol]

        start = utils.convert_string_to_datetime(start)
        end = utils.convert_string_to_datetime(end)

        if data.symbol == symbol and data.exchange_name == exchange_name and data.interval == timeframe:
            df_ohlvc = data.ohlcv.copy()
            df_ohlvc = df_ohlvc.drop(df_ohlvc[df_ohlvc.index < start].index)
            df_ohlvc = df_ohlvc.drop(df_ohlvc[df_ohlvc.index > end].index)
        return df_ohlvc