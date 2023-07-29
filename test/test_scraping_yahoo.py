import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from src import yahoo
from . import utils

class TestScrapingYahoo:

    def test_get_list_nasdaq(self):
        df = yahoo.get_list_nasdaq()
        assert(df["symbol"].isin(["AACG","AACI","ZXZZT"]).value_counts().loc[True] == 3)
        #utils.check_expectations(df, "yahoo_list_nasdaq.csv")

    def test_get_list_yahoo_sp500(self):
        df = yahoo.get_list_yahoo_sp500()
        utils.check_expectations(df, "yahoo_list_sp500.csv")

    def test_get_list_dow(self):
        df = yahoo.get_list_dow()
        utils.check_expectations(df, "yahoo_list_dow.csv")
       
    def test_get_list_ftse100(self):
        # TODO : yahoo_fin needs an update
        # replace table.EPIC.tolist() with table.Ticker.tolist()
        return
        df = yahoo.get_list_ftse100()
        utils.check_expectations(df, "yahoo_list_ftse100.csv")

    def test_get_list_ftse250(self):
        # TODO : yahoo_fin needs an update
        # replace table.EPIC.tolist() with table.Ticker.tolist()
        return
        df = yahoo.get_list_ftse250()
        utils.check_expectations(df, "yahoo_list_ftse250.csv")

    def test_get_list_ibovespa(self):
        df = yahoo.get_list_ibovespa()
        utils.check_expectations(df, "yahoo_list_ibovespa.csv")

    def test_get_list_nifty50(self):
        df = yahoo.get_list_nifty50()
        #utils.check_expectations(df, "yahoo_list_nifty50.csv")

    def test_get_list_nifty_bank(self):
        df = yahoo.get_list_nifty_bank()
        utils.check_expectations(df, "yahoo_list_nifty_bank.csv")

    def test_get_list_euronext(self):
        df = yahoo.get_list_euronext()
        utils.check_expectations(df, "yahoo_list_euronext.csv")

    def test_get_list_undervalued(self):
        df = yahoo.get_list_undervalued()

        # can't compare with a reference since it changes
        assert(isinstance(df, pd.DataFrame))
        #assert(df.size == 700)

    def test_get_list_losers(self):
        df = yahoo.get_list_losers()
 
        # can't compare with a reference since it changes
        assert(isinstance(df, pd.DataFrame))
        assert(df.size > 100)

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
