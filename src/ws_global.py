import threading
from . import utils
from . import bitget_ws_candle

ws_candle = None
_lock = threading.Lock()

ws_global_cpt = None
_cpt_lock = threading.Lock()

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

def ws_cpt_start():
    global ws_global_cpt

    if ws_global_cpt is not None:
        return

    ws_global_cpt = utils.debug_cpt()

def ws_cpt_increment_success():
    global ws_global_cpt

    with _cpt_lock:
        ws_global_cpt.increment_success()

def ws_cpt_increment_failure():
    global ws_global_cpt

    with _cpt_lock:
        ws_global_cpt.increment_failure()