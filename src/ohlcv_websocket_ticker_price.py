import asyncio, json
import websockets  # install with: pip install websockets

# USING V2 API & entry point
# https://www.bitget.com/api-doc/spot/websocket/public/Tickers-Channel#:~:text=action%20String%20Push%20data%20action%3A,trading%20volume%20in%20left%20coin
async def subscribe_ticker():
    uri = "wss://ws.bitget.com/v2/ws/public"
    lst_ticker = ["BTCUSDT", "ETHUSDT", "XRPUSDT"]
    async with websockets.connect(uri) as websocket:
        for symbol in lst_ticker:
            sub_req = {
                "op": "subscribe",
                "args": [{
                    "instType": "USDT-FUTURES",
                    "channel": "ticker",
                    "instId": symbol
                }]
            }
            await websocket.send(json.dumps(sub_req))
        # Await confirmation (subscribe event) and then continuously read data
        while True:
            message = await websocket.recv()
            try:
                lst_data = json.loads(message)["data"]
                for ticker in lst_ticker:
                    for data in lst_data:
                        if data['instId'] == ticker:
                            print("symbol: ", ticker, " - last price: ", data['lastPr'])
            except:
                print("Received:", message)

# USING V1 API & entry point
# https://bitgetlimited.github.io/apidoc/en/mix/#public-channels
async def subscribe_ticker_future():
    uri = "wss://ws.bitget.com/mix/v1/stream"
    lst_ticker = ["BTCUSDT", "ETHUSDT"]
    async with websockets.connect(uri) as websocket:
        for symbol in lst_ticker:
            sub_req = {
                "op": "subscribe",
                "args": [{
                    "instType": "mc",
                    "channel": "ticker",
                    "instId": symbol
                }]
            }
            await websocket.send(json.dumps(sub_req))
        # Await confirmation (subscribe event) and then continuously read data
        while True:
            message = await websocket.recv()
            # print("Received:", message)
            try:
                lst_data = json.loads(message)["data"]
                for ticker in lst_ticker:
                    for data in lst_data:
                        if data['instId'] == ticker:
                            print("symbol: ", ticker, " - last price: ", data['last'])
            except:
                pass


# Run the coroutine
asyncio.run(subscribe_ticker())
# asyncio.run(subscribe_ticker_future())
