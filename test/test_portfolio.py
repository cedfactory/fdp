
import pandas as pd
import pytest

from src import portfolio

class TestPortfolio:

    def test_get_portfolio(self):
        df = portfolio.get_portfolio()
        assert(isinstance(df, pd.DataFrame))
        columns = df.columns.tolist()

        # check the columns names
        columns = df.columns.tolist()
        assert(any(column in ['symbol', 'volume', 'change', 'rank', 'RECOMMENDATION_15m', 'RECOMMENDATION_30m', 'RECOMMENDATION_1h'] for column in columns))
