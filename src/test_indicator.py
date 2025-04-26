import os
import pandas as pd

import indicators
import crypto

# 1) hard-coded filenames
filename_1 = "51_BITGET_BTCUSDT.csv"
filename_2 = "StrategyObelix_prod_BTC_BTC_ZY3N_1m.csv"

filename_1 = "49_BITGET_BTCUSDT.csv"
filename_2 = "49_BITGET_BTCUSDT - Copie.csv"

# 2) ensure output directory exists
output_dir = "test_results"
os.makedirs(output_dir, exist_ok=True)

# 3) read them in (assuming the timestamp is the first column and should be parsed)
df1 = pd.read_csv(filename_1, index_col=0, parse_dates=True)
# df2 = pd.read_csv(filename_2, index_col="time", parse_dates=True)
df2 = pd.read_csv(filename_2, index_col=0, parse_dates=True)
df_1h = crypto. _get_ohlcv_bitget_v2("BTCUSDT", "1h", 1000)

# 4) find the overlapping time span
start = max(df1.index.min(), df2.index.min())
end   = min(df1.index.max(), df2.index.max())

# 5) trim to that common interval
df1_trimmed = df1.loc[start:end].copy()
df2_trimmed = df2.loc[start:end].copy()

# 6) save out the results into test_results/
out1 = os.path.join(output_dir, f"trimmed_{filename_1}")
out2 = os.path.join(output_dir, f"trimmed_{filename_2}")
df1_trimmed["source"] = ""
df1_trimmed["released_dt"] = ""
df1_trimmed["index_ws"] = ""
df2_trimmed["source"] = ""
df2_trimmed["released_dt"] = ""
df2_trimmed["index_ws"] = ""

df_1h["source"] = ""
df_1h["released_dt"] = ""
df_1h["index_ws"] = ""

df1_trimmed.to_csv(out1)
df2_trimmed.to_csv(out2)

print(f"Trimmed '{filename_1}' → '{out1}' ({len(df1_trimmed)} rows)")
print(f"Trimmed '{filename_2}' → '{out2}' ({len(df2_trimmed)} rows)")

keep_only_requested_indicators = True
zerolag_id1 = {'zerolag_id1': {'indicator': 'zerolag_ma', 'ma_type': 'HMA', 'high_offset': 1.002, 'low_offset': 1, 'zema_len_buy': 60, 'zema_len_sell': 70, 'window_size': 70, 'id': '1',
                               'output': ['close', 'source', 'released_dt', 'index_ws', 'zerolag_ma_buy_adj', 'zerolag_ma_sell_adj']}}
params = {'symbol': 'XRP/USDT', 'exchange': 'bitget'}

df1_zerolag = indicators.compute_indicators(df1_trimmed, indicators=zerolag_id1, keep_only_requested_indicators=keep_only_requested_indicators, params=params)
df2_zerolag = indicators.compute_indicators(df2_trimmed, indicators=zerolag_id1, keep_only_requested_indicators=keep_only_requested_indicators, params=params)

keep_only_requested_indicators = True
trend_id1 = {'trend_id1': {'indicator': 'trend_indicator',
                           'trend_type': 'PRICE_ACTION',
                           'id': '1',
                           'window_size': 30,
                           'output': [
                               'trend_signal',
                               'source',
                               "s_highest_window",
                               "s_lowest_window",
                               "buy_signal",
                               "sell_signal"
                           ]
                           }
             }
params = {'symbol': 'ETH/USDT', 'exchange': 'bitget'}

df1_trend_id1 = indicators.compute_indicators(df_1h, indicators=trend_id1, keep_only_requested_indicators=keep_only_requested_indicators, params=params)

out1 = os.path.join(output_dir, f"trend_{filename_1}_{filename_2}")
df1_trend_id1.to_csv(out1)

df1_trend_id1.index = df1_trend_id1.index.tz_localize(None)

trend_1m = df1_trend_id1.reindex(df1_zerolag.index, method='ffill')

df1_zerolag = pd.concat([df1_zerolag, trend_1m], axis=1)
df2_zerolag = pd.concat([df2_zerolag, trend_1m])

out1 = os.path.join(output_dir, f"zerolag_{filename_1}")
out2 = os.path.join(output_dir, f"zerolag_{filename_2}")
df1_zerolag.to_csv(out1)
df2_zerolag.to_csv(out2)
