import pandas as pd
import json
from datetime import datetime

from . import utils
from . import crypto

class Data():
    def __init__(self, df, symbol, indicators):
        self.symbol = symbol
        self.exchange_name = df.loc[df['symbol'] == symbol, 'exchange_name'].iloc[0]
        self.start_date = datetime.strptime(df.loc[df['symbol'] == symbol, 'start_date'].iloc[0], "%Y-%m-%d %H:%M:%S")
        self.end_date = datetime.strptime(df.loc[df['symbol'] == symbol, 'end_date'].iloc[0], "%Y-%m-%d %H:%M:%S")
        self.interval = df.loc[df['symbol'] == symbol, 'interval'].iloc[0]
        self.ohlcv = crypto.get_symbol_ohlcv(self.exchange_name, self.symbol, self.start_date, self.end_date, self.interval, None,indicators)

class DataRecorder():
    def __init__(self, csvfilename, indicatorfilename, params=None):
        self.df_symbols_param = pd.read_csv('./' + csvfilename)

        with open(indicatorfilename) as f:
            data = f.read()
        self.indicators = json.loads(data)

        self.lst_symbols = self.df_symbols_param["symbol"].tolist()
        self.data = {}
        for symbol in self.lst_symbols:
            self.data[symbol] = Data(self.df_symbols_param, symbol, self.indicators)

    def get_symbol_ohlcv(self, exchange_name, symbol, start, end, timeframe, length, indicators):
        data = self.data[symbol]

        start = utils.convert_string_to_datetime(start)
        end = utils.convert_string_to_datetime(end)

        if data.symbol == symbol and data.exchange_name == exchange_name and data.interval == timeframe:
            df_ohlvc = data.ohlcv.copy()
            df_ohlvc = df_ohlvc.drop(df_ohlvc[df_ohlvc.index < start].index)
            df_ohlvc = df_ohlvc.drop(df_ohlvc[df_ohlvc.index > end].index)
        return df_ohlvc