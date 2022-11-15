import pytest
from pandas.testing import assert_frame_equal

from src import wiki
from . import utils

class TestScrapingWiki:

    def test_get_list_cac(self):
        df = wiki.get_list_cac()
        utils.check_expectations(df, "wiki_list_cac.csv")

    def test_get_list_dax(self):
        df = wiki.get_list_dax()
        utils.check_expectations(df, "wiki_list_dax.csv")

    def test_get_list_nasdaq100(self):
        df = wiki.get_list_nasdaq100()
        utils.check_expectations(df, "wiki_list_nasdaq100.csv")

    def test_get_list_dji(self):
        df = wiki.get_list_dji()
        utils.check_expectations(df, "wiki_list_dji.csv")

    def test_wiki_get_list_sp500(self):
        df = wiki.get_list_sp500()
        utils.check_expectations(df, "wiki_list_sp500.csv")
