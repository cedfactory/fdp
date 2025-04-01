import threading
from . import utils
from . import bitget_ws_candle

ws_candle = None
_lock = threading.Lock()

def ws_candle_start(conf_param=""):
    global ws_candle

    with _lock:
        if ws_candle is not None:
            return ws_candle

        if conf_param == "":
            conf_param = "./conf/fdp_conf_lst_data_description.xml"

        params = utils.xml_to_list(conf_param)
        ws_candle = bitget_ws_candle.WSCandle(params=params)
        return ws_candle

def ws_candle_stop():
    global ws_candle

    with _lock:
        if ws_candle:
            ws_candle.stop()
            ws_candle = None
