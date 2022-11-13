import pytest

import pandas as pd
from src import tradingview

class TestTradingView:

    def test_get_recommendations_from_list(self):
        symbol = "1INCHUSD"
        result = tradingview.get_recommendations_from_list("crypto", "binance", [symbol], "1h")
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
        df['exchange'] = "binance"
        
        df = tradingview.get_recommendations_from_dataframe(df, "2h")
        df = tradingview.get_recommendations_from_dataframe(df, "1d")

        assert(list(df.columns) == ["symbol", "symbolTV", "screener", "exchange", "RECOMMENDATION_2h", "buy_2h", "sell_2h", 'neutral_2h', "RECOMMENDATION_1d", "buy_1d", "sell_1d", "neutral_1d"])

    def test_remove_rows_where_recommendation_not_in_filter(self):
        df_symbol = pd.DataFrame({
        'RECOMMENDATION_15m': ['BUY', 'BUY', 'NEUTRAL', 'STRONG_BUY', 'BUY', 'NEUTRAL'],
        'RECOMMENDATION_30m': ['BUY', 'SELL', 'BUY', 'STRONG_BUY', 'STRONG_BUY', 'NEUTRAL'],
        'RECOMMENDATION_1h': ['BUY', 'STRONG_BUY', 'STRONG_BUY', 'STRONG_SELL', 'STRONG_BUY', 'SELL'],
        'foobar': ['NEUTRAL', 'NEUTRAL', 'SELL', 'SELL', 'STRONG_SELL', 'BUY'],
        'value': [1, 2, 3, 4, 5, 6],
        })
        filter = ['BUY', 'STRONG_BUY']
        df_symbol = tradingview.remove_rows_where_recommendation_not_in_filter(df_symbol, filter)
        assert(len(df_symbol.index) == 2)

    def test_filter_with_tradingview_recommendations(self):
        symbols = ['AXS/USD', 'BICO/USD', 'CTX/USD', 'SLP/USD', 'STSOL/USD', 'SOL/USD']
        df_filtered_symbols = tradingview.filter_with_tradingview_recommendations(symbols, ['STRONG_BUY', 'BUY', 'NEUTRAL'], ["15m", "30m", "1h"])

        # result is a dataframe
        assert(isinstance(df_filtered_symbols,pd.DataFrame))

        # check the columns names
        columns = df_filtered_symbols.columns.tolist()
        assert(any(column in ['symbol', 'RECOMMENDATION_15m', 'RECOMMENDATION_30m', 'RECOMMENDATION_1h'] for column in columns))

        # check the filtered symbols
        assert(all(symbol in symbols for symbol in df_filtered_symbols['symbol'].tolist()))
                
