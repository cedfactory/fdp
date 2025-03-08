from abc import ABC, abstractmethod
import pandas as pd
import requests
import threading
import time
from collections import deque
import json
from . import crypto

def url_request_post(url, params):
    if not url or url == "":
        return {"status": "ko", "info": "url not found"}

    result = {}

    n_attempts = 3
    while n_attempts > 0:
        try:
            # response = requests.post(fdp_url+'/'+url, json=params)
            with requests.post(url, json=params) as response:
                pass
            response.close()
            if response.status_code == 200:
                response_json = json.loads(response.text)
                result["status"] = "ok"
                result["elapsed_time"] = response_json["elapsed_time"]
                result["result"] = response_json["result"]
                break
        except:
            reason = "exception when requesting POST {}".format(url)
            result = {"status": "ko", "info": reason}
            n_attempts = n_attempts - 1
            print('FDP ERROR : ', reason)

    return result


class FDPSource:
    def __init__(self, params=None):
        self.call_times = deque()  # Store timestamps for the last calls
        self.lock = threading.Lock()
        self.id = ""
        if params:
            self.id = params.get("id", self.id)

    def can_request(self):
        now = time.time()

        with self.lock:
            # remove calls from more than 1 second
            while self.call_times and self.call_times[0] < now - 1:
                self.call_times.popleft()

            # check if this source can be called
            if len(self.call_times) < 10:
                print("Request managed by {} ({})".format(self.id, len(self.call_times)))
                self.call_times.append(now)
                return True

        return False

    @abstractmethod
    def request(self, method, params = None):
        pass


class FDPURL(FDPSource):

    def __init__(self, params=None):
        super().__init__()
        self.url = params.get("url", "")

    def request(self, method, params = None):
        symbols = params.get("symbol", None)

        response_json = url_request_post(self.url + '/' + method, params)

        features = {}  # get the features from params ?

        data = {feature: [] for feature in features}
        data["symbol"] = []

        if response_json["status"] == "ok":
            for symbol in symbols.split(","):
                formatted_symbol = symbol.replace('/', '_')
                if response_json["result"][formatted_symbol]["status"] == "ko":
                    print("[RealTimeDataProvider:get_current_data] !!!! no data for ", symbol)
                    continue
                df = pd.read_json(response_json["result"][formatted_symbol]["info"])
                columns = list(df.columns)
                data["symbol"].append(symbol)
                for feature in features:
                    if feature not in columns:
                        print("FDP MISSING FEATURE COLUMN")
                        return None
                    if len(df[feature]) > 0:
                        data[feature].append(df[feature].iloc[-1])
                    else:
                        print("FDP MISSING FEATURE VALUE")
                        return None

        result = pd.DataFrame(data)
        result.set_index("symbol", inplace=True)


class FDPCCXT(FDPSource):

    def __init__(self, params=None):
        super().__init__()
        self.exchange_name = params.get("exchange", "")
        self.exchange = None
        self.markets = None

        if self.exchange_name in ["bitget", "binance", "kraken", "hitbtc", "bitmex", "coinbase"]:
            self.exchange, self.markets = crypto.get_exchange_and_markets(self.exchange_name)
        else:
            print("Unknown exchange : {}", self.exchange_name)

    def get_symbol_ohlcv(self, symbol, start, end=None, timeframe="1d", length = None, indicators = {}):
        return crypto.get_symbol_ohlcv(self.exchange_name, symbol, start, end, timeframe, length, indicators, self.exchange)

    def get_symbol_ohlcv_last(self, symbol, start=None, end=None, timeframe="1h", indicators=None, candle_stick="released"):
        if indicators is None:
            indicators = {}
            window_size = 100 # CEDE DEFAULT
        else:
            window_size = list(indicators.values())[0]["window_size"]
        return crypto.get_symbol_ohlcv_last(
            self.exchange_name,
            symbol,
            start, end, timeframe, window_size,
            indicators, exchange=self.exchange,
            candle_stick=candle_stick)

    def request(self, method, params = None):
        result = None
        if method == "last":
            symbol = params.get("symbol", None)
            start = params.get("start", None)
            end = params.get("end", None)
            timeframe = params.get("interval", "1h")
            features = params.get("indicators", None)
            candle_stick = params.get("candle_stick", "released")
            result = self.get_symbol_ohlcv_last(symbol, start, end, timeframe, features, candle_stick)

        return result