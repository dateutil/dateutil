# ------- YOUR CODE -------------#
from dateutil import rrule
from datetime import datetime

MLK_DAY = rrule.rrule(
    dtstart=datetime(1986, 1, 20),      # First celebration
    freq=rrule.YEARLY,                  # Occurs once per year
    bymonth=1,                          # In January
    byweekday=rrule.MO(+3),             # On the 3rd Monday
)

# -------------------------------#

from datetime import datetime

MLK_TEST_CASES = [
    ((datetime(1970, 1, 1), datetime(1980, 1, 1)),
     []),
    ((datetime(1980, 1, 1), datetime(1989, 1, 1)),
     [datetime(1986, 1, 20),
      datetime(1987, 1, 19),
      datetime(1988, 1, 18)]),
    ((datetime(2017, 2, 1), datetime(2022, 2, 1)),
     [datetime(2018, 1, 15, 0, 0),
      datetime(2019, 1, 21, 0, 0),
      datetime(2020, 1, 20, 0, 0),
      datetime(2021, 1, 18, 0, 0),
      datetime(2022, 1, 17, 0, 0)]
     ),
]


def test_mlk_day():
    for (between_args, expected) in MLK_TEST_CASES:
        assert MLK_DAY.between(*between_args) == expected


if __name__ == "__main__":
    test_mlk_day()
    print('Success!')
