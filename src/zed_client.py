import zmq
import pandas as pd
import json
import sys

class ZMQClient:
    def __init__(self, address: str):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        print(f"[CLIENT] Connected to {address}")

    def get_status(self) -> dict:
        self.socket.send_json({"command": "get_status"})
        return self.socket.recv_json()

    def get_data(self, symbol: str, timeframe: str, length: int, last_tick: str) -> pd.DataFrame:
        cmd = {
            "command": "get_data",
            "symbol": symbol,
            "timeframe": timeframe,
            "length": length,
            "last_tick": last_tick
        }
        self.socket.send_json(cmd)
        resp = self.socket.recv_json()
        if "data" in resp:
            return pd.read_json(resp["data"], orient="split")
        raise RuntimeError(resp.get("error", "Unknown error"))

    def close(self):
        self.socket.close()
        self.context.term()

