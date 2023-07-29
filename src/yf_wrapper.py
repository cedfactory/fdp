import time
import yfinance as yf

def get_info(value):
    if value == None:
        return {"status":"ko", "reason":"no value"}

    yf_value = yf.Ticker(value)
    time.sleep(3)

    info = {}
    info["symbol"] = value
    info["isin"] = yf_value.info.get("isin", "")
    info["industry"] = yf_value.info.get("industry", "")
    info["sector"] = yf_value.info.get("sector", "")
    info["shortName"] = yf_value.info.get("shortName", "")
    info["country"] = yf_value.info.get("country", "")
    info["exchange"] = yf_value.info.get("exchange", "")

    return {"status": "ok", "info": info}
