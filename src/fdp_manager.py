import time
from . import fdp
from . import bitget_ws_candle

class FDPManager:
    def __init__(self, fdp_data=None):
        sources = fdp_data["fdp_sources"]
        self.lstSources = []
        if sources:
            for source_params in sources:
                if not source_params:
                    continue

                source = None
                source_type = source_params.get("type", None)
                if source_type == "ccxt":
                    source = fdp.FDPCCXT(source_params)
                elif source_type == "url":
                    source = fdp.FDPURL(source_params)
                elif source_type == "ws_candle":
                    source = bitget_ws_candle.WSCandle(source_params, fdp_data["ws_data_description"])
                elif source_type == "api":
                    source = None
                if source:
                    self.lstSources.append(source)

    def stop(self):
        for source in self.lstSources:
            if source.__class__.__name__ in ["FDPWSTicker", "FDPWSPositions"]:
                if callable(getattr(source, "stop", None)):
                    source.stop()
                else:
                    print("!!! Warning : {} needs to be closed".format(source.__class__.__name__))

    def request(self, service, params, ws_id=None):
        result = None

        if ws_id:
            for source in self.lstSources:
                if source.id == ws_id:
                    result = source.request(service, params)
                    return result

        result_done = False
        while not result_done:
            for source in self.lstSources:
                if source.can_request():
                    result = source.request(service, params)
                    result_done = True
                    break
            time.sleep(.5)

        return result
