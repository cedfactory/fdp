from . import crypto, tradingview

def get_portfolio():
    df = crypto.get_top_gainers(50)
    symbols = df['symbol'].to_list()
    symbols = tradingview.filter_with_tradingview_recommendations(symbols, ["BUY", "STRONG_BUY"])
    return symbols
