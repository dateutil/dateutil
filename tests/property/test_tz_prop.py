import sys
from datetime import datetime, timedelta

import pytest
from hypothesis import assume, example, given
from hypothesis import strategies as st

from dateutil import tz

# hypothesis' st.datetimes() requires naive min_value/max_value, but we still
# derive them from UTC (rather than the environment-dependent, naive-local
# datetime.fromtimestamp()) and then strip tzinfo. `tz.UTC` is used instead of
# datetime.timezone.utc so this stays importable on Python 2. The datetimes
# generated below are UTC (see `timezones=st.just(tz.UTC)`), and tzfile's
# transition table is bounded by a transition derived from the 32-bit
# timestamp min, expressed in UTC. Computing the bound via local time can
# shift it by the local UTC offset, letting examples fall into the narrow
# pre-first-transition window where tzfile intentionally reports "LMT" for a
# date the system zoneinfo/libc resolves to the zone's standard abbreviation
# (e.g. 'EST' for America/New_York, which is what CI runs under); see the
# tzfile docstring.
EPOCHALYPSE = (
    datetime(1970, 1, 1, tzinfo=tz.UTC) + timedelta(seconds=2147483647)
).replace(tzinfo=None)
NEGATIVE_EPOCHALYPSE = (
    datetime(1970, 1, 1, tzinfo=tz.UTC) - timedelta(seconds=2147483648)
).replace(tzinfo=None)


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
@example(dt=NEGATIVE_EPOCHALYPSE)  # Very old
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
        # `dt` is UTC, which is never fold-ambiguous, so enfolding it has no
        # effect on the local time it converts to; re-derive the local wall
        # time's ambiguity from its own (naive) representation instead, the
        # same way a directly-supplied naive local datetime would be folded.
        dt_exp_naive = dt_exp.replace(tzinfo=None)
        assert (
            tz.enfold(dt_exp_naive, fold=0).astimezone().utcoffset()
            != tz.enfold(dt_exp_naive, fold=1).astimezone().utcoffset()
        )
        assert dt_act != dt_exp
