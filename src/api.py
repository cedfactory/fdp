import pandas as pd
from datetime import datetime
from . import wiki,yahoo,yf_wrapper,crypto

map_market_function = {
    "w_cac":                wiki.get_list_cac,
    "w_dax":                wiki.get_list_dax,
    "w_nasdaq":             wiki.get_list_nasdaq100,
    "w_dji":                wiki.get_list_dji,
    "w_sp500":              wiki.get_list_sp500,
    
    "y_nasdaq":             yahoo.get_list_nasdaq,
    "y_sp500":              yahoo.get_list_yahoo_sp500,
    "y_dow":                yahoo.get_list_dow,
    "y_ftse100":            yahoo.get_list_ftse100,
    "y_ftse250":            yahoo.get_list_ftse250,
    "y_ibovespa":           yahoo.get_list_ibovespa,
    "y_nifty50":            yahoo.get_list_nifty50,
    "y_nifty_bank":         yahoo.get_list_nifty_bank,
    "y_euronext":           yahoo.get_list_euronext,
    "y_undervalued":        yahoo.get_list_undervalued,
    "y_losers":             yahoo.get_list_losers,
    "y_gainers":            yahoo.get_list_gainers,
    "y_most_actives":       yahoo.get_list_most_actives,
    "y_trending_tickers":   yahoo.get_list_trending_tickers,

    "c_hitbtc":             crypto.get_list_symbols_hitbtc,
    "c_bitmex":             crypto.get_list_symbols_bitmex,
    "c_binance":            crypto.get_list_symbols_binance,
    "c_ftx":                crypto.get_list_symbols_ftx
}

def api_list(str_markets):
    if str_markets == None:
        return {"result":{}, "status":"ko", "reason":"no market", "elapsed_time":"0"}

    start = datetime.now()

    result_for_response = {}

    markets = str_markets.split(',')
    for market in markets:
        df = None
        if market in map_market_function.keys():
            df = map_market_function[market]()
        else:
            result_for_response[market] = {"dataframe":"", "status":"ko", "reason":"unknown market"}
            continue

        current_result = {}
        if isinstance(df, pd.DataFrame) == True:
            current_result["dataframe"] = df.to_json()
            current_result["status"] = "ok"
        else:
            current_result["status"] = "ko"
            current_result["reason"] = "invalid dataframe"

        result_for_response[market] = current_result

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response

def api_value(str_values):
    if str_values == None:
        return {"result":{}, "status":"ko", "reason":"no values", "elapsed_time":"0"}

    start = datetime.now()

    result_for_response = {}

    values = str_values.split(',')
    for value in values:
        if '_' in value:
            # crypto
            info = crypto.get_symbol_ticker("hitbtc", value.replace("_", "/"))
            value_info = {"status": "ok", "info": info}
        else:
            value_info = yf_wrapper.get_info(value)
        result_for_response[value] = value_info

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response

def api_history(str_source, str_symbol, str_start, length):
    if str_source == None or str_symbol == None:
        return {"result":{}, "status":"ko", "reason":"source or symbol not specified", "elapsed_time":"0"}

    start = datetime.now()

    result_for_response = {}

    if '_' in str_symbol:
        # crypto ('_' stands for '/')
        df = crypto.get_symbol_ohlcv(str_source, str_symbol.replace("_", "/"), str_start, "1d", length)
        if isinstance(df, pd.DataFrame):
            result_for_response[str_symbol] = {"status": "ok", "info": df.to_json()}
        else:
            result_for_response[str_symbol] = {"status": "ko", "reason": df, "info": ""}

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response
   
