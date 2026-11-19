# --------- YOUR CODE -------------- #
from dateutil import tz
from dateutil.parser import parse

ISRAEL = tz.gettz("Asia/Jerusalem")
INDIA = tz.gettz("Asia/Kolkata")


def tzinfo_from_abbreviation(tzname, tzoffset):
    # "IDT" (Israel Daylight Time) is unambiguous.
    if tzname == "IDT":
        return ISRAEL

    # "IST" is India Standard Time (+05:30) in India and Israel Standard
    # Time (+02:00) in Israel. dateutil hands over the offset attached to
    # the name with the sign reversed ("IST+05:30" arrives as -19800), so
    # the absolute value is what distinguishes the two cases. A bare "IST"
    # has no offset, and the exercise asks for India in that case.
    if tzoffset is None or abs(tzoffset) == 19800:
        return INDIA

    return ISRAEL


def parse_func_ind_isr(dtstr):
    return parse(dtstr, tzinfos=tzinfo_from_abbreviation)


# ---------------------------------- #
from datetime import datetime

PARSE_IXT_TEST_CASE = [
    ("2018-02-03 12:00 IST+02:00", datetime(2018, 2, 3, 12, tzinfo=ISRAEL)),
    ("2018-06-14 12:00 IDT+03:00", datetime(2018, 6, 14, 12, tzinfo=ISRAEL)),
    ("2018-06-14 12:00 IST", datetime(2018, 6, 14, 12, tzinfo=INDIA)),
    ("2018-06-14 12:00 IST+05:30", datetime(2018, 6, 14, 12, tzinfo=INDIA)),
    ("2018-02-03 12:00 IST", datetime(2018, 2, 3, 12, tzinfo=INDIA)),
]


def test_parse_ixt():
    for dtstr, dt_exp in PARSE_IXT_TEST_CASE:
        dt_act = parse_func_ind_isr(dtstr)
        assert dt_act == dt_exp, (dt_act, dt_exp)
        assert dt_act.tzinfo is dt_exp.tzinfo, (dt_act, dt_exp)


if __name__ == "__main__":
    test_parse_ixt()
    print("Success!")
