import utils
import bitget_ws_candle

conf_param = "./conf/fdp_conf_lst_data_description.xml"
params = utils.xml_to_list(conf_param)
ws_candle = bitget_ws_candle.WSCandle(params=params)