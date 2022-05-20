from . import crypto
import pandas as pd

def get_symbol_indicators(map_indicators, exchange_name, symbol, start=None, end=None, timeframe="1d", length=None):
    df_result = crypto.get_symbol_ohlcv(exchange_name, symbol, start=start, end=end, timeframe=timeframe, length=length)
    if not isinstance(df_result, pd.DataFrame):
        return df_result

    # compute the indicators
    columns = list(df_result.columns)
    for indicator in map_indicators:
        indicator_name = indicator
        if map_indicators[indicator]:
            indicator_name = map_indicators[indicator].get("feature", indicator)
            
        print("indicator_name ", indicator_name)
        if not indicator_name in columns:
            print("compute ", indicator_name)

    # keep only the requested indicators
    requested_indicator_names = [indicator for indicator in map_indicators]
    print("requested_indicator_names ", requested_indicator_names)
    columns = list(df_result.columns)
    for column in columns:
        if not column in requested_indicator_names:
            df_result.drop(columns=[column], inplace=True)

    print(df_result)
    return df_result
    