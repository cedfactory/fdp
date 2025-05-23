import pandas as pd
import redis
import pickle

class WSRedisCandleData:
    def __init__(self, params, redis_host='localhost', redis_port=6379, db=0):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=db)

        for item in params:
            symbol_key = item["symbol"] + "USDT"
            timeframe = item["timeframe"]
            key = f"{symbol_key}:{timeframe}"
            if not self.redis_client.exists(key):
                self.redis_client.set(key, pickle.dumps(None))

    def set_value(self, symbol_key, timeframe, df):
        if not symbol_key.endswith("USDT"):
            symbol_key += "USDT"
        key = f"{symbol_key}:{timeframe}"

        existing_df = pickle.loads(self.redis_client.get(key))
        if existing_df is None:
            self.redis_client.set(key, pickle.dumps(df.iloc[:-1].copy()))
            return

        to_update = []
        to_append = []

        for idx, row in df.iterrows():
            if idx in existing_df.index:
                to_update.append((idx, row))
            else:
                to_append.append(row)

        for idx, row in to_update:
            existing_df.loc[idx] = row

        if to_append:
            append_df = pd.DataFrame(to_append, index=[r.name for r in to_append])
            existing_df = pd.concat([existing_df, append_df])
            existing_df.sort_index(inplace=True)

        existing_df = existing_df[~existing_df.index.duplicated(keep='last')]
        if len(existing_df) > 1000:
            existing_df = existing_df.tail(1000)

        self.redis_client.set(key, pickle.dumps(existing_df))

    def get_value(self, symbol_key, timeframe):
        if not symbol_key.endswith("USDT"):
            symbol_key += "USDT"
        key = f"{symbol_key}:{timeframe}"
        return pickle.loads(self.redis_client.get(key))

    def get_ohlcv(self, symbol_key, timeframe, length):
        if not symbol_key.endswith("USDT"):
            symbol_key += "USDT"
        key = f"{symbol_key}:{timeframe}"
        df = pickle.loads(self.redis_client.get(key))
        if df is None:
            return None
        return df.tail(length)

    def update_ohlcv_from_api(self, symbol_key, timeframe, df_api_ohlv):
        if not symbol_key.endswith("USDT"):
            symbol_key += "USDT"
        key = f"{symbol_key}:{timeframe}"
        existing_df = pickle.loads(self.redis_client.get(key))
        if existing_df is None or df_api_ohlv is None:
            return

        df_api_ohlv = df_api_ohlv[existing_df.columns]
        missing_indices = df_api_ohlv.index.difference(existing_df.index)
        df_missing = df_api_ohlv.loc[missing_indices]
        df_combined = pd.concat([existing_df, df_missing])
        df_combined.sort_index(inplace=True)
        self.redis_client.set(key, pickle.dumps(df_combined))