from src import bitget_ws_client
import json
import pandas as pd
from collections import defaultdict
from src import utils

from src import bitget_ws_candle_data

import time

class WSCandle:

    def __init__(self, params=None):
        self.id = None
        self.status = "Off"

        groups = defaultdict(list)
        for entry in params:
            groups[entry['symbol']].append(entry)

        lst_params = list(groups.values())

        self.dct_candle_data = {}
        for group in lst_params:
            symbol = group[0]['symbol']
            candle_data = bitget_ws_candle_data.WSCandleData(group)
            self.dct_candle_data[symbol] = candle_data

        try:
            self.client = bitget_ws_client.BitgetWsClient(
                ws_url=bitget_ws_client.CONTRACT_WS_URL_PUBLIC,
                verbose=True) \
                .error_listener(bitget_ws_client.handel_error) \
                .build()
        except Exception as e:
            print("constructor: ", e)


        """
        timeframe_map = {
            "1m": "candle1m",
            "5m": "candle5m",
            "15m": "candle15m",
            "30m": "candle30m",
            "1h": "candle1H",
            "4h": "candle4H",
        }
        """
        self.timeframe_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1H",
            "4h": "4H",
            "12h": "4H",
            "1d": "1D",
        }
        self.reverse_timeframe_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1H": "1h",
            "4H": "4h",
            "12H": "4h",
            "1D": "1d",
        }

        channels = [
            bitget_ws_client.SubscribeReq(
                "USDT-FUTURES",
                f"candle{self.timeframe_map.get(d['timeframe'], d['timeframe'])}",
                f"{d['symbol']}USDT"
            )
            for d in params
        ]

        # 2) Build your list of channels
        self.lst_channels = [
            {
                "inst_type": "USDT-FUTURES",
                "channel": f"candle{self.timeframe_map.get(item['timeframe'], item['timeframe'])}",
                "inst_id": f"{item['symbol']}USDT"
            }
            for item in params
        ]

        def on_message(message):
            json_obj = json.loads(message)
            action = str(json_obj.get('action')).replace("\'", "\"")

            timestamp_ms = json_obj["ts"]
            timestamp_sec = timestamp_ms / 1000
            current_time_sec = time.time()
            time_difference = current_time_sec - timestamp_sec
            if time_difference < 5:
                if action == "snapshot" or action == 'update':
                    arg = json_obj.get('arg')
                    if arg['instType'] == 'USDT-FUTURES' \
                            and arg['channel'].startswith("candle"):
                        symbol = arg['instId']
                        timeframe = arg['channel'].replace("candle", "", 1)
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
                            ms_array = pd.to_numeric(df['timestamp'], errors='raise') \
                                .astype('int64') \
                                .values \
                                .astype('datetime64[ms]')

                            # 2) Build a timezone-aware UTC index from that
                            df.index = pd.DatetimeIndex(ms_array, tz='UTC')
                            self.dct_candle_data[symbol.removesuffix("USDT")].set_value(symbol,
                                                                                        self.reverse_timeframe_map.get(timeframe),
                                                                                        df)

                    else:
                        exit(73492)
                else:
                    exit(7392)


        self.client.subscribe(channels, on_message)

        lst_subscribed_candle_channels = self.client.get_subscribed_channels()
        if utils.dict_lists_equal(lst_subscribed_candle_channels,
                                  self.lst_channels):
            self.status = "On"
        else:
            self.status = "Failed"

    def stop(self):
        self.client.close()

    def __del__(self):
        print("destructor")
        self.client.close()

    def request(self, service, params=None):
        # if service == "last":
        #     return self.df
        return None

    def get_ohlcv(self, symbol_key, timeframe, length):
        return self.dct_candle_data[symbol_key.split("/")[0]].get_ohlcv(symbol_key.replace("/", ""), timeframe, length)

    def update_ohlcv_from_api(self, symbol_key, timeframe, df_api_ohlv):
        self.dct_candle_data[symbol_key.split("/")[0]].update_ohlcv_from_api(symbol_key.replace("/", ""), timeframe, df_api_ohlv)