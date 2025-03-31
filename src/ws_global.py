from . import utils
from . import bitget_ws_candle

conf_param = "./conf/fdp_conf_lst_data_description.xml"
params = utils.xml_to_list(conf_param)
ws_candle = bitget_ws_candle.WSCandle(params=params)

def ws_candle_start(conf_param=""):
    global ws_candle
    if ws_candle:
        ws_candle.stop()
        ws_candle = None

    if conf_param == "":
        conf_param = "./conf/fdp_conf_lst_data_description.xml"
    params = utils.xml_to_list(conf_param)
    ws_candle = bitget_ws_candle.WSCandle(params=params)

def ws_candle_stop():
    global ws_candle
    if ws_candle:
        ws_candle.stop()
        ws_candle = None
