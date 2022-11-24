import pandas as pd
from datetime import datetime
from . import wiki,yahoo,yf_wrapper,crypto,tradingview,portfolio,indicators
from src import config
import concurrent.futures
import json

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

    "hitbtc":             crypto.get_list_symbols_hitbtc,
    "bitmex":             crypto.get_list_symbols_bitmex,
    "binance":            crypto.get_list_symbols_binance,
    "ftx":                crypto.get_list_symbols_ftx
}

def api_list(str_exchanges):
    if str_exchanges == None:
        return {"result":{}, "status":"ko", "reason":"no market", "elapsed_time":"0"}

    start = datetime.now()

    result_for_response = {}

    exchanges = str_exchanges.split(',')
    for exchange in exchanges:
        result = None
        if exchange in map_market_function.keys():
            result = map_market_function[exchange]()
        else:
            result_for_response[exchange] = {"symbols":"", "status":"ko", "reason":"unknown market"}
            continue

        if isinstance(result, pd.DataFrame) == True:
            symbols = result["symbol"].to_list()
        else:
            symbols = result
        current_result = {}
        current_result["symbols"] = ','.join(symbols)
        current_result["status"] = "ok"

        result_for_response[exchange] = current_result

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response

def api_symbol(str_screener, str_exchange, str_symbols):
    if str_symbols == None:
        return {"result":{}, "status":"ko", "reason":"no values", "elapsed_time":"0"}

    start = datetime.now()

    result_for_response = {}

    symbols = str_symbols.split(',')
    for symbol in symbols:
        if str_screener == "crypto":
            info = crypto.get_symbol_ticker(str_exchange, symbol.replace("_", "/"))
            symbol_info = {"status": "ok", "info": info}
        else:
            symbol_info = yf_wrapper.get_info(symbol)
        result_for_response[symbol] = symbol_info

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response

def api_history_parse_parameters(request):
    status = "ok"
    reason = ""
    str_exchange = ""
    str_symbol = ""
    str_start = ""
    str_end = None
    str_interval = "1d"
    length = 100
    indicators = {}
    if request.method == 'GET':
        str_exchange = request.args.get("exchange")
        str_symbol = request.args.get("symbol")
        str_start = request.args.get("start")
        str_end = request.args.get("end")
        str_interval = request.args.get("interval", "1d")
        length = request.args.get("length", 100)
        if length != None:
            length = int(length)
        indicators= request.args.get("indicators", {})
        if isinstance(indicators, str):
            indicatorsArray = indicators.split(',')
            indicators = dict.fromkeys(indicatorsArray)
    elif request.method == 'POST':
        if request.is_json:
            params = request.get_json()
            str_exchange = params.get("exchange", str_exchange)
            str_symbol = params.get("symbol", str_symbol)
            str_start = params.get("start", str_start)
            str_end = params.get("end", str_end)
            str_interval = params.get("interval", str_interval)
            length = params.get("length", length)
            indicators = params.get("indicators", indicators)
        else:
            if "exchange" in request.form:
                str_exchange = request.form['exchange']
            if "symbol" in request.form:
                str_symbol = request.form['symbol']
            if "start" in request.form:
                str_start = request.form['start']
            if "end" in request.form:
                str_end = request.form['end']
            if "interval" in request.form:
                str_interval = request.form["interval"]
            if "length" in request.form:
                length = request.form['length']
                length = int(length)
            if "indicators" in request.form:
                indicators = request.form["indicators"]
                print(type(indicators))
                indicators = json.loads(indicators)

    if str_exchange == None or str_exchange == "":
        status = False
        reason = "exchange not specified"
    elif str_symbol == None or str_symbol == "":
        reason = "symbol not specified"
    elif str_start == None or str_start == "":
        reason = "start not specified"

    if reason != "":
        status = "ko"

    if str_end == None:
        str_end = datetime.today().strftime('%Y-%m-%d')

    return {
        "status":status, "reason":reason,
        "str_exchange":str_exchange, "str_symbol":str_symbol,
        "str_start":str_start, "str_end":str_end, "str_interval":str_interval,
        "length":length, "indicators":indicators}

def api_history(history_params):
    str_exchange = history_params.get("str_exchange")
    str_symbol = history_params.get("str_symbol")
    str_start = history_params.get("str_start")
    str_end = history_params.get("str_end")
    str_interval = history_params.get("str_interval", "1d")
    length = history_params.get("length", None)
    indicators = history_params.get("indicators", {})

    start = datetime.now()

    result_for_response = {}

    symbols = str_symbol.split(',')
    real_symbols = [symbol.replace("_", "/") for symbol in symbols]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        get_symbol_ohlcv_fn = None
        if config.use_mock:
            get_symbol_ohlcv_fn = config.g_data.get_symbol_ohlcv
        else:
            get_symbol_ohlcv_fn = crypto.get_symbol_ohlcv
        futures = {executor.submit(get_symbol_ohlcv_fn, exchange_name=str_exchange, symbol=real_symbol, start=str_start, end=str_end, timeframe=str_interval, length=length, indicators=indicators): real_symbol for real_symbol in real_symbols}

        for future in concurrent.futures.as_completed(futures):
            real_symbol = futures[future]
            symbol = real_symbol.replace('/', '_')
            df = future.result()
            if isinstance(df, pd.DataFrame):
                df.reset_index(inplace=True)
                result_for_response[symbol] = {"status": "ok", "info": df.to_json()}
            else:
                result_for_response[symbol] = {"status": "ko", "reason": "", "info": df}
              
    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response

def api_recommendations(screener, exchange, str_symbols = None, interval = "1h"):
    result_for_response = {}
    result_for_response["result"] = {}
    result_for_response["parameters"] = {"screener": screener, "exchange": exchange, "symbols": str_symbols, "interval": interval}
    result_for_response["elapsed_time"] = "0"
    if screener == None or exchange == None:
        result_for_response["status"] = "ko"
        result_for_response["message"] = "missing parameter(s) among screener, exchange. all parameters are screener, exchange, symbols and interval"
        return result_for_response

    start = datetime.now()
    
    if str_symbols != None:
        # look for recommendations for the symbols provided as argument
        symbols = str_symbols.split(',')
        result_for_response = tradingview.get_recommendations_from_list(screener, exchange, symbols, interval)
    else:
        # look for recommendations for all the symbols managed by the exchange
        if exchange in map_market_function.keys():
            symbols = map_market_function[exchange]()
            symbols = [symbol.replace("/", "") for symbol in symbols]
            result_for_response = tradingview.get_recommendations_from_list(screener, exchange, symbols, interval)
        else:
            result_for_response = {"symbols":"", "status":"ko", "message":"unknown exchange"}

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response

def api_portfolio(exchange_name="binance", recommendations=["BUY", "STRONG_BUY"], intervals=["15m", "30m", "1h"]):
    start = datetime.now()

 
    symbols = portfolio.get_portfolio(exchange_name, recommendations, intervals)
    result_for_response = {"symbols":symbols.to_json(), "status":"ok"}

    end = datetime.now()
    elapsed_time = str(end - start)

    final_response = {
        "result":result_for_response,
        "status":"ok",
        "elapsed_time":elapsed_time
    }

    return final_response
