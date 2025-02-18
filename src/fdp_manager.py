from abc import ABCMeta
import requests
import json
from . import fdp


def url_request_post(url, params):
    if not url or url == "":
        return {"status": "ko", "info": "url not found"}

    final_result = {}

    n_attempts = 3
    while n_attempts > 0:
        try:
            # response = requests.post(fdp_url+'/'+url, json=params)
            with requests.post(url, json=params) as response:
                pass
            response.close()
            if response.status_code == 200:
                response_json = json.loads(response.text)
                final_result["status"] = "ok"
                final_result["elapsed_time"] = response_json["elapsed_time"]
                final_result["result"] = response_json["result"]
                break
        except:
            reason = "exception when requesting POST {}".format(url)
            final_result = {"status": "ko", "info": reason}
            n_attempts = n_attempts - 1
            print('FDP ERROR : ', reason)

    return final_result


class FDPManager(metaclass=ABCMeta):
    def __init__(self, params=None):
        self.sources = {}
        if params:
            fdps_params = params.get("fdps", [])
            for fdp_params in fdps_params:
                fdp_id = fdp_params.get("id", None)
                src = fdp_params.get("src", None)
                if not fdp_id or not src:
                    continue
                if src == "FDP":
                    src = fdp.FDP({"exchange_name": "bitget"})

                self.sources[fdp_id] = src


    def request(self, id, service, params):
        if not id in self.sources:
            return None

        result = None
        source = self.sources[id]
        if isinstance(source, str):
            result = url_request_post(source + '/' + service, params)
        else:
            if service == "last":
                symbol = params.get("symbol", None)
                start = params.get("start", None)
                end = params.get("end", None)
                timeframe = params.get("timeframe", "1d")
                indicators = params.get("indicators", None)
                candle_stick = params.get("candle_stick", "released")
                result = source.get_symbol_ohlcv_last(symbol, start, end, timeframe, indicators, candle_stick)

        return result
