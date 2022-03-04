import pytest
import pandas as pd

from src import api
from . import test_utils

class TestApi:

    def test_api_list_cac(self):
        response = api.api_list("w_cac")
        assert(response["status"] == "ok")
        assert("w_cac" in response["result"])
        assert(response["result"]["w_cac"]["status"] == "ok")
        
        df_data = response["result"]["w_cac"]["dataframe"]
        df = pd.read_json(df_data)
        test_utils.check_expectations(df, "wiki_list_cac.csv")

    def test_api_value(self):
        response = api.api_value("AI.PA")
        assert("status" in response)
        assert(response["status"] == "ok")
        assert("result" in response)
        assert("AI.PA" in response["result"])
        assert(response["result"]["AI.PA"]["status"] == "ok")
        assert("status" in response["result"]["AI.PA"])
        assert(response["result"]["AI.PA"]["status"] == "ok")
        assert("info" in response["result"]["AI.PA"])
        assert(response["result"]["AI.PA"]["info"]["symbol"] == "AI.PA")
