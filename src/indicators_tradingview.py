from tradingview_ta import TA_Handler, Interval, Exchange
import pandas as pd

from time import sleep

class Interval:
    INTERVAL_1_MINUTE = "1m"
    INTERVAL_5_MINUTES = "5m"
    INTERVAL_15_MINUTES = "15m"
    INTERVAL_30_MINUTES = "30m"
    INTERVAL_1_HOUR = "1h"
    INTERVAL_2_HOURS = "2h"
    INTERVAL_4_HOURS = "4h"
    INTERVAL_1_DAY = "1d"
    INTERVAL_1_WEEK = "1W"
    INTERVAL_1_MONTH = "1M"

tv_indicators = {
    "tv_1m" : Interval.INTERVAL_1_MINUTE,
    "tv_5m" : Interval.INTERVAL_5_MINUTES,
    "tv_15m" : Interval.INTERVAL_15_MINUTES,
    "tv_30m" : Interval.INTERVAL_30_MINUTES,
    "tv_1h" : Interval.INTERVAL_1_HOUR,
    "tv_2h" : Interval.INTERVAL_2_HOURS,
    "tv_4h" : Interval.INTERVAL_4_HOURS,
    "tv_1d" : Interval.INTERVAL_1_DAY,
    "tv_1W" : Interval.INTERVAL_1_WEEK,
    "tv_1M" : Interval.INTERVAL_1_MONTH
}

def get_recommendation(df, indicator, params):
    symbol = ""
    exchange = "FTX" # default
    if params:
        symbol = params.get("symbol", symbol)
        symbol = symbol.replace('/', '')
        exchange = params.get("exchange", exchange)

    handler = TA_Handler()
    handler.set_symbol_as(symbol)
    handler.set_exchange_as_crypto_or_stock(exchange)
    handler.set_screener_as_crypto()

    interval = tv_indicators[indicator]

    try_cpt = 0
    while True:
        try:
            handler.set_interval_as(interval)
            tv_recommendation = handler.get_analysis().summary["RECOMMENDATION"]
            return tv_recommendation
        except:
            sleep(1)
            try_cpt = try_cpt + 1
            if cpt == 3:
                print('no recommention for: ', symbol, ' interval: ', interval)
                tv_recommendation = "FAILED"
                return tv_recommendation