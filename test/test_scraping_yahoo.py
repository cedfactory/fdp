import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from src import yahoo
from . import test_utils

class TestScrapingYahoo:

    def test_get_list_nasdaq(self):
        df = yahoo.get_list_nasdaq()
        test_utils.check_expectations(df, "yahoo_list_nasdaq.csv")

    def test_get_list_yahoo_sp500(self):
        df = yahoo.get_list_yahoo_sp500()
        test_utils.check_expectations(df, "yahoo_list_sp500.csv")

    def test_get_list_dow(self):
        df = yahoo.get_list_dow()
        test_utils.check_expectations(df, "yahoo_list_dow.csv")
       
    def test_get_list_ftse100(self):
        df = yahoo.get_list_ftse100()
        test_utils.check_expectations(df, "yahoo_list_ftse100.csv")

    def test_get_list_ftse250(self):
        df = yahoo.get_list_ftse250()
        test_utils.check_expectations(df, "yahoo_list_ftse250.csv")

    def test_get_list_ibovespa(self):
        df = yahoo.get_list_ibovespa()
        test_utils.check_expectations(df, "yahoo_list_ibovespa.csv")

    def test_get_list_nifty50(self):
        df = yahoo.get_list_nifty50()
        #test_utils.check_expectations(df, "yahoo_list_nifty50.csv")

    def test_get_list_nifty_bank(self):
        df = yahoo.get_list_nifty_bank()
        test_utils.check_expectations(df, "yahoo_list_nifty_bank.csv")

    def test_get_list_euronext(self):
        df = yahoo.get_list_euronext()
        test_utils.check_expectations(df, "yahoo_list_euronext.csv")

    def test_get_list_undervalued(self):
        df = yahoo.get_list_undervalued()

        # can't compare with a reference since it changes
        assert(isinstance(df, pd.DataFrame))
        assert(df.size == 700)

    def test_get_list_losers(self):
        df = yahoo.get_list_losers()
 
        # can't compare with a reference since it changes
        assert(isinstance(df, pd.DataFrame))
        assert(df.size == 700)

    def test_get_list_gainers(self):
        df = yahoo.get_list_gainers()

        # can't compare with a reference since it changes
        assert(isinstance(df, pd.DataFrame))

    def test_get_list_most_actives(self):
        df = yahoo.get_list_most_actives()

        # can't compare with a reference since it changes
        assert(isinstance(df, pd.DataFrame))

    def test_get_list_trending_tickers(self):
        df = yahoo.get_list_trending_tickers()

        # can't compare with a reference since it changes
        assert(isinstance(df, pd.DataFrame))
