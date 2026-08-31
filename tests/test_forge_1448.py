"""Regression test for dayfirst bug with unambiguous year.

According to the documentation, dayfirst should only distinguish between
YDM and YMD when yearfirst is True. When the year is unambiguous (e.g.,
a 4-digit year), dayfirst should not affect the parsing.

See: https://dateutil.readthedocs.io/en/stable/parser.html
"""
import pytest
from datetime import datetime
from dateutil import parser


def test_dayfirst_with_unambiguous_year():
    """
    When parsing '2024-11-06', the year is unambiguous (4 digits).
    With dayfirst=True and yearfirst=False (or default), the result
    should still be 2024-11-06, not 2024-06-11.
    
    The bug is that dayfirst=True incorrectly swaps month and day
    even when the year is clearly the 4-digit number.
    """
    # Without dayfirst, this should parse as Nov 6, 2024
    result_default = parser.parse('2024-11-06')
    assert result_default == datetime(2024, 11, 6, 0, 0)
    
    # With dayfirst=True but yearfirst=False (default), the year is still
    # unambiguous, so the result should be the same: Nov 6, 2024
    # The bug causes this to return June 11, 2024 instead
    result_dayfirst = parser.parse('2024-11-06', dayfirst=True)
    assert result_dayfirst == datetime(2024, 11, 6, 0, 0), \
        f"Expected 2024-11-06 but got {result_dayfirst.date()}. " \
        "dayfirst should not affect parsing when year is unambiguous."
    
    # Explicitly setting yearfirst=False should also not change the result
    result_dayfirst_yearfirst_false = parser.parse('2024-11-06', dayfirst=True, yearfirst=False)
    assert result_dayfirst_yearfirst_false == datetime(2024, 11, 6, 0, 0), \
        f"Expected 2024-11-06 but got {result_dayfirst_yearfirst_false.date()}."
