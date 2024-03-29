from tradingview_ta import TA_Handler, Interval, Exchange
import pandas as pd
import concurrent.futures

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
    tv_summary = {}
    data_handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=g_interval_for_ta[interval])
    try:
        tv_summary = data_handler.get_analysis().summary
        tv_summary["status"] = "ok"
    except:
        tv_summary = {"status":"ko", "message":"exception in tradvingview.get_analysis"}

    return tv_summary


def insert_tradingview_data(df, screener, exchange, symbol, interval, summary):
    recommendation = "RECOMMENDATION_" + interval
    df.loc[symbol, 'exchange'] = exchange
    df.loc[symbol, 'screener'] = screener
    df.loc[symbol, recommendation] = summary['RECOMMENDATION']
    tot = summary['BUY'] + summary['SELL'] + summary['NEUTRAL']
    df.loc[symbol, 'buy_' + interval] = int(100 * summary['BUY'] / tot)
    df.loc[symbol, 'sell_' + interval] = int(100 * summary['SELL'] / tot)
    df.loc[symbol, 'neutral_' + interval] = int(100 * summary['NEUTRAL'] / tot)

    return df


def get_recommendations_from_dataframe(df, interval):
    symbols = df['symbolTV'].tolist()
    df = df.set_index('symbolTV', drop=False)

    for symbol in symbols:
        screener = df.loc[symbol, 'screener']
        exchange = df.loc[symbol, 'exchange']

        tv_summary = get_recommendation(screener, exchange, symbol, interval)
        if tv_summary["status"] == "ok":
            df = insert_tradingview_data(df, screener, exchange, symbol, interval, tv_summary)

    df.reset_index(inplace=True, drop=True)

    return df

def get_recommendations_from_list(screener, exchange, symbols, interval):
    recommendations = {}
    for symbol in symbols:
        tv_summary = get_recommendation(screener, exchange, symbol, interval)
        recommendations[symbol] = tv_summary

    return recommendations

def remove_rows_where_recommendation_not_in_filter(df, filter):
    recommendations_columns = [column for column in df.columns if column.startswith('RECOMMENDATION_')]
    for recommendation_column in recommendations_columns:
        index_names = df[~df[recommendation_column].isin(filter)].index
        df.drop(index_names , inplace=True)
    return df

def filter_with_tradingview_recommendations(exchange, symbols, recommendations, intervals):
    df_symbol = pd.DataFrame(symbols, columns =['symbol'])
    df_symbol['symbolTV'] = df_symbol['symbol'].str.replace("/", "")
    df_symbol['exchange'] = exchange
    df_symbol['screener'] = 'crypto'

    # get recommendations
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for interval in intervals:
            futures.append(executor.submit(get_recommendations_from_dataframe, df=df_symbol, interval=interval))
        for future in concurrent.futures.as_completed(futures):
            df_symbol = pd.merge(df_symbol, future.result())
            
    # filter symbols
    df_symbol = remove_rows_where_recommendation_not_in_filter(df_symbol, recommendations)
 
    # cleaning
    columns_to_drop = ['symbolTV', 'exchange', 'screener',
                        'buy_1h', 'sell_1h', 'neutral_1h',
                        'buy_15m', 'sell_15m', 'neutral_15m',
                        'buy_30m', 'sell_30m', 'neutral_30m']
    df_symbol.drop(columns_to_drop, axis = 1, inplace=True)

    return df_symbol
