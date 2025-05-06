import asyncio
import json
from collections import defaultdict

import pandas as pd
import websockets
from websockets.exceptions import ConnectionClosedError, WebSocketException

# ——————————————————————————————————————————————————————————————
# 1) CONFIGURATION
# ——————————————————————————————————————————————————————————————
# Contract (mix) public WebSocket URL for futures candlesticks
# :contentReference[oaicite:0]{index=0}
WS_URL    = "wss://ws.bitget.com/mix/v1/stream"
INST_TYPE = "USDT-FUTURES"          # USDT‑settled perpetuals
SYMBOLS   = ["BTCUSDT", "ETHUSDT"]  # add your symbols here
INTERVALS = ["1m", "5m"]            # and the timeframes you want

# ——————————————————————————————————————————————————————————————
# 2) STORAGE: nested dict for symbol → timeframe → DataFrame
# ——————————————————————————————————————————————————————————————
data: dict[str, dict[str, pd.DataFrame]] = defaultdict(lambda: {})

# ——————————————————————————————————————————————————————————————
# 3) CANDLE PROCESSOR
# ——————————————————————————————————————————————————————————————
def process_candle(msg: dict):
    arg         = msg["arg"]
    sym         = arg["instId"]
    channel     = arg["channel"]        # e.g. "candle1m"
    tf          = channel.replace("candle", "")
    raw_candles = msg.get("data", [])

    # lazy‑init the DataFrame
    if tf not in data[sym]:
        data[sym][tf] = pd.DataFrame(
            columns=["open", "high", "low", "close", "volume"],
            index=pd.DatetimeIndex([], name="timestamp"),
        )

    df = data[sym][tf]

    for c in raw_candles:
        ts, o, h, l, clo, vol = (
            int(c[0]), float(c[1]), float(c[2]),
            float(c[3]), float(c[4]), float(c[5])
        )
        dt = pd.to_datetime(ts, unit="ms")
        df.loc[dt] = [o, h, l, clo, vol]

        # print each new candle
        print(
            f"Added {sym} {tf} @ {dt} → "
            f"o={o:.2f}, h={h:.2f}, l={l:.2f}, c={clo:.2f}, v={vol:.4f}"
        )

    # keep time‑sorted
    data[sym][tf] = df.sort_index()

# ——————————————————————————————————————————————————————————————
# 4) SUBSCRIPTION BUILDER
# ——————————————————————————————————————————————————————————————
async def subscribe(ws: websockets.WebSocketClientProtocol):
    args = [
        {
            "instType": INST_TYPE,
            "channel": f"candle{tf}",
            "instId": sym,
        }
        for sym in SYMBOLS
        for tf in INTERVALS
    ]
    await ws.send(json.dumps({"op": "subscribe", "args": args}))
    print(f"→ Subscribed to {len(args)} streams: "
          f"{', '.join(f'{s}-{t}' for s in SYMBOLS for t in INTERVALS)}")

# ——————————————————————————————————————————————————————————————
# 5) MAIN LOOP WITH RECONNECT
# ——————————————————————————————————————————————————————————————
async def main():
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=20) as ws:
                print("Connected to", WS_URL)
                await subscribe(ws)

                async for raw in ws:
                    msg = json.loads(raw)
                    ch  = msg.get("arg", {}).get("channel", "")
                    if ch.startswith("candle"):
                        process_candle(msg)

        except ConnectionClosedError as e:
            print(f"WebSocket closed ({e}). Reconnecting in 5 s…")
            await asyncio.sleep(5)

        except WebSocketException as e:
            print(f"WebSocket error ({e}). Reconnecting in 5 s…")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"Unexpected error {type(e).__name__}: {e}. Reconnecting in 5 s…")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
