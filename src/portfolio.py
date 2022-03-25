import pandas as pd
from . import crypto, tradingview

def get_portfolio():
    df_gainers = crypto.get_top_gainers(50)
    symbols = df_gainers['symbol'].to_list()
    df_recommendations = tradingview.filter_with_tradingview_recommendations(symbols, ["BUY", "STRONG_BUY"])
    df_portfolio = pd.merge(df_gainers, df_recommendations)
    return df_portfolio
