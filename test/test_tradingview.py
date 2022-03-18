import pytest

import pandas as pd
from src import tradingview

class TestTradingView:

    def test_get_recommendations_from_list(self):
        symbol = "1INCHUSD"
        result = tradingview.get_recommendations_from_list("crypto", "ftx", [symbol], "1h")
        assert(symbol in result)
        assert(result[symbol]["status"] == "ok")
        assert("status" in result[symbol])
        assert(result[symbol]["status"] == "ok")
        assert("RECOMMENDATION" in result[symbol])
        assert(result[symbol]["RECOMMENDATION"] in ["STRONG_BUY", "BUY", "NEUTRAL", "SELL", "STRONG_SELL"])

    def test_get_recommendations_from_dataframe(self):
        symbols = ["1INCH/USD"]
        df = pd.DataFrame(symbols, columns =['symbol'])
        df['symbolTV'] = df['symbol'].str.replace("/", "")
        df['screener'] = "crypto"
        df['exchange'] = "ftx"
        
        df = tradingview.get_recommendations_from_dataframe(df, "2h")
        df = tradingview.get_recommendations_from_dataframe(df, "1d")

        assert(list(df.columns) == ["symbol", "symbolTV", "screener", "exchange", "RECOMMENDATION_2h", "buy_2h", "sell_2h", 'neutral_2h', "RECOMMENDATION_1d", "buy_1d", "sell_1d", "neutral_1d"])
