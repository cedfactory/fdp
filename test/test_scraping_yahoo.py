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
        pass
        #df = yahoo.get_list_undervalued()
        #test_utils.check_expectations(df, "yahoo_list_undervalued.csv")

    def test_get_list_losers(self):
        pass
        #df = scrap_yahoo_list.get_list_losers()
        #test_utils.check_expectations(df, "yahoo_list_losers.csv")

    def test_get_list_gainers(self):
        pass
        #df = yahoo.get_list_gainers()
        #test_utils.check_expectations(df, "yahoo_list_gainers.csv")

    def test_get_list_most_actives(self):
        pass
        #df = yahoo.get_list_most_actives()
        #test_utils.check_expectations(df, "yahoo_list_most_actives.csv")

    def test_get_list_trending_tickers(self):
        pass
        #df = yahoo.get_list_trending_tickers()
        #test_utils.check_expectations(df, "yahoo_list_trending_tickers.csv")
