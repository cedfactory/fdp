import pandas as pd
from datetime import datetime
from . import wiki,yahoo

def api_list(markets):
    start = datetime.now()

    result_for_response = {}

    for market in markets:
        df = None
        if market in ["w_cac", "w_cac40", "w_CAC", "w_CAC40"]:
            df = wiki.get_list_cac()
        elif market in ["dax", "DAX"]:
            df = wiki.get_list_dax()
        elif market in ["w_nasdaq", "w_nasdaq100", "w_NASDAQ", "w_NASDAQ100"]:
            df = wiki.get_list_nasdaq100()
        elif market in ["w_dji", "w_DJI"]:
            df = wiki.get_list_dji()
        elif market in ["w_sp500", "w_SP500"]:
            df = wiki.get_list_sp500()
        
        elif market in ["y_nasdaq"]:
            df = yahoo.get_list_nasdaq()
        elif market in ["y_sp500"]:
            df = yahoo.get_list_yahoo_sp500()
        elif market in ["y_dow"]:
            df = yahoo.get_list_dow()
        elif market in ["y_ftse100"]:
            df = yahoo.get_list_ftse100
        elif market in ["y_ftse250"]:
            df = yahoo.get_list_ftse250()
        elif market in ["y_ibovespa"]:
            df = yahoo.get_list_ibovespa()
        elif market in ["y_nifty50"]:
            df = yahoo.get_list_nifty50()
        elif market in ["y_nifty_bank"]:
            df = yahoo.get_list_nifty_bank()
        elif market in ["y_euronext"]:
            df = yahoo.get_list_euronext()
        elif market in ["y_undervalued"]:
            df = yahoo.get_list_undervalued()
        elif market in ["y_losers"]:
            df = yahoo.get_list_losers()
        elif market in ["y_gainers"]:
            df = yahoo.get_list_gainers()
        elif market in ["y_most_actives"]:
            df = yahoo.get_list_most_actives()
        elif market in ["y_trending_tickers"]:
            df = yahoo.get_list_trending_tickers()

        current_result = {}
        if isinstance(df, pd.DataFrame) == True:
            current_result["dataframe"] = df.to_json()
            current_result["status"] = "ok"
        else:
            current_result["status"] = "ko"

        result_for_response[market] = current_result

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response
