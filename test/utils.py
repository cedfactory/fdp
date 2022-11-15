import os
import pandas as pd
from pandas.testing import assert_frame_equal

def check_expectations(df, csvfile):
    assert(isinstance(df, pd.DataFrame))
    generated_file = "./test/generated/"+csvfile
    df.to_csv(generated_file)
    df_generated = pd.read_csv(generated_file)
    os.remove(generated_file)
    df_ref = pd.read_csv("./test/references/"+csvfile)
    assert_frame_equal(df_generated, df_ref)

