import sys
from datetime import datetime, timedelta

import pytest
from hypothesis import assume, example, given
from hypothesis import strategies as st

from dateutil import tz

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
@example(
    dt=datetime(2005, 10, 30, 5, 15, tzinfo=tz.UTC)
)  # Ambiguous in US time zones
@example(dt=datetime(1975, 10, 26, 5, tzinfo=tz.UTC))  # Aware ambiguous time
@example(dt=NEGATIVE_EPOCHALYPSE.replace(tzinfo=tz.UTC))  # Very old
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
        assert dt_act != dt_exp
