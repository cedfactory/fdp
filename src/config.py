from . import data_recorder

use_mock = False
g_data = None
get_symbol_ohlcv_fn = None

SYMBOL_SYNTHETIC = 'SYNTHETIC'
trace_ohlcv = True
noise = False

'''
    features = {"low": None,
                "high": None,
                "ema_5": None,
                "ema_400": None,
                "super_trend_direction": {"feature": "super_trend"}
                }

    with open('features_super_reversal.txt', 'w') as convert_file:
        convert_file.write(json.dumps(features))

    with open('features_super_reversal.txt') as f:
        data = f.read()

    js = json.loads(data)
'''