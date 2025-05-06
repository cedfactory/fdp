import zmq
import pandas as pd
import json
import sys
from zed_client import ZMQClient
from zed_server import ZMQServer

def load_config(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <config.json>")
        sys.exit(1)
    server = ZMQServer(sys.argv[1])
    server.serve_forever()

    # Accept either a JSON config or a raw address
    if len(sys.argv) == 2 and sys.argv[1].lower().endswith('.json'):
        cfg = load_config(sys.argv[1])
        address = cfg.get("bind_address", "tcp://127.0.0.1:5555")
    else:
        address = sys.argv[1] if len(sys.argv) > 1 else "tcp://127.0.0.1:5555"

    client = ZMQClient(address)
    try:
        status = client.get_status()
        print("Status:", status)
        df = client.get_data()
        print(df)
    except Exception as e:
        print("Error:", e)
    finally:
        client.close()