import os
import pandas as pd
from pandas.testing import assert_frame_equal

def check_expectations(df, csvfile):
    assert(isinstance(df, pd.DataFrame))
    df.to_csv("./test/generated/"+csvfile)
    df_generated = pd.read_csv("./test/generated/"+csvfile)
    os.remove("./test/generated/"+csvfile)
    df_ref = pd.read_csv("./test/references/"+csvfile)
    assert_frame_equal(df_generated, df_ref)
