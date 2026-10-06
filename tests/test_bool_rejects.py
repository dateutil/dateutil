
# -*- coding: utf-8 -*-
"""Reject bool where int is required (bool subclass of int trap)."""
from datetime import datetime

import pytest

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from dateutil import tz


@pytest.mark.parametrize(
    "kwargs",
    [
        {"years": True},
        {"months": False},
        {"days": True},
        {"year": True},
        {"month": True},
        {"day": True},
        {"weekday": True},
    ],
)
def test_relativedelta_rejects_bool(kwargs):
    with pytest.raises(TypeError):
        relativedelta(**kwargs)


def test_tzoffset_rejects_bool():
    with pytest.raises(TypeError):
        tz.tzoffset("X", True)
    with pytest.raises(TypeError):
        tz.tzoffset("X", False)


def test_rrule_rejects_bool_count_interval():
    dt = datetime(2020, 1, 1)
    with pytest.raises(TypeError):
        rrule(DAILY, count=True, dtstart=dt)
    with pytest.raises(TypeError):
        rrule(DAILY, interval=True, count=3, dtstart=dt)


def test_still_accepts_int():
    assert relativedelta(years=1).years == 1
    assert tz.tzoffset("X", 3600).utcoffset(None).total_seconds() == 3600
    assert len(list(rrule(DAILY, count=2, dtstart=datetime(2020, 1, 1)))) == 2
