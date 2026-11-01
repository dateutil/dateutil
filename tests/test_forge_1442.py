import pytest
from dateutil import parser
import datetime


def test_parse_9digit_time_as_hhmmssmmm():
    """
    Test that the default parser correctly parses a 9-digit time string
    as HHMMSSmmm format (hour-minute-second-microseconds).
    
    Bug: parser incorrectly interprets "040506789" as a year instead of
    recognizing it as time with microseconds.
    
    Expected: datetime.datetime(2001, 2, 3, 4, 5, 6, 789000)
    """
    # This should parse as: year=2001, month=2, day=3, hour=4, minute=5, second=6, microsecond=789000
    result = parser.parse("20010203 040506789")
    expected = datetime.datetime(2001, 2, 3, 4, 5, 6, 789000)
    assert result == expected
