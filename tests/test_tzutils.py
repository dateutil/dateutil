import pytest
from datetime import datetime, timedelta
from dateutil.tz import gettz
from dateutil.tzutils import walltimedelta

def test_walltimedelta_dst_transition():
    # Test wall time delta across DST start (spring forward).
    tz = gettz("America/New_York")
    start = datetime(2024, 3, 10, 1, 0, tzinfo=tz)  # Before DST
    end = datetime(2024, 3, 10, 3, 0, tzinfo=tz)    # After DST
    delta = walltimedelta(start, end)
    assert delta == timedelta(hours=1), f"Expected 1 hour, got {delta}"

def test_walltimedelta_no_dst():
    # Test wall time delta without DST change.
    tz = gettz("America/New_York")
    start = datetime(2024, 1, 1, 12, 0, tzinfo=tz)
    end = datetime(2024, 1, 2, 12, 0, tzinfo=tz)
    delta = walltimedelta(start, end)
    assert delta == timedelta(days=1), f"Expected 1 day, got {delta}"

def test_walltimedelta_naive_with_tz():
    # Test naive datetimes with provided timezone.
    tz = gettz("Europe/Berlin")
    start = datetime(2024, 3, 30, 12, 0)
    end = datetime(2024, 3, 31, 12, 0)
    delta = walltimedelta(start, end, tz=tz)
    assert delta == timedelta(days=1, hours=1), f"Expected 1 day + 1 hour, got {delta}"

def test_walltimedelta_naive_no_tz():
    # Test naive datetimes without timezone raises ValueError.
    start = datetime(2024, 1, 1, 12, 0)
    end = datetime(2024, 1, 2, 12, 0)
    with pytest.raises(ValueError, match="Some datetime is naive"):
        walltimedelta(start, end)
# -*- coding: utf-8 -*-
import pytest
from datetime import datetime, timedelta
from dateutil.tz import gettz, tzoffset
from dateutil.tzutils import walltimedelta


def test_walltimedelta_dst_transition_spring():
    """Test wall time delta across DST start (spring forward)."""
    tz = gettz("America/New_York")
    # 1:30 AM to 3:30 AM on DST transition day (spring forward)
    # Wall clock shows 1:30 AM, then 3:30 AM (skipping 2:00-2:59 AM)
    # Actual elapsed time is 1 hour
    start = datetime(2024, 3, 10, 1, 30, tzinfo=tz)  # Before DST transition
    end = datetime(2024, 3, 10, 3, 30, tzinfo=tz)    # After DST transition
    delta = walltimedelta(start, end)
    assert delta == timedelta(hours=1), f"Expected 1 hour, got {delta}"


def test_walltimedelta_dst_transition_fall():
    """Test wall time delta across DST end (fall back)."""
    tz = gettz("America/New_York")
    # 1:30 AM to 1:30 AM on DST transition day (fall back)
    # Clock shows 1:30 AM EDT, then repeats 1:30 AM EST
    # Actual elapsed time is 1 hour
    start = datetime(2023, 11, 5, 1, 30, tzinfo=tz, fold=0)  # EDT
    end = datetime(2023, 11, 5, 1, 30, tzinfo=tz, fold=1)    # EST
    delta = walltimedelta(start, end)
    assert delta == timedelta(hours=1), f"Expected 1 hour, got {delta}"


def test_walltimedelta_no_dst():
    """Test wall time delta without DST change."""
    tz = gettz("America/New_York")
    start = datetime(2024, 1, 1, 12, 0, tzinfo=tz)
    end = datetime(2024, 1, 2, 12, 0, tzinfo=tz)
    delta = walltimedelta(start, end)
    assert delta == timedelta(days=1), f"Expected 1 day, got {delta}"


def test_walltimedelta_naive_with_tz():
    """Test naive datetimes with provided timezone."""
    tz = gettz("Europe/Berlin")
    # March 31, 2024 is DST transition in Europe
    start = datetime(2024, 3, 30, 12, 0)  # Before DST transition
    end = datetime(2024, 3, 31, 12, 0)    # After DST transition 
    delta = walltimedelta(start, end, tz=tz)
    # Due to DST, wall time difference is 23 hours
    assert delta == timedelta(hours=23), f"Expected 23 hours, got {delta}"


def test_walltimedelta_naive_no_tz():
    """Test naive datetimes without timezone raises ValueError."""
    start = datetime(2024, 1, 1, 12, 0)
    end = datetime(2024, 1, 2, 12, 0)
    with pytest.raises(ValueError, match="Some datetime is naive"):
        walltimedelta(start, end)


def test_walltimedelta_different_timezones():
    """Test datetimes in different timezones raises ValueError."""
    tz1 = gettz("America/New_York")
    tz2 = gettz("Europe/London")
    start = datetime(2024, 1, 1, 12, 0, tzinfo=tz1)
    end = datetime(2024, 1, 2, 12, 0, tzinfo=tz2)
    with pytest.raises(ValueError, match="Datetimes are in different timezones"):
        walltimedelta(start, end)


def test_walltimedelta_with_fixed_offset_tzs():
    """Test with fixed-offset timezones."""
    tz1 = tzoffset("UTC+1", 3600)  # UTC+1
    tz2 = tzoffset("UTC+1", 3600)  # Another UTC+1 instance
    start = datetime(2024, 1, 1, 12, 0, tzinfo=tz1)
    end = datetime(2024, 1, 2, 12, 0, tzinfo=tz2)
    delta = walltimedelta(start, end)
    assert delta == timedelta(days=1), f"Expected 1 day, got {delta}"


def test_walltimedelta_mixed_naive_and_aware():
    """Test with one naive and one aware datetime."""
    tz = gettz("America/New_York")
    start = datetime(2024, 1, 1, 12, 0)  # Naive
    end = datetime(2024, 1, 2, 12, 0, tzinfo=tz)  # Aware
    delta = walltimedelta(start, end, tz=tz)
    assert delta == timedelta(days=1), f"Expected 1 day, got {delta}"

    # Test the other way around too
    start = datetime(2024, 1, 1, 12, 0, tzinfo=tz)  # Aware
    end = datetime(2024, 1, 2, 12, 0)  # Naive
    delta = walltimedelta(start, end, tz=tz)
    assert delta == timedelta(days=1), f"Expected 1 day, got {delta}"
def test_walltimedelta_different_timezones():
    # Test datetimes in different timezones raises ValueError.
    tz1 = gettz("America/New_York")
    tz2 = gettz("Europe/London")
    start = datetime(2024, 1, 1, 12, 0, tzinfo=tz1)
    end = datetime(2024, 1, 2, 12, 0, tzinfo=tz2)
    with pytest.raises(ValueError, match="Datetimes are on different timezones"):
        walltimedelta(start, end)

def test_walltimedelta_ambiguous_time():
    # Test handling of ambiguous DST time (fall back).
    tz = gettz("America/New_York")
    start = datetime(2024, 11, 3, 1, 0, tzinfo=tz)  # Ambiguous time
    end = datetime(2024, 11, 3, 2, 0, tzinfo=tz)
    delta = walltimedelta(start, end)
    assert delta == timedelta(hours=2), f"Expected 2 hours, got {delta}"
