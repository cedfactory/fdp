import pandas as pd
import pytest

from src import indicators

class TestIndicators:

    def test_get_indicators(self):
        df_indicators = indicators.get_symbol_indicators({"close" : None, "high" : None}, "ftx", "BTC/USD", "01_04_2022", "01_05_2022", timeframe="1d")
        assert(isinstance(df_indicators,pd.DataFrame))
        assert(len(df_indicators.index) == 30)
