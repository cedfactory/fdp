from abc import ABCMeta
import requests
import json
from collections import deque
import time
import threading
from . import fdp
import pandas as pd


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
    def __init__(self, fdp_id, fdp_source):
        self.id = fdp_id
        self.source = fdp_source
        if fdp_source.startswith("FDP"):
            exchange_name = "bitget"  # default exchange
            if fdp_source.startswith("FDP:"):
                exchange_name = fdp_source.split(":")[1]
            self.source = fdp.FDP({"exchange_name": exchange_name})

        self.call_times = deque()  # Store timestamps for the last calls
        self.lock = threading.Lock()

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

    def request(self, service, params):
        result = {}
        if isinstance(self.source, str):
            symbols = params.get("symbol", None)

            response_json = url_request_post(self.source + '/' + service, params)

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

        else:
            if service == "last":
                symbol = params.get("symbol", None)
                start = params.get("start", None)
                end = params.get("end", None)
                timeframe = params.get("timeframe", "1d")
                features = params.get("indicators", None)
                candle_stick = params.get("candle_stick", "released")
                response_json = self.source.get_symbol_ohlcv_last(symbol, start, end, timeframe, features, candle_stick)

        return result

class FDPManager:
    def __init__(self, params=None):
        self.lstSources = []
        if params:
            fdps_params = params.get("fdps", [])
            for fdp_params in fdps_params:
                fdp_id = fdp_params.get("id", None)
                fdp_source = fdp_params.get("src", None)
                if not fdp_id or not fdp_source:
                    continue

                o_fdp_source = FDPSource(fdp_id, fdp_source)
                self.lstSources.append(o_fdp_source)

    def request(self, service, params):
        result = None

        result_done = False
        while not result_done:
            for source in self.lstSources:
                if source.can_request():
                    result = source.request(service, params)
                    result_done = True
                    break
            time.sleep(.5)

        return result
