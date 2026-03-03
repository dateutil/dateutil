# --------- YOUR CODE -------------- #
from dateutil.relativedelta import relativedelta, MO


def next_monday(dt):
    next_meeting = dt + relativedelta(
        dt, weekday=MO, weeks=0, hour=10, minute=0, second=0, microsecond=0
    )
    if next_meeting < dt:
        next_meeting = next_meeting + relativedelta(weeks=1)
    return next_meeting


# ---------------------------------- #

from datetime import datetime
from dateutil import tz

NEXT_MONDAY_CASES = [
    (datetime(2018, 4, 11, 14, 30, 15, 123456), datetime(2018, 4, 16, 10, 0)),
    (datetime(2018, 4, 16, 10, 0), datetime(2018, 4, 16, 10, 0)),
    (datetime(2018, 4, 16, 10, 30), datetime(2018, 4, 23, 10, 0)),
    (
        datetime(2018, 4, 14, 9, 30, tzinfo=tz.gettz("America/New_York")),
        datetime(2018, 4, 16, 10, 0, tzinfo=tz.gettz("America/New_York")),
    ),
]


def test_next_monday_1():
    for dt_in, dt_out in NEXT_MONDAY_CASES:
        print(dt_in, dt_out, next_monday(dt_in))
        assert next_monday(dt_in) == dt_out


if __name__ == "__main__":
    test_next_monday_1()
    print("Success!")
