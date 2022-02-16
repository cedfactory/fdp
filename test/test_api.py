import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from src import api

class TestApi:

    def check_expectations(self, df, csvfile):
        assert(isinstance(df, pd.DataFrame))
        df.to_csv("./test/generated/"+csvfile)
        df_generated = pd.read_csv("./test/generated/"+csvfile)
        df_ref = pd.read_csv("./test/references/"+csvfile)
        assert_frame_equal(df_generated, df_ref)

    def test_api_list_cac(self):
        response = api.api_list(["w_cac"])
        print(response)
        assert(response["status"] == "ok")
        assert("w_cac" in response["result"])
        assert(response["result"]["w_cac"]["status"] == "ok")
        
        df_data = response["result"]["w_cac"]["dataframe"]
        df = pd.read_json(df_data)
        self.check_expectations(df, "wiki_list_cac.csv")

