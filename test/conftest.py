import pytest
from src import ws_global

def pytest_sessionstart(session):
    print("-> pytest_sessionstart")
    ws_global.ws_candle_start("../conf/fdp_conf_lst_data_description.xml")

def pytest_sessionfinish(session, exitstatus):
    print("-> pytest_sessionfinish")
    ws_global.ws_candle_stop()
