"""Regression test for bug: TypeError in tzstr when parsing "UTC" or "GMT" without offset."""
import pytest
from dateutil.tz import tzstr


def test_tzstr_gmt_no_offset():
    """Test that tzstr('GMT') without explicit offset does not raise TypeError."""
    # This should not raise TypeError: unsupported operand type(s) for *=: 'NoneType' and 'int'
    tz = tzstr("GMT")
    assert tz is not None


def test_tzstr_utc_no_offset():
    """Test that tzstr('UTC') without explicit offset does not raise TypeError."""
    # This should not raise TypeError: unsupported operand type(s) for *=: 'NoneType' and 'int'
    tz = tzstr("UTC")
    assert tz is not None
