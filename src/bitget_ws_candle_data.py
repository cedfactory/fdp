import pandas as pd
#import datetime
#from src import utils

import threading

class WSCandleData:
    def __init__(self, params):
        """
        params: a list of dicts, e.g.
        [
            {"symbol": "BTC", "timeframe": "1m"},
            {"symbol": "BTC", "timeframe": "1h"},
            {"symbol": "ETH", "timeframe": "1m"},
            {"symbol": "ETH", "timeframe": "1h"},
            ...
        ]
        """
        self.state = {}
        self._lock = threading.Lock()

        # Build the nested dictionary
        for item in params:
            symbol_key = item["symbol"] + "USDT"
            if symbol_key not in self.state:
                self.state[symbol_key] = {}
            self.state[symbol_key][item["timeframe"]] = None

    def set_value(self, symbol_key, timeframe, df):
        # print("set_value", symbol_key, timeframe)
        if not symbol_key.endswith("USDT"):
            symbol_key += "USDT"
        self.state.setdefault(symbol_key, {})

        # 2) First‐time load: drop the very last row and store
        if self.state[symbol_key][timeframe] is None:
            self.state[symbol_key][timeframe] = df.iloc[:-1].copy()
            return  # nothing else to do on first load

        existing_df = self.state[symbol_key][timeframe]

        # 3) Separate new rows into update vs append
        to_update = []
        to_append = []

        for idx, row in df.iterrows():
            if idx in existing_df.index:
                to_update.append((idx, row))
            else:
                to_append.append(row)

        # 4) Bulk‐update existing rows
        for idx, row in to_update:
            # with self._lock:
            existing_df.loc[idx] = row
            # print(f"+ {symbol_key} {timeframe} updated: {idx} at now (UTC): {datetime.datetime.now(datetime.timezone.utc)}")  # CEDE DEBUG

        # 5) Bulk‐append new rows (as a single concat)
        if to_append:
            append_df = pd.DataFrame(to_append, index=[r.name for r in to_append])
            # with self._lock:
            existing_df = pd.concat([existing_df, append_df], axis=0)
            existing_df.sort_index(inplace=True)
            # for idx in append_df.index: # CEDE DEBUG
            #     print(f"- {symbol_key} {timeframe} added: {idx} at now (UTC): {datetime.datetime.now(datetime.timezone.utc)}") # CEDE DEBUG

        # 6) Final dedupe & trim
        existing_df = existing_df[~existing_df.index.duplicated(keep='last')]
        if len(existing_df) > 1000:
            existing_df = existing_df.tail(1000)

        # 7) Save back into state
        # with self._lock:
        self.state[symbol_key][timeframe] = existing_df

    def get_value(self, symbol_key, timeframe):
        """
        Get the value for a given symbol + timeframe combination.
        Returns None if not found.
        """
        if not symbol_key.endswith("USDT"):
            symbol_key += "USDT"

        return self.state[symbol_key].get(timeframe)

    def get_ohlcv(self, symbol_key, timeframe, length):
        """
        Get the value for a given symbol + timeframe combination.
        Returns None if not found.
        """
        if not symbol_key.endswith("USDT"):
            symbol_key += "USDT"

        print("self.state[symbol_key].get(timeframe): ", self.state[symbol_key].get(timeframe))
        # with self._lock:
        if self.state[symbol_key].get(timeframe) is None:
            # return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
            return None
        # print('self.state[symbol_key].get(timeframe).tail(length): ', self.state[symbol_key].get(timeframe).tail(5))
        return self.state[symbol_key].get(timeframe).tail(length)

    def update_ohlcv_from_api(self, symbol_key, timeframe, df_api_ohlv):
        if (self.state[symbol_key].get(timeframe)) is None or (df_api_ohlv is None):
            return

        with self._lock:
            df_existing = self.state[symbol_key].get(timeframe)
            df_api_ohlv = df_api_ohlv[df_existing.columns]
            missing_indices = df_api_ohlv.index.difference(df_existing.index)
            df_missing = df_api_ohlv.loc[missing_indices]
            df_combined = pd.concat([df_existing, df_missing])
            df_combined = df_combined.sort_index()
            self.state[symbol_key][timeframe] = df_combined


