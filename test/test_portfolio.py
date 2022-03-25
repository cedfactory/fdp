import pytest

from src import portfolio

class TestPortfolio:

    def test_get_portfolio(self):
        res = portfolio.get_portfolio()
        assert(isinstance(res, list))
