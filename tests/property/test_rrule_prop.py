import copy
import itertools
import pickle
from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from dateutil import tz
from dateutil.rrule import DAILY, SECONDLY, YEARLY, rrule, rruleset


@st.composite
def recurrence_options(draw):
    """Finite rules with varied frequencies, weekdays, intervals and timezones."""
    return dict(
        freq=draw(st.integers(min_value=YEARLY, max_value=SECONDLY)),
        dtstart=draw(
            st.datetimes(
                min_value=datetime(2000, 1, 1),
                max_value=datetime(2030, 12, 31),
                timezones=st.sampled_from(
                    [None, tz.UTC, tz.tzoffset(None, 3600)]
                ),
            )
        ),
        count=draw(st.integers(min_value=0, max_value=25)),
        interval=draw(st.integers(min_value=1, max_value=5)),
        byweekday=draw(
            st.lists(
                st.integers(min_value=0, max_value=6),
                min_size=1,
                max_size=7,
                unique=True,
            )
        ),
    )


def _pickle_roundtrip(value, protocol):
    serialized = pickle.dumps(value, protocol)
    return pickle.loads(serialized)


@pytest.mark.rrule
@pytest.mark.parametrize(
    "cache_state", ["disabled", "empty", "partial", "complete"]
)
@pytest.mark.parametrize("operation", ["pickle", "deepcopy"])
@given(
    options=recurrence_options(),
    protocol=st.integers(2, pickle.HIGHEST_PROTOCOL),
)
def test_rrule_roundtrip(options, protocol, cache_state, operation):
    expected = list(rrule(**options))
    original = rrule(cache=cache_state != "disabled", **options)
    iterator = None
    prefix = []
    if cache_state == "partial":
        iterator = iter(original)
        prefix = list(itertools.islice(iterator, 1))
    elif cache_state == "complete":
        assert list(original) == expected

    restored = (
        _pickle_roundtrip(original, protocol)
        if operation == "pickle"
        else copy.deepcopy(original)
    )
    assert list(restored) == expected
    assert restored.count() == len(expected)
    assert str(restored) == str(original)
    if iterator is not None:
        assert prefix + list(iterator) == expected
    assert list(original) == expected


@pytest.mark.rruleset
@pytest.mark.parametrize(
    "cache_state", ["disabled", "empty", "partial", "complete"]
)
@pytest.mark.parametrize("operation", ["pickle", "deepcopy"])
@given(
    options=recurrence_options(),
    protocol=st.integers(2, pickle.HIGHEST_PROTOCOL),
)
def test_rruleset_roundtrip(options, protocol, cache_state, operation):
    cache = cache_state != "disabled"
    original = rruleset(cache=cache)
    original.rrule(rrule(cache=cache, **options))
    start = options["dtstart"].replace(microsecond=0)
    original.rdate(start)
    # Mix included rules/dates with exclusions, including nested cached rules.
    original.exdate(start)
    original.exrule(rrule(DAILY, dtstart=start, count=2, cache=cache))
    expected = sorted(
        set(rrule(**options)) - set(rrule(DAILY, dtstart=start, count=2))
    )
    iterator = None
    prefix = []
    if cache_state == "partial":
        iterator = iter(original)
        prefix = list(itertools.islice(iterator, 1))
    elif cache_state == "complete":
        assert list(original) == expected

    restored = (
        _pickle_roundtrip(original, protocol)
        if operation == "pickle"
        else copy.deepcopy(original)
    )
    assert list(restored) == expected
    assert restored.count() == len(expected)
    if iterator is not None:
        assert prefix + list(iterator) == expected
    assert list(original) == expected
