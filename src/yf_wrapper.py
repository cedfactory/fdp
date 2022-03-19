import time
import yfinance as yf

def get_info(value):
    if value == None:
        return {"status":"ko", "reason":"no value"}

    yf_value = yf.Ticker(value)
    time.sleep(3)

    info = {}
    info["symbol"] = value
    try:
        info["isin"] = yf_value.isin
    except BaseException as e:
        info["isin"] = '-'
    try:
        info["industry"] = yf_value.info['industry']
    except BaseException as e:
        pass
    try:
        info["sector"] = yf_value.info['sector']
    except BaseException as e:
        pass
    try:
        info["short_name"] = yf_value.info['shortName']
    except BaseException as e:
        pass
    try:
        info["country"] = yf_value.info['country']
    except BaseException as e:
        pass
    try:
        info["exchange"] = yf_value.info['exchange']
    except BaseException as e:
        pass    

    return {"status":"ok", "info":info}