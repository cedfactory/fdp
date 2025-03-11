from . import bitget_ws
import json
import pandas as pd

class FDPWSTicker:

    def __init__(self, params=None):
        self.id = None
        self.df = None

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
                self.df = pd.DataFrame(candle_data,
                                  columns=["timestamp", "open", "high", "low", "close", "volume", "volume_2", "volume_3"])
                self.df = self.df.drop(columns=['volume_2', 'volume_3'])
                self.df = self.df.rename(columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
                cols = ["open", "high", "low", "close", "volume"]
                self.df[cols] = self.df[cols].astype(float)
                if not self.df.empty:
                    self.df = self.df.set_index(self.df['timestamp'])
                    self.df.index = self.df.index.str.replace(r'0{3}$', '', regex=True)
                    self.df.index = pd.to_datetime(self.df.index.astype(int), unit='s', utc=True, errors='coerce')

            elif action == "update":
                data = json_obj.get('data')
                print(data)

            #print(">>>>>", message)
            # client.unsubscribe(channels)

        self.client.subscribe(channels, on_message)

    def stop(self):
        self.client.close()

    def __del__(self):
        print("destructor")
        self.client.close()

    def request(self, service, params=None):
        if service == "last":
            return self.df
        return None

