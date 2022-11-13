
import pandas as pd
import pytest

from src import portfolio

class TestPortfolio:

    def test_get_portfolio(self):
        return # TODO
        df = portfolio.get_portfolio()
        assert(isinstance(df, pd.DataFrame))
        print(df)
        columns = df.columns.tolist()
        print(columns)

        # check the columns names
        columns = df.columns.tolist()
        assert(any(column in ['symbol', 'change1h', 'rank_change1h', 'change24h', 'rank_change24h', 'RECOMMENDATION_15m', 'RECOMMENDATION_30m', 'RECOMMENDATION_1h'] for column in columns))
