import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from scraping import scrap_yahoo_list

class TestScrapingYahoo:

    def check_expectations(self, df, csvfile):
        assert(isinstance(df, pd.DataFrame))
        df.to_csv("./test/generated/"+csvfile)
        df_generated = pd.read_csv("./test/generated/"+csvfile)
        df_ref = pd.read_csv("./test/references/"+csvfile)
        assert_frame_equal(df_generated, df_ref)

    def test_get_list_nasdaq(self):
        df = scrap_yahoo_list.get_list_NASDAQ()
        self.check_expectations(df, "list_nasdaq.csv")

    def test_get_list_yahoo_sp500(self):
        df = scrap_yahoo_list.get_list_yahoo_SP500()
        self.check_expectations(df, "list_sp500.csv")

    def test_get_list_dow(self):
        df = scrap_yahoo_list.get_list_DOW()
        self.check_expectations(df, "list_dow.csv")
       
    def test_get_list_ftse100(self):
        df = scrap_yahoo_list.get_list_FTSE100()
        self.check_expectations(df, "list_ftse100.csv")

    def test_get_list_ftse250(self):
        df = scrap_yahoo_list.get_list_FTSE250()
        self.check_expectations(df, "list_ftse250.csv")

    def test_get_list_ibovespa(self):
        df = scrap_yahoo_list.get_list_IBOVESPA()
        self.check_expectations(df, "list_ibovespa.csv")

    def test_get_list_nifty50(self):
        df = scrap_yahoo_list.get_list_NIFTY50()
        #self.check_expectations(df, "list_nifty50.csv")

    def test_get_list_nifty_bank(self):
        df = scrap_yahoo_list.get_list_NIFTY_BANK()
        self.check_expectations(df, "list_nifty_bank.csv")

    def test_get_list_euronext(self):
        df = scrap_yahoo_list.get_list_EURONEXT()
        self.check_expectations(df, "list_euronext.csv")

    def test_get_list_undervalued(self):
        pass
        #df = scrap_yahoo_list.get_list_undervalued()
        #self.check_expectations(df, "list_undervalued.csv")

    def test_get_list_losers(self):
        pass
        #df = scrap_yahoo_list.get_list_losers()
        #self.check_expectations(df, "list_losers.csv")

    def test_get_list_gainers(self):
        pass
        #df = scrap_yahoo_list.get_list_gainers()
        #self.check_expectations(df, "list_gainers.csv")

    def test_get_list_most_actives(self):
        pass
        #df = scrap_yahoo_list.get_list_most_actives()
        #self.check_expectations(df, "list_most_actives.csv")

    def test_get_list_trending_tickers(self):
        pass
        #df = scrap_yahoo_list.get_list_trending_tickers()
        #self.check_expectations(df, "list_trending_tickers.csv")
