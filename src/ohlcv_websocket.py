import asyncio
import json
import pandas as pd
import websockets
import datetime
import threading
import csv
import os
import shutil
import logging

# Configure logging for better output and error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BitgetWebSocketClient:
    def __init__(self, subscriptions, url="wss://ws.bitget.com/v2/ws/public", directory="OHLVC_candles"):
        """
        :param subscriptions: List of dicts with subscription details.
               Example: {"instType": "SPOT", "channel": "candle1m", "instId": "BTCUSDT"}
        :param url: Bitget WebSocket public endpoint.
        :param directory: Directory to store CSV files.
        """
        self.url = url
        self.subscriptions = subscriptions
        self.ws = None
        self.lock = threading.Lock()

        # Create the directory if it doesn't exist and clear existing files
        os.makedirs(directory, exist_ok=True)
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.error(f"Failed to delete {file_path}. Reason: {e}")

        self.filenames = {}
        self.previous_candle = {}
        self.previous_candle_dt = {}

        # Create an empty DataFrame and save as CSV for each subscription
        df = pd.DataFrame(columns=["ts", "datetime", "open", "high", "low", "close", "volume"])
        for sub in subscriptions:
            inst_id = sub["instId"]
            channel = sub["channel"]

            if inst_id not in self.filenames:
                self.filenames[inst_id] = {}
                self.previous_candle[inst_id] = {}
                self.previous_candle_dt[inst_id] = {}

            # Remove 'USDT' to get the symbol and 'candle' to get the interval for naming the file
            symbol = inst_id.replace("USDT", "")
            interval = channel.replace("candle", "")

            full_filename = os.path.join(directory, f"{symbol}_{interval}.csv")
            self.filenames[inst_id][channel] = full_filename
            df.to_csv(full_filename, index=False)
            self.previous_candle[inst_id][channel] = []
            self.previous_candle_dt[inst_id][channel] = ""  # initial value

    async def connect(self):
        """Establish the websocket connection."""
        try:
            self.ws = await websockets.connect(self.url)
            logging.info(f"Connected to Bitget WebSocket at {self.url}")
        except Exception as e:
            logging.error("Connection error:", exc_info=True)
            raise e

    async def subscribe(self):
        """Send subscription messages for the specified channels."""
        if not self.ws:
            logging.error("WebSocket not connected.")
            return

        subscribe_message = {
            "op": "subscribe",
            "args": self.subscriptions
        }
        await self.ws.send(json.dumps(subscribe_message))
        logging.info(f"Subscribed with message: {subscribe_message}")

    async def send_ping(self):
        """Send a 'ping' message every 30 seconds to keep the connection alive."""
        try:
            while True:
                await asyncio.sleep(30)
                if self.ws and self.ws.open:
                    await self.ws.send("ping")
                    logging.info("Ping sent")
                else:
                    logging.warning("WebSocket not open for ping.")
                    break
        except Exception as e:
            logging.error("Error sending ping:", exc_info=True)

    async def listen(self):
        """Listen for incoming messages from the WebSocket."""
        if not self.ws:
            logging.error("WebSocket not connected.")
            return
        while True:
            try:
                message = await self.ws.recv()
                if not message:
                    logging.warning("Received empty message; skipping.")
                    continue
                # Check if message is plain text like 'pong'
                if message == "pong":
                    logging.info("Received pong response.")
                    continue
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logging.warning(f"Received non-JSON message: {message}")
                    continue
                self.handle_message(data)
            except Exception as e:
                logging.error("Error receiving message:", exc_info=True)
                raise e

    def process_candle(self, channel, candle):
        """
        Process an individual candle update for a given channel.
        Candle is expected in the format: [ts, open, high, low, close, volume].
        """
        if len(candle) < 6:
            logging.warning(f"Unexpected candle format: {candle}")
            return None
        try:
            ts = int(candle[0])
        except Exception as e:
            logging.error("Error converting timestamp:", exc_info=True)
            return None

        dt_str = pd.to_datetime(ts, unit='ms').strftime("%Y-%m-%d %H:%M:%S")
        new_row = [candle[0], dt_str] + candle[1:6]
        return new_row

    def handle_message(self, data):
        """Process incoming messages."""
        logging.info(f"Received data: {data}")

        if ("arg" in data and
            "channel" in data["arg"] and
            "instId" in data["arg"] and
            "data" in data):
            channel = data["arg"]["channel"]
            ticker = data["arg"]["instId"]

            for candle in data["data"]:
                processed = self.process_candle(channel, candle)
                if processed is not None:
                    self.add_row(ticker, channel, processed)

    def add_row(self, ticker, channel, candle):
        """
        Write candle data to CSV file when the candle timestamp changes.
        Uses a threading lock to ensure safe file writing.
        """
        filename = self.filenames[ticker][channel]
        current_candle_dt = candle[1]  # formatted datetime string

        if self.previous_candle_dt[ticker][channel] == "":
            self.previous_candle_dt[ticker][channel] = current_candle_dt
            self.previous_candle[ticker][channel] = candle
            return

        if current_candle_dt != self.previous_candle_dt[ticker][channel]:
            with self.lock:
                try:
                    with open(filename, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(self.previous_candle[ticker][channel])
                    logging.info(f"Wrote candle for {ticker} {channel}: {self.previous_candle[ticker][channel]}")
                except Exception as e:
                    logging.error("Error writing to CSV:", exc_info=True)
            self.previous_candle_dt[ticker][channel] = current_candle_dt
            self.previous_candle[ticker][channel] = candle
        else:
            self.previous_candle[ticker][channel] = candle

    async def run(self):
        """Main run loop with reconnection and ping."""
        while True:
            try:
                await self.connect()
                await self.subscribe()
                # Start the ping task concurrently.
                ping_task = asyncio.create_task(self.send_ping())
                # Listen for messages; this will run until an exception is raised.
                await self.listen()
            except websockets.exceptions.ConnectionClosedError as e:
                logging.warning(f"Connection closed: {e}. Reconnecting in 5 seconds...", exc_info=True)
            except asyncio.exceptions.IncompleteReadError as e:
                logging.warning(f"Incomplete read: {e}. Reconnecting in 5 seconds...", exc_info=True)
            except Exception as e:
                logging.error("Unexpected error occurred:", exc_info=True)
            finally:
                if self.ws:
                    try:
                        await self.ws.close()
                    except Exception as e:
                        logging.error("Error closing WebSocket:", exc_info=True)
                logging.info("Reconnecting after 5 seconds...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    directory = "OHLVC_datas"
    subscriptions = [
        {"instType": "SPOT", "channel": "candle1m", "instId": "BTCUSDT"},
        {"instType": "SPOT", "channel": "candle1m", "instId": "ETHUSDT"}
    ]
    client = BitgetWebSocketClient(subscriptions, directory=directory)
    asyncio.run(client.run())
