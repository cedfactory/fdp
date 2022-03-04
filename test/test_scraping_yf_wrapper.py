import pytest

from src import yf_wrapper

class TestScrapingYfWrapper:

    def test_get_info(self):
        result = yf_wrapper.get_info("AI.PA")
        print(type(result))
        print(result)
        assert("status" in result)
        assert(result["status"] == "ok")
        assert("info" in result)
        assert(result["info"]["country"] == "France")
        assert(result["info"]["exchange"] == "PAR")
        assert(result["info"]["isin"] == "FR0000053951")
        assert(result["info"]["sector"] == "Basic Materials")
        assert(result["info"]["short_name"] == "AIR LIQUIDE")
        assert(result["info"]["symbol"] == "AI.PA")
