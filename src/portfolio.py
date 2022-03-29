import pandas as pd
from . import crypto, tradingview

def get_portfolio(recommendations=["BUY", "STRONG_BUY"], intervals=["15m", "30m", "1h"]):
    df_gainers = crypto.get_top_gainers(50)
    symbols = df_gainers['symbol'].to_list()
    df_recommendations = tradingview.filter_with_tradingview_recommendations(symbols, recommendations, intervals)
    df_portfolio = pd.merge(df_gainers, df_recommendations)
    print(df_portfolio)
    return df_portfolio
