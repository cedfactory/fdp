from abc import ABCMeta
import pandas as pd
from . import crypto

class FDP(metaclass=ABCMeta):

    def __init__(self, params=None):
        self.exchange_name = ""
        self.exchange = None
        self.markets = None
        if params:
            self.exchange_name = params.get("exchange_name", self.exchange_name)

        if self.exchange_name:
            self.exchange, self.markets = crypto.get_exchange_and_markets(self.exchange_name)

    def get_symbol_ohlcv(self, symbol, start, end=None, timeframe="1d", length = None, indicators = {}):
        return crypto.get_symbol_ohlcv(self.exchange_name, symbol, start, end, timeframe, length, indicators, self.exchange)

    def get_symbol_ohlcv_last(self, symbol, start=None, end=None, timeframe="1d", indicators=None, candle_stick="released"):
        if indicators is None:
            indicators = {}
        return crypto.get_symbol_ohlcv_last(
            self.exchange_name,
            symbol,
            start, end, timeframe, 1,
            indicators, exchange=self.exchange,
            candle_stick=candle_stick)
