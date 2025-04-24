import threading
from . import utils
from . import bitget_ws_candle

ws_candle = None
_lock = threading.Lock()

ws_global_traces = None
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

def ws_traces_start():
    global ws_global_traces

    if ws_global_traces is not None:
        return

    ws_global_traces = utils.traces_cpt()

def ws_traces_increment_success():
    global ws_global_traces

    with _cpt_lock:
        ws_global_traces.increment_success()

def ws_traces_increment_failure(is_not_none=False, is_dataframe=False, limit=False, tick_in=False):
    global ws_global_traces

    with _cpt_lock:
        ws_global_traces.increment_failure(is_not_none=is_not_none,
                                           is_dataframe=is_dataframe,
                                           limit=limit,
                                           tick_in=tick_in)

def ws_traces_get_status():
    global ws_global_traces

    with _cpt_lock:
        return ws_global_traces.get_status()