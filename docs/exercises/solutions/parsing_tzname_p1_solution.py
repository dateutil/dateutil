# --------- YOUR CODE -------------- #
from dateutil import tz
from dateutil.parser import parse

NEW_YORK = tz.gettz("America/New_York")
CHICAGO = tz.gettz("America/Chicago")
DENVER = tz.gettz("America/Denver")
LOS_ANGELES = tz.gettz("America/Los_Angeles")
INDIA = tz.gettz("Asia/Kolkata")
TOKYO = tz.gettz("Asia/Tokyo")

# Every abbreviation that can show up in a %Z-formatted string for these
# zones needs an entry: CST and CDT both refer to America/Chicago, and so on.
TZINFOS = {
    "EST": NEW_YORK,
    "EDT": NEW_YORK,
    "CST": CHICAGO,
    "CDT": CHICAGO,
    "MST": DENVER,
    "MDT": DENVER,
    "PST": LOS_ANGELES,
    "PDT": LOS_ANGELES,
    "IST": INDIA,
    "JST": TOKYO,
}


def parse_func_us_jp_ind(dtstr):
    return parse(dtstr, tzinfos=TZINFOS)


# ---------------------------------- #

from datetime import datetime

PARSE_TZ_TEST_DATETIMES = [
    datetime(2018, 1, 1, 12, 0),
    datetime(2018, 3, 20, 2, 0),
    datetime(2018, 5, 12, 3, 30),
    datetime(2014, 9, 1, 23),
]

PARSE_TZ_TEST_ZONES = [
    tz.gettz("America/New_York"),
    tz.gettz("America/Chicago"),
    tz.gettz("America/Denver"),
    tz.gettz("America/Los_Angeles"),
    tz.gettz("Asia/Kolkata"),
    tz.gettz("Asia/Tokyo"),
]


def test_parse():
    for tzi in PARSE_TZ_TEST_ZONES:
        for dt in PARSE_TZ_TEST_DATETIMES:
            dt_exp = dt.replace(tzinfo=tzi)
            dtstr = dt_exp.strftime("%Y-%m-%d %H:%M:%S %Z")

            dt_act = parse_func_us_jp_ind(dtstr)
            assert dt_act == dt_exp
            assert dt_act.tzinfo is dt_exp.tzinfo


if __name__ == "__main__":
    test_parse()
    print("Success!")
