from . import bitget_ws
import json
import pandas as pd
from datetime import datetime

class FDPWSAccountTickers:

    def __init__(self, params = None):
        self.client_account = None
        self.client_tickers = None
        self.id = None

        if not params:
            return

        self.id = params.get("id", self.id)
        api_key = params.get("api_key", None)
        api_secret = params.get("api_secret", None)
        api_passphrase = params.get("api_passphrase", None)
        if not api_key or not api_secret or not api_passphrase:
            return

        self.client_account = bitget_ws.BitgetWsClient(
            api_key = api_key,
            api_secret = api_secret,
            passphrase = api_passphrase,
            ws_url = bitget_ws.CONTRACT_WS_URL_PRIVATE,
            verbose=True) \
            .error_listener(bitget_ws.handel_error) \
            .build()

        self.client_tickers = bitget_ws.BitgetWsClient(
            ws_url=bitget_ws.CONTRACT_WS_URL_PUBLIC,
            verbose=True) \
            .error_listener(bitget_ws.handel_error) \
            .build()

        self.lst_tickers = params.get("tickers", [])
        self.verbose = True
        self.state = {
            "ticker_prices": {},
            "positions": None,
            "orders": None,
            "orders-algo": None,
            "account": {
                "marginCoin": None,
                "available": None,
                "maxOpenPosAvailable": None,
                "usdtEquity": None
            },
        }

        channels = [
            bitget_ws.SubscribeReqCoin("USDT-FUTURES", "account", "default"),
            bitget_ws.SubscribeReq("USDT-FUTURES", "positions", "default"),
            bitget_ws.SubscribeReq("USDT-FUTURES", "orders", "default"),
            bitget_ws.SubscribeReq("USDT-FUTURES", "orders-algo", "default"),
        ]

        def on_message_account(message):
            print(">> ACCOUNT >>", message)
            if "event" in json.loads(message) and "arg" in json.loads(message):
                if self.verbose:
                    print(message)
                pass
            elif "data" in json.loads(message):
                data = json.loads(message)["data"]
                arg = json.loads(message)["arg"]

                if data and isinstance(arg, dict) and arg["channel"] == "account":
                    data = data[0]
                    if self.verbose:
                        print("marginCoin: ", data['marginCoin'],
                              " available: ", data['available'],
                              " maxOpenPosAvailable: ", data['maxOpenPosAvailable'],
                              " usdtEquity: ", data['usdtEquity']
                              )
                    self.state["account"]["marginCoin"] = data['marginCoin']
                    self.state["account"]["available"] = data['available']
                    self.state["account"]["maxOpenPosAvailable"] = data['maxOpenPosAvailable']
                    self.state["account"]["usdtEquity"] = data['usdtEquity']

                elif data and isinstance(arg, dict) and arg["channel"] == "positions":   # CEDE TEST LST OF DCT POSITIONS
                    self.state["positions"] = pd.DataFrame(data)
                    if self.verbose:
                        print(self.state["positions"].to_string(index=False))

                elif data and isinstance(arg, dict) and arg["channel"] == "orders":
                    self.state["orders"] = pd.DataFrame(data)
                    if self.verbose:
                        print(self.state["orders"].to_string(index=False))

                elif data and isinstance(arg, dict) and arg["channel"] == "orders-algo":
                    self.state["orders-algo"] = pd.DataFrame(data)
                    if self.verbose:
                        print(self.state["orders-algo"].to_string(index=False))

                else:
                    try:
                        if isinstance(arg, dict) \
                                and arg["channel"] != "account" \
                                and arg["channel"] != "positions" \
                                and arg["channel"] != "orders" \
                                and arg["channel"] != "orders-algo":
                            print("Received:", message)
                    except:
                        print("Received nok:", message)

        self.client_account.subscribe(channels, on_message_account) # TORESTORE

        # Tickers
        def on_message_ticker(message):
            print(">> TICKER >>", message)
            if "event" in json.loads(message) and "arg" in json.loads(message):
                print(message)
                pass
            elif "data" in json.loads(message) and "arg" in json.loads(message):
                data = json.loads(message)["data"]
                arg = json.loads(message)["arg"]

                if data and isinstance(arg, dict) and arg["channel"] == "ticker":
                    lst_data = json.loads(message)["data"]
                    if lst_data[0]['instId'] in self.lst_tickers:
                        self.state["ticker_prices"][lst_data[0]['instId']] = {
                            "timestamp": datetime.timestamp(datetime.now()),
                            "symbols": lst_data[0]['instId'],
                            "values": lst_data[0]['lastPr']
                        }

                elif json.loads(message)["arg"]["channel"] != "ticker":
                    print("Received:", message)

        for symbol in self.lst_tickers:
            channels = [bitget_ws.SubscribeReq("USDT-FUTURES", "candle1m", symbol)]
            self.client_tickers.subscribe(channels, on_message_ticker)

    def stop(self):
        self.client_account.close()
        self.client_tickers.close()

    def __del__(self):
        print("destructor")
        #self.client.close()

    def get_state(self):
        return self.state
