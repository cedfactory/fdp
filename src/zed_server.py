import zmq
import pandas as pd
import json
import sys
import utils
# from ws_global import ws_candle_start
import bitget_ws_candle

class ZMQServer:
    def __init__(self, config_path: str):
        self.params = self._load_config(config_path)
        self.ws_candle = self._start_cancle(self.params)


        self.address = self.params.get("bind_address", "tcp://127.0.0.1:5555")

        """
        data_file = self.config.get("data_file")

        if data_file:
            self.df = pd.read_csv(data_file, parse_dates=True, index_col=0)
        else:
            self.df = pd.DataFrame()
        """

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.address)
        print(f"[SERVER] Listening on {self.address}")

    def _load_config(self, conf_param: str) -> dict:
        if conf_param == "":
            conf_param = "./conf/fdp_conf_lst_data_description.xml"
        params = utils.xml_to_list(conf_param)
        return params

    def _start_cancle(self, params):
        ws_candle = bitget_ws_candle.WSCandle(params=params)
        return ws_candle

    def _handle_request(self, message: dict) -> dict:
        cmd = message.get("command")
        if cmd == "get_status":
            return {"status": "ok"}

        if cmd == "get_data":
            # Expecting parameters: symbol, timeframe, length, last_tick
            symbol = message.get("symbol")
            timeframe = message.get("timeframe")  # for future use
            length = message.get("length")
            last_tick = message.get("last_tick")

            # Validate inputs
            if not all([symbol, length is not None, last_tick]):
                return {"error": "Missing one of symbol, length, or last_tick"}
            try:
                length = int(length)
                last_dt = pd.to_datetime(last_tick)
            except Exception as e:
                return {"error": f"Invalid parameter: {e}"}

            # Filter by symbol
            df_sym = self.df
            if "symbol" in df_sym.columns:
                df_sym = df_sym[df_sym["symbol"] == symbol]
            # Filter by last_tick
            df_sym = df_sym[df_sym.index <= last_dt]
            # Return the last `length` rows
            sliced = df_sym.tail(length)

            return {"data": sliced.to_json(orient="split")}

        return {"error": f"Unknown command '{cmd}'"}

    def serve_forever(self):
        try:
            while True:
                msg = self.socket.recv_json()
                response = self._handle_request(msg)
                self.socket.send_json(response)
        except KeyboardInterrupt:
            print("[SERVER] Shutting down...")
        finally:
            self.socket.close()
            self.context.term()