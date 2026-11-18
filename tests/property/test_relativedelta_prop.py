from datetime import datetime, timedelta

from hypothesis import given
from hypothesis import strategies as st

from dateutil.relativedelta import relativedelta

FIELDS = (
    "years",
    "months",
    "days",
    "hours",
    "minutes",
    "seconds",
    "microseconds",
)

# Whole months are counted from dt2, so swapping the arguments only negates
# the result when it has no months in it, i.e. under 28 days apart.
SHORT = timedelta(days=27)


@given(dt1=st.datetimes(), dt2=st.datetimes())
def test_difference_has_one_sign(dt1, dt2):
    rd = relativedelta(dt1, dt2)
    values = [getattr(rd, field) for field in FIELDS]

    if dt1 < dt2:
        assert max(values) <= 0, rd
    else:
        assert min(values) >= 0, rd

    assert dt2 + rd == dt1


@given(
    dt=st.datetimes(
        min_value=datetime.min + SHORT, max_value=datetime.max - SHORT
    ),
    delta=st.timedeltas(min_value=-SHORT, max_value=SHORT),
)
def test_short_difference_is_order_invariant(dt, delta):
    rd12 = relativedelta(dt + delta, dt)
    rd21 = relativedelta(dt, dt + delta)

    assert rd12 == -rd21
    assert abs(rd12) == abs(rd21)
