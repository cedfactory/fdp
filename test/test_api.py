import pytest
import pandas as pd

from src import api
from . import test_utils

class TestApi:

    def test_api_list_cac(self):
        response = api.api_list("w_cac")
        print(response)
        assert(response["status"] == "ok")
        assert("w_cac" in response["result"])
        assert(response["result"]["w_cac"]["status"] == "ok")
        
        df_data = response["result"]["w_cac"]["dataframe"]
        df = pd.read_json(df_data)
        test_utils.check_expectations(df, "wiki_list_cac.csv")

