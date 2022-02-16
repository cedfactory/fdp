import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from src import wiki

class TestScrapingWiki:

    def check_expectations(self, df, csvfile):
        assert(isinstance(df, pd.DataFrame))
        df.to_csv("./test/generated/"+csvfile)
        df_generated = pd.read_csv("./test/generated/"+csvfile)
        df_ref = pd.read_csv("./test/references/"+csvfile)
        assert_frame_equal(df_generated, df_ref)

    def test_get_list_cac(self):
        df = wiki.get_list_cac()
        self.check_expectations(df, "wiki_list_cac.csv")

    def test_get_list_dax(self):
        df = wiki.get_list_dax()
        self.check_expectations(df, "wiki_list_dax.csv")

    def test_get_list_nasdaq100(self):
        df = wiki.get_list_nasdaq100()
        self.check_expectations(df, "wiki_list_nasdaq100.csv")

    def test_get_list_dji(self):
        df = wiki.get_list_dji()
        self.check_expectations(df, "wiki_list_dji.csv")

    def test_wiki_get_list_sp500(self):
        df = wiki.get_list_sp500()
        self.check_expectations(df, "wiki_list_sp500.csv")
