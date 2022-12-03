import sys
from datetime import datetime, timedelta

import pytest
from hypothesis import assume, example, given
from hypothesis import strategies as st

from dateutil import tz

# Bounds of a signed 32-bit time_t, as naive *UTC* datetimes. They are naive
# because st.datetimes() requires naive bounds; the strategy attaches tz.UTC
# to them, so they must be computed in UTC and not with fromtimestamp(),
# which returns local time and would shift them by the process time zone.
EPOCH = datetime(1970, 1, 1)
EPOCHALYPSE = EPOCH + timedelta(seconds=2**31 - 1)
NEGATIVE_EPOCHALYPSE = EPOCH - timedelta(seconds=2**31)

try:
    import zoneinfo
except ImportError:
    try:
        import backports.zoneinfo as zoneinfo
    except ImportError:
        zoneinfo = None


def __valid_keys():
    key_list = tz.available_iana_timezones()
    return tuple(sorted(key_list))


VALID_KEYS = __valid_keys()
del __valid_keys

iana_keys = st.sampled_from(VALID_KEYS)


@pytest.mark.gettz
@given(key=iana_keys)
def test_key_property(key):
    tzi = tz.gettz(key)
    assume(isinstance(tzi, tz.tzfile))
    assert tzi.key == key


@pytest.mark.gettz
@pytest.mark.skipif(
    sys.version_info < (3, 6), reason="Not supported on Python < 3.6"
)
@pytest.mark.parametrize("gettz_arg", [None, ""])
# TODO: Remove bounds when GH #590 is resolved
@given(
    dt=st.datetimes(
        min_value=NEGATIVE_EPOCHALYPSE,
        max_value=EPOCHALYPSE,
        timezones=st.just(tz.UTC),
    )
)
# Explicit examples are UTC-aware like the generated values, so that they go
# through the same code path (a naive dt would be interpreted as local time,
# which puts a fixed "very old" example inside or outside the GH #590 bound
# depending on the process time zone).
# 01:15 in America/New_York on a fall-back day, i.e. ambiguous local time.
@example(dt=datetime(2005, 10, 30, 5, 15, tzinfo=tz.UTC))
# 01:00 in America/New_York on a fall-back day: CI's falsifying example.
@example(dt=datetime(2015, 11, 1, 5, 0, tzinfo=tz.UTC))
# Very old: the 32-bit floor itself. CI's falsifying example was 5 hours
# earlier, which is outside the bound (the miscomputed local-time bound let
# it through); that value fails by design (GH #590), so the regression check
# is the edge of the corrected bound.
@example(dt=NEGATIVE_EPOCHALYPSE.replace(tzinfo=tz.UTC))
@example(dt=EPOCHALYPSE.replace(tzinfo=tz.UTC))
def test_gettz_returns_local(gettz_arg, dt):
    act_tz = tz.gettz(gettz_arg)
    if isinstance(act_tz, tz.tzlocal):
        return

    dt_act = dt.astimezone(act_tz)
    dt_exp = dt.astimezone()

    assert dt_act.astimezone(tz.UTC) == dt_exp.astimezone(tz.UTC)
    assert dt_act.tzname() == dt_exp.tzname()
    assert dt_act.utcoffset() == dt_exp.utcoffset()

    # According to PEP 495, if the value of fold would change the return value
    # of utcoffset(), comparisons with the datetime always return false, so we
    # must handle the case of ambiguous and imaginary datetimes here for the
    # property to remain valid.
    if (
        tz.enfold(dt_act, fold=0).utcoffset()
        == tz.enfold(dt_act, fold=1).utcoffset()
    ):
        assert dt_act == dt_exp
    else:
        # Check that the system time zone also considers the local wall time
        # ambiguous. This must be done on the naive wall time: fold has no
        # effect on the UTC-aware dt, and dt_exp carries a fixed offset.
        wall = dt_exp.replace(tzinfo=None)
        assert (
            tz.enfold(wall, fold=0).astimezone().utcoffset()
            != tz.enfold(wall, fold=1).astimezone().utcoffset()
        )
        assert dt_act != dt_exp
