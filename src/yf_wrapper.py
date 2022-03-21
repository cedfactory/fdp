import time
import yfinance as yf
from inspect import getframeinfo, stack

def print_exception_info(exception):
    caller = getframeinfo(stack()[2][0])
    print("[{}:{}] - {}".format(caller.filename, caller.lineno, exception))

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
        print_exception_info(e)
    try:
        info["industry"] = yf_value.info['industry']
    except BaseException as e:
        print_exception_info(e)
        pass
    try:
        info["sector"] = yf_value.info['sector']
    except BaseException as e:
        print_exception_info(e)
        pass
    try:
        info["short_name"] = yf_value.info['shortName']
    except BaseException as e:
        print_exception_info(e)
        pass
    try:
        info["country"] = yf_value.info['country']
    except BaseException as e:
        print_exception_info(e)
        pass
    try:
        info["exchange"] = yf_value.info['exchange']
    except BaseException as e:
        print_exception_info(e)
        pass    

    return {"status":"ok", "info":info}
