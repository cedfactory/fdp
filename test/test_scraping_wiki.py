import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from src import wiki
from . import test_utils

class TestScrapingWiki:

    def test_get_list_cac(self):
        df = wiki.get_list_cac()
        test_utils.check_expectations(df, "wiki_list_cac.csv")

    def test_get_list_dax(self):
        df = wiki.get_list_dax()
        test_utils.check_expectations(df, "wiki_list_dax.csv")

    def test_get_list_nasdaq100(self):
        df = wiki.get_list_nasdaq100()
        test_utils.check_expectations(df, "wiki_list_nasdaq100.csv")

    def test_get_list_dji(self):
        df = wiki.get_list_dji()
        test_utils.check_expectations(df, "wiki_list_dji.csv")

    def test_wiki_get_list_sp500(self):
        df = wiki.get_list_sp500()
        test_utils.check_expectations(df, "wiki_list_sp500.csv")
