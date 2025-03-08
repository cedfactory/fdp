import asyncio, json, hmac, hashlib, base64, time
import websockets
import pandas as pd

API_KEY = "YOUR_API_KEY"
PASSPHRASE = "YOUR_API_PASSPHRASE"
SECRET_KEY = "YOUR_API_SECRET"

async def subscribe_account_balance():
    uri = "wss://ws.bitget.com/v2/ws/private"
    lst_ticker = ["BTCUSDT", "ETHUSDT", "XRPUSDT"]
    async with websockets.connect(uri) as websocket:
        # Prepare login message with API credentials
        timestamp = str(int(time.time()))
        message = timestamp + "GET" + "/user/verify"
        signature = base64.b64encode(hmac.new(
            SECRET_KEY.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()).decode('utf-8')
        login_req = {
            "op": "login",
            "args": [{
                "apiKey": API_KEY,
                "passphrase": PASSPHRASE,
                "timestamp": timestamp,
                "sign": signature
            }]
        }
        # Send login request and wait for success
        await websocket.send(json.dumps(login_req))
        response = await websocket.recv()
        print("Auth response:", response)
        # (You should parse response and check for login success code here)
        # Now subscribe to the account balance channel for all coins (spot)
        sub_req = {
            "op": "subscribe",
            "args": [{
                "instType": "USDT-FUTURES",
                "channel": "account",
                "coin": "default"
            }]
        }
        await websocket.send(json.dumps(sub_req))

        sub_req = {
            "op": "subscribe",
            "args": [{
                "instType": "USDT-FUTURES",
                "channel": "positions",
                "coin": "default"
            }]
        }
        await websocket.send(json.dumps(sub_req))

        # Listen for balance updates
        while True:
            message = await websocket.recv()
            try:
                data = json.loads(message)["data"][0]
                print("marginCoin: ", data['marginCoin'],
                      " available: ", data['available'],
                      " maxOpenPosAvailable: ", data['maxOpenPosAvailable'],
                      " usdtEquity: ", data['usdtEquity']
                      )
            except:
                try:
                    data = json.loads(message)["data"]
                    # Convert the list of dictionaries to a DataFrame
                    df = pd.DataFrame(data)

                    # Print the DataFrame as a string (without the index if you prefer)
                    print(df.to_string(index=False))
                except:
                    print("Received:", message)

# Run the coroutine
asyncio.run(subscribe_account_balance())
