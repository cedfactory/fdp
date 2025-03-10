import time
from . import bitget_ws
import json
import pandas as pd

g_df = None
class FDPWSTicker:

    def __init__(self, params=None):
        self.id = None

        if params:
            self.id = params.get("id", self.id)

        self.client = bitget_ws.BitgetWsClient(
            ws_url=bitget_ws.CONTRACT_WS_URL_PUBLIC,
            verbose=True) \
            .error_listener(bitget_ws.handel_error) \
            .build()

        channels = [bitget_ws.SubscribeReq("USDT-FUTURES", "candle1m", "BTCUSDT")]

        def on_message(message):
            json_obj = json.loads(message)
            action = str(json_obj.get('action')).replace("\'", "\"")
            if action == "snapshot":
                data = json_obj.get('data')
                print(data)
                candle_data = json_obj.get("data", [])
                # Assuming each candle is in the format:
                # [timestamp, open, high, low, close, volume]
                df = pd.DataFrame(candle_data,
                                  columns=["timestamp", "open", "high", "low", "close", "volume", "volume_2", "volume_3"])
                df = df.drop(columns=['volume_2', 'volume_3'])
                df = df.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
                cols = ["open", "high", "low", "close", "volume"]
                df[cols] = df[cols].astype(float)
                if not df.empty:
                    df = df.set_index(df['timestamp'])
                    df.index = df.index.str.replace(r'0{3}$', '', regex=True)
                    df.index = pd.to_datetime(df.index.astype(int), unit='s', utc=True, errors='coerce')
                global g_df
                g_df = df

            elif action == "update":
                data = json_obj.get('data')
                print(data)

            #print(">>>>>", message)
            # client.unsubscribe(channels)

        self.client.subscribe(channels, on_message)

    def __del__(self):
        print("destructor")
        self.client.close()

    def request(self, service, params=None):
        if service == "last":
            return g_df
        return None

