import sys
from datetime import datetime, timedelta

import pytest
from hypothesis import assume, example, given
from hypothesis import strategies as st

from dateutil import tz

# `dateutil` only reads the 32-bit (version 1) block of a TZif file, so it
# has no transition data outside the range representable by a signed 32-bit
# timestamp.  The strategy below generates *UTC* datetimes, so these bounds
# must be UTC as well -- deriving them from `datetime.fromtimestamp()` made
# them local wall times, which in any zone with a non-zero offset let the
# strategy wander outside the representable range (GH #590).
EPOCH = datetime(1970, 1, 1)
EPOCHALYPSE = EPOCH + timedelta(seconds=2147483647)
NEGATIVE_EPOCHALYPSE = EPOCH - timedelta(seconds=2147483648)


@pytest.mark.gettz
@pytest.mark.skipif(
    sys.version_info < (3, 6), reason="Not supported on Python 2"
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
@example(dt=datetime(2005, 10, 30, 1, 15))  # Ambiguous in US time zones
# The strategy above yields UTC-aware datetimes; keep this example aware
# too, so that it names an instant rather than a local wall time that
# lands outside the 32-bit range in zones east of UTC.
@example(dt=datetime(1901, 12, 13, 20, 45, 52, tzinfo=tz.UTC))
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
        assert (
            tz.enfold(dt, fold=0).astimezone().utcoffset()
            != tz.enfold(dt, fold=1).astimezone().utcoffset()
        )
        assert dt_act != dt_exp
