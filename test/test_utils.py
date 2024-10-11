
import pytest
from datetime import datetime
from src import utils

class TestUtils:

    def test_convert_string_to_datetime_YYY_MM_DD(self):
        # action
        timestamp = utils.convert_string_to_datetime("2022-01-01")

        # expectations
        assert(isinstance(timestamp, datetime))
        assert(timestamp.timestamp() == 1640991600)

    def test_convert_string_to_datetime_YYY_MM_DD_HH_MM_SS(self):
        # action
        timestamp = utils.convert_string_to_datetime("2021-12-15 08:00:00")

        # expectations
        assert(isinstance(timestamp, datetime))
        assert(timestamp.timestamp() == 1639551600)

    def test_convert_string_to_datetime_timestamp_as_string(self):
        # action
        timestamp = utils.convert_string_to_datetime("1640995200000")

        # expectations
        assert(isinstance(timestamp, datetime))
        assert(timestamp.timestamp() == 1640995200)

    def test_convert_string_to_datetime_timestamp_as_integer(self):
        # action
        timestamp = utils.convert_string_to_datetime(1640995200000)

        # expectations
        assert(isinstance(timestamp, datetime))
        assert(timestamp.timestamp() == 1640995200)
