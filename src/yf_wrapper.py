import time
import yfinance as yf
from . import utils

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
        utils.print_exception_info(e)
        raise e
    try:
        info["industry"] = yf_value.info['industry']
    except BaseException as e:
        utils.print_exception_info(e)
        raise e
    try:
        info["sector"] = yf_value.info['sector']
    except BaseException as e:
        utils.print_exception_info(e)
        raise e
    try:
        info["short_name"] = yf_value.info['shortName']
    except BaseException as e:
        utils.print_exception_info(e)
        raise e
    try:
        info["country"] = yf_value.info['country']
    except BaseException as e:
        utils.print_exception_info(e)
        raise e
    try:
        info["exchange"] = yf_value.info['exchange']
    except BaseException as e:
        utils.print_exception_info(e)
        raise e 

    return {"status":"ok", "info":info}
