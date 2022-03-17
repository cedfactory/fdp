from tradingview_ta import TA_Handler, Interval, Exchange

g_interval_for_ta = {
    "1m" : Interval.INTERVAL_1_MINUTE,
    "5m" : Interval.INTERVAL_5_MINUTES,
    "15m" : Interval.INTERVAL_15_MINUTES,
    "30m" : Interval.INTERVAL_30_MINUTES,
    "1h" : Interval.INTERVAL_1_HOUR,
    "2h" : Interval.INTERVAL_2_HOURS,
    "4h" : Interval.INTERVAL_4_HOURS,
    "1d" : Interval.INTERVAL_1_DAY,
    "1W" : Interval.INTERVAL_1_WEEK,
    "1M" : Interval.INTERVAL_1_MONTH
}

def get_recommendation(screener, exchange, symbol, interval):
    tv_summary = None
    data_handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=g_interval_for_ta[interval])
    try:
        tv_summary = data_handler.get_analysis().summary
    except:
        print("!!! exception in get_recommendation")

    return tv_summary


def insert_tradingview_data(df, screener, exchange, symbol, interval, summary):
    recommendation = "RECOMMENDATION_" + interval
    df.loc[symbol, 'exchange'] = exchange
    df.loc[symbol, 'screener'] = screener
    df.loc[symbol, recommendation] = summary['RECOMMENDATION']
    sum = summary['BUY'] + summary['SELL'] + summary['NEUTRAL']
    df.loc[symbol, 'buy_' + interval] = int(100 * summary['BUY'] / sum)
    df.loc[symbol, 'sell_' + interval] = int(100 * summary['SELL'] / sum)
    df.loc[symbol, 'neutral_' + interval] = int(100 * summary['NEUTRAL'] / sum)

    return df


def get_recommendations_from_dataframe(df, interval):
    symbols = df['symbolTV'].tolist()
    df = df.set_index('symbolTV', drop=False)

    for symbol in symbols:
        screener = df.loc[symbol, 'screener']
        exchange = df.loc[symbol, 'exchange']

        tv_summary = get_recommendation(screener, exchange, symbol, interval)
        df = insert_tradingview_data(df, screener, exchange, symbol, interval, tv_summary)

    df.reset_index(inplace=True, drop=True)

    return df

def get_recommendations_from_list(symbols, screener, exchange, interval):
    recommendations = {}
    for symbol in symbols:
        tv_summary = get_recommendation(screener, exchange, symbol, interval)
        recommendations[symbol] = tv_summary

    return recommendations
