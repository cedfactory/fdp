import pandas as pd

def create_hlcv(df, i):
    '''
    #i: days
    '''
    df[f'high_{i}D'] = df.high.rolling(i).max()
    df[f'low_{i}D'] = df.low.rolling(i).min()
    df[f'close_{i}D'] = df.close.rolling(i). \
        apply(lambda x: x[-1])
    df[f'volume_{i}D'] = df.volume.rolling(i).sum()

    return df


def create_vsa_features(df, i):
    df = create_hlcv(df, i)
    high = df[f'high_{i}D']
    low = df[f'low_{i}D']
    close = df[f'close_{i}D']
    volume = df[f'volume_{i}D']

    features = pd.DataFrame(index=df.index)
    features['vsa_' + f'volume_{i}D'] = volume.pct_change()
    features['vsa_' + f'price_spread_{i}D'] = (high - low).pct_change()
    features['vsa_' + f'close_loc_{i}D'] = (high - close) / (high - low)
    features['vsa_' + f'close_change_{i}D'] = close.pct_change(-i)

    return features


def create_bunch_of_vsa_features(df, days):
    df_close_copy = df.close.copy()
    bunch_of_features = pd.DataFrame(index=df.index)
    for day in days:
        f = create_vsa_features(df, day)
        bunch_of_features = bunch_of_features.join(f)

    frames = [df_close_copy, bunch_of_features]
    bunch_of_features = pd.concat(frames, axis=1)
    return bunch_of_features
