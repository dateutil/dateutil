import sys
from datetime import datetime, timedelta

import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from dateutil import tz
from dateutil.parser import isoparse

# Strategies
ZONES = [
    tz.gettz(zname)
    for zname in (
        "America/New_York",
        "America/Los_Angeles",
        "Australia/Sydney",
        "Europe/London",
    )
]
# A missing zone must not silently turn into a naive datetime.
assert None not in ZONES
TIME_ZONE_STRATEGY = st.sampled_from([None, tz.UTC] + ZONES)
ASCII_STRATEGY = st.characters(max_codepoint=127)


@pytest.mark.isoparser
@settings(deadline=3000)
@given(dt=st.datetimes(timezones=TIME_ZONE_STRATEGY), sep=ASCII_STRATEGY)
# Ambiguous in US/Eastern: the first 01:00 (EDT) and the second (EST)
@example(dt=datetime(2020, 11, 1, 1, tzinfo=tz.gettz("US/Eastern")), sep="T")
@example(
    dt=tz.enfold(datetime(2020, 11, 1, 1, tzinfo=tz.gettz("US/Eastern")), 1),
    sep="T",
)
def test_timespec_auto(dt, sep):
    if dt.tzinfo is not None:
        # Assume offset has no sub-second components
        assume(dt.utcoffset().total_seconds() % 60 == 0)

    sep = str(sep)          # Python 2.7 requires bytes
    dtstr = dt.isoformat(sep=sep)
    dt_rt = isoparse(dtstr)

    # The round trip preserves the wall time and the offset.
    assert dt_rt.replace(tzinfo=None) == dt.replace(tzinfo=None)
    assert dt_rt.utcoffset() == dt.utcoffset()

    # According to PEP 495, if the value of fold would change the return value
    # of utcoffset(), comparisons with the datetime always return false, so we
    # must handle the case of ambiguous and imaginary datetimes here for the
    # property to remain valid. Before Python 3.6 there is no fold support in
    # datetime itself, so the comparison is always by instant.
    if (
        sys.version_info < (3, 6)
        or dt.tzinfo is None
        or tz.enfold(dt, fold=0).utcoffset()
        == tz.enfold(dt, fold=1).utcoffset()
    ):
        assert dt_rt == dt
    else:
        assert dt_rt != dt
