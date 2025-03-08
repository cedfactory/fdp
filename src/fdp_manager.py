import time
from . import fdp

class FDPManager:
    def __init__(self, sources=None):
        self.lstSources = []
        if sources:
            for source_params in sources:
                if not source_params:
                    continue

                source_type = source_params.get("type", None)
                if source_type == "ccxt":
                    source = fdp.FDPCCXT(source_params)
                elif source_type == "url":
                    source = fdp.FDPURL(source_params)
                elif source_type == "ws":
                    source = None
                elif source_type == "api":
                    source = None
                if source:
                    self.lstSources.append(source)

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
