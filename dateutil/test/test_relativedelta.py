# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ._common import NotAValue

import calendar
from datetime import datetime, date, timedelta

import pytest

from dateutil.relativedelta import relativedelta, MO, TU, WE, FR, SU

NOW = datetime(2003, 9, 17, 20, 54, 47, 282310)
TODAY = date(2003, 9, 17)


def test_relative_delta_inheritance():
    # Ensure that relativedelta is inheritance-friendly.
    class rdChildClass(relativedelta):
        pass

    ccRD = rdChildClass(years=1, months=1, days=1, leapdays=1, weeks=1,
                        hours=1, minutes=1, seconds=1, microseconds=1)

    rd = relativedelta(years=1, months=1, days=1, leapdays=1, weeks=1,
                       hours=1, minutes=1, seconds=1, microseconds=1)

    assert type(ccRD + rd) == type(ccRD), 'Addition does not inherit type.'

    assert type(ccRD - rd) == type(ccRD), 'Subtraction does not inherit type.'

    assert type(-ccRD) == type(ccRD), 'Negation does not inherit type.'

    assert type(ccRD * 5.0) == type(ccRD), 'Multiplication does not inherit type.'

    assert type(ccRD / 5.0) == type(ccRD), 'Division does not inherit type.'


def test_relative_delta_month_end_month_beginning():
    assert relativedelta(datetime(2003, 1, 31, 23, 59, 59), datetime(2003, 3, 1, 0, 0, 0)) == relativedelta(months=-1,
                                                                                                            seconds=-1)

    assert relativedelta(datetime(2003, 3, 1, 0, 0, 0), datetime(2003, 1, 31, 23, 59, 59)) == relativedelta(months=1,
                                                                                                            seconds=1)


def test_relative_delta_month_end_month_beginning_leap_year():
    assert relativedelta(datetime(2012, 1, 31, 23, 59, 59), datetime(2012, 3, 1, 0, 0, 0)) == relativedelta(months=-1,
                                                                                                            seconds=-1)

    assert relativedelta(datetime(2003, 3, 1, 0, 0, 0), datetime(2003, 1, 31, 23, 59, 59)) == relativedelta(months=1,
                                                                                                            seconds=1)


def test_relative_delta_next_month():
    assert NOW + relativedelta(months=+1) == datetime(2003, 10, 17, 20, 54, 47, 282310)


def test_relative_delta_next_month_plus_one_week():
    assert NOW + relativedelta(months=+1, weeks=+1) == datetime(2003, 10, 24, 20, 54, 47, 282310)


def test_relative_delta_next_month_plus_one_week_10am():
    assert TODAY + relativedelta(months=+1, weeks=+1, hour=10) == datetime(2003, 10, 24, 10, 0)


def test_relative_delta_next_month_plus_one_week_10am_diff():
    assert relativedelta(datetime(2003, 10, 24, 10, 0), TODAY) == relativedelta(months=+1, days=+7, hours=+10)


def test_relative_delta_one_month_before_one_year():
    assert NOW + relativedelta(years=+1, months=-1) == datetime(2004, 8, 17, 20, 54, 47, 282310)


def test_relative_delta_months_of_diff_num_of_days():
    assert date(2003, 1, 27) + relativedelta(months=+1) == date(2003, 2, 27)
    assert date(2003, 1, 31) + relativedelta(months=+1) == date(2003, 2, 28)
    assert date(2003, 1, 31) + relativedelta(months=+2) == date(2003, 3, 31)


def test_relative_delta_months_of_diff_num_of_days_with_years():
    assert date(2000, 2, 28) + relativedelta(years=+1) == date(2001, 2, 28)
    assert date(2000, 2, 29) + relativedelta(years=+1) == date(2001, 2, 28)

    assert date(1999, 2, 28) + relativedelta(years=+1) == date(2000, 2, 28)
    assert date(1999, 3, 1) + relativedelta(years=+1) == date(2000, 3, 1)
    assert date(1999, 3, 1) + relativedelta(years=+1) == date(2000, 3, 1)

    assert date(2001, 2, 28) + relativedelta(years=-1) == date(2000, 2, 28)
    assert date(2001, 3, 1) + relativedelta(years=-1) == date(2000, 3, 1)


def test_relative_delta_next_friday():
    assert TODAY + relativedelta(weekday=FR) == date(2003, 9, 19)


def test_relative_delta_next_friday_int():
    assert TODAY + relativedelta(weekday=calendar.FRIDAY) == date(2003, 9, 19)


def test_relative_delta_last_friday_in_this_month():
    assert TODAY + relativedelta(day=31, weekday=FR(-1)) == date(2003, 9, 26)


def test_relative_delta_next_wednesday_is_today():
    assert TODAY + relativedelta(weekday=WE) == date(2003, 9, 17)


def test_relative_delta_next_wenesday_not_today():
    assert TODAY + relativedelta(days=+1, weekday=WE) == date(2003, 9, 24)


def test_relative_delta_add_more_than12_months():
    assert date(2003, 12, 1) + relativedelta(months=+13) == date(2005, 1, 1)


def test_relative_delta_add_negative_months():
    assert date(2003, 1, 1) + relativedelta(months=-2) == date(2002, 11, 1)


def test_relative_delta_15th_iso_year_week():
    assert date(2003, 1, 1) + relativedelta(day=4, weeks=+14, weekday=MO(-1)) == date(2003, 4, 7)


def test_relative_delta_millennium_age():
    assert relativedelta(NOW, date(2001, 1, 1)) == relativedelta(years=+2, months=+8, days=+16,
                                                                 hours=+20, minutes=+54, seconds=+47,
                                                                 microseconds=+282310)


def test_relative_delta_john_age():
    assert relativedelta(NOW, datetime(1978, 4, 5, 12, 0)) == relativedelta(years=+25, months=+5, days=+12,
                                                                            hours=+8, minutes=+54, seconds=+47,
                                                                            microseconds=+282310)


def test_relative_delta_john_age_with_date():
    assert relativedelta(TODAY, datetime(1978, 4, 5, 12, 0)) == relativedelta(years=+25, months=+5, days=+11, hours=+12)


def test_relative_delta_year_day():
    assert date(2003, 1, 1)+relativedelta(yearday=260) == date(2003, 9, 17)
    assert date(2002, 1, 1)+relativedelta(yearday=260) == date(2002, 9, 17)
    assert date(2000, 1, 1)+relativedelta(yearday=260) == date(2000, 9, 16)
    assert TODAY + relativedelta(yearday=261) == date(2003, 9, 18)


def test_relative_delta_year_day_bug():
    # Tests a problem reported by Adam Ryan.
    assert date(2010, 1, 1)+relativedelta(yearday=15) == date(2010, 1, 15)


def test_relative_delta_non_leap_year_day():
    assert date(2003, 1, 1)+relativedelta(nlyearday=260) == date(2003, 9, 17)
    assert date(2002, 1, 1)+relativedelta(nlyearday=260) == date(2002, 9, 17)
    assert date(2000, 1, 1)+relativedelta(nlyearday=260) == date(2000, 9, 17)
    assert TODAY + relativedelta(yearday=261) == date(2003, 9, 18)


def test_relative_delta_addition():
    assert relativedelta(days=10) + relativedelta(years=1, months=2, days=3, hours=4, minutes=5, microseconds=6) == \
           relativedelta(years=1, months=2, days=13, hours=4, minutes=5, microseconds=6)


def test_relative_delta_absolute_addition():
    assert relativedelta() + relativedelta(day=0, hour=0) == relativedelta(day=0, hour=0)
    assert relativedelta(day=0, hour=0) + relativedelta() == relativedelta(day=0, hour=0)


def test_relative_delta_addition_to_datetime():
    assert datetime(2000, 1, 1) + relativedelta(days=1) == datetime(2000, 1, 2)


def test_relative_delta_right_addition_to_datetime():
    assert relativedelta(days=1) + datetime(2000, 1, 1) == datetime(2000, 1, 2)


def test_relative_delta_addition_invalid_type():
    with pytest.raises(TypeError):
        relativedelta(days=3) + 9


def test_relative_delta_addition_unsupported_type():
    # For unsupported types that define their own comparators, etc.
    assert relativedelta(days=1) + NotAValue is NotAValue


def test_relative_delta_addition_float_value():
    assert datetime(2000, 1, 1) + relativedelta(days=float(1)) == datetime(2000, 1, 2)
    assert datetime(2000, 1, 1) + relativedelta(months=float(1)) == datetime(2000, 2, 1)
    assert datetime(2000, 1, 1) + relativedelta(years=float(1)) == datetime(2001, 1, 1)


def test_relative_delta_addition_float_fractionals():
    assert datetime(2000, 1, 1, 0) + relativedelta(days=float(0.5)) == datetime(2000, 1, 1, 12)
    assert datetime(2000, 1, 1, 0, 0) + relativedelta(hours=float(0.5)) == datetime(2000, 1, 1, 0, 30)
    assert datetime(2000, 1, 1, 0, 0, 0) + relativedelta(minutes=float(0.5)) == datetime(2000, 1, 1, 0, 0, 30)
    assert datetime(2000, 1, 1, 0, 0, 0, 0) + relativedelta(seconds=float(0.5)) == datetime(2000, 1, 1, 0, 0, 0, 500000)

    assert datetime(2000, 1, 1, 0, 0, 0, 0) + relativedelta(microseconds=float(500000.25)) == \
           datetime(2000, 1, 1, 0, 0, 0, 500000)


def test_relative_delta_subtraction():
    assert relativedelta(days=10) - relativedelta(years=1, months=2, days=3, hours=4, minutes=5, microseconds=6) == \
           relativedelta(years=-1, months=-2, days=7, hours=-4, minutes=-5, microseconds=-6)


def test_relative_delta_right_subtraction_from_datetime():
    assert datetime(2000, 1, 2) - relativedelta(days=1) == datetime(2000, 1, 1)


def test_relative_delta_subraction_with_datetime():
    with pytest.raises(TypeError):
        relativedelta(days=1) -  datetime(2000, 1, 1)


def test_relative_delta_subtraction_invalid_type():
    with pytest.raises(TypeError):
        relativedelta(hours=12) - 14


def test_relative_delta_subtraction_unsupported_type():
    assert relativedelta(days=1) + NotAValue is  NotAValue


def test_relative_delta_multiplication():
    assert datetime(2000, 1, 1) + relativedelta(days=1) * 28 == datetime(2000, 1, 29)
    assert datetime(2000, 1, 1) + 28 * relativedelta(days=1) == datetime(2000, 1, 29)


def test_relative_delta_multiplication_unsupported_type():
    assert relativedelta(days=1) * NotAValue is NotAValue


def test_relative_delta_division():
    assert datetime(2000, 1, 1) + relativedelta(days=28) / 28 == datetime(2000, 1, 2)


def test_relative_delta_division_unsupported_type():
    assert relativedelta(days=1) / NotAValue is NotAValue


def test_relative_delta_boolean():
    assert not relativedelta(days=0)
    assert relativedelta(days=1)


def test_relative_delta_absolute_value_negative():
    rd_base = relativedelta(years=-1, months=-5, days=-2, hours=-3, minutes=-5, seconds=-2, microseconds=-12)
    rd_expected = relativedelta(years=1, months=5, days=2, hours=3, minutes=5, seconds=2, microseconds=12)
    assert abs(rd_base) == rd_expected


def test_relative_delta_absolute_value_positive():
    rd_base = relativedelta(years=1, months=5, days=2, hours=3, minutes=5, seconds=2, microseconds=12)
    rd_expected = rd_base

    assert abs(rd_base) == rd_expected


def test_relative_delta_comparison():
    d1 = relativedelta(years=1, months=1, days=1, leapdays=0, hours=1,
                        minutes=1, seconds=1, microseconds=1)
    d2 = relativedelta(years=1, months=1, days=1, leapdays=0, hours=1,
                        minutes=1, seconds=1, microseconds=1)
    d3 = relativedelta(years=1, months=1, days=1, leapdays=0, hours=1,
                        minutes=1, seconds=1, microseconds=2)

    assert d1 == d2
    assert d1 != d3


def test_relative_delta_inequality_type_mismatch():
    # Different type
    assert not relativedelta(year=1) == 19


def test_relative_delta_inequality_unsupported_type():
    assert (relativedelta(hours=3) == NotAValue) is NotAValue


def test_relative_delta_inequality_weekdays():
    # Different weekdays
    no_wday = relativedelta(year=1997, month=4)
    wday_mo_1 = relativedelta(year=1997, month=4, weekday=MO(+1))
    wday_mo_2 = relativedelta(year=1997, month=4, weekday=MO(+2))
    wday_tu = relativedelta(year=1997, month=4, weekday=TU)

    assert wday_mo_1 == wday_mo_1

    assert not no_wday == wday_mo_1
    assert not wday_mo_1 == no_wday

    assert not wday_mo_1 == wday_mo_2
    assert not wday_mo_2 == wday_mo_1

    assert not wday_mo_1 == wday_tu
    assert not wday_tu == wday_mo_1


def test_relative_delta_month_overflow():
    assert relativedelta(months=273) == relativedelta(years=22, months=9)


def test_relative_delta_weeks():
     # Test that the weeks property is working properly.
    rd = relativedelta(years=4, months=2, weeks=8, days=6)
    assert (rd.weeks, rd.days) == (8, 8 * 7 + 6)

    rd.weeks = 3
    assert (rd.weeks, rd.days) == (3, 3 * 7 + 6)


def test_relative_delta_relative_delta_repr():
    assert repr(relativedelta(years=1, months=-1, days=15)) == 'relativedelta(years=+1, months=-1, days=+15)'

    assert repr(relativedelta(months=14, seconds=-25)) == 'relativedelta(years=+1, months=+2, seconds=-25)'

    assert repr(relativedelta(month=3, hour=3, weekday=SU(3))) == 'relativedelta(month=3, weekday=SU(+3), hour=3)'


def test_relative_delta_relative_delta_fractional_year():
    with pytest.raises(ValueError):
        relativedelta(years=1.5)


def test_relative_delta_relative_delta_fractional_month():
     with pytest.raises(ValueError):
            relativedelta(months=1.5)


def test_relative_delta_relative_delta_invalid_datetime_object():
    with pytest.raises(TypeError):
        relativedelta(dt1='2018-01-01', dt2='2018-01-02')

    with pytest.raises(TypeError):
        relativedelta(dt1=datetime(2018, 1, 1), dt2='2018-01-02')

    with pytest.raises(TypeError):
        relativedelta(dt1='2018-01-01', dt2=datetime(2018, 1, 2))


def test_relative_delta_relative_delta_fractional_absolutes():
    # Fractional absolute values will soon be unsupported,
    # check for the deprecation warning.
    with pytest.warns(DeprecationWarning):
        relativedelta(year=2.86)

    with pytest.warns(DeprecationWarning):
        relativedelta(month=1.29)

    with pytest.warns(DeprecationWarning):
        relativedelta(day=0.44)

    with pytest.warns(DeprecationWarning):
        relativedelta(hour=23.98)

    with pytest.warns(DeprecationWarning):
        relativedelta(minute=45.21)

    with pytest.warns(DeprecationWarning):
        relativedelta(second=13.2)

    with pytest.warns(DeprecationWarning):
        relativedelta(microsecond=157221.93)


def test_relative_delta_relative_delta_fractional_repr():
    rd = relativedelta(years=3, months=-2, days=1.25)

    assert repr(rd) == 'relativedelta(years=+3, months=-2, days=+1.25)'

    rd = relativedelta(hours=0.5, seconds=9.22)
    assert repr(rd) == 'relativedelta(hours=+0.5, seconds=+9.22)'


def test_relative_delta_relative_delta_fractional_weeks():
    # Equivalent to days=8, hours=18
    rd = relativedelta(weeks=1.25)
    d1 = datetime(2009, 9, 3, 0, 0)
    assert d1 + rd == datetime(2009, 9, 11, 18)


def test_relative_delta_relative_delta_fractional_days():
    rd1 = relativedelta(days=1.48)

    d1 = datetime(2009, 9, 3, 0, 0)
    assert d1 + rd1 ==  datetime(2009, 9, 4, 11, 31, 12)

    rd2 = relativedelta(days=1.5)
    assert d1 + rd2 == datetime(2009, 9, 4, 12, 0, 0)


def test_relative_delta_relative_delta_fractional_hours():
    rd = relativedelta(days=1, hours=12.5)
    d1 = datetime(2009, 9, 3, 0, 0)
    assert d1 + rd == datetime(2009, 9, 4, 12, 30, 0)


def test_relative_delta_relative_delta_fractional_minutes():
    rd = relativedelta(hours=1, minutes=30.5)
    d1 = datetime(2009, 9, 3, 0, 0)
    assert d1 + rd == datetime(2009, 9, 3, 1, 30, 30)


def test_relative_delta_relative_delta_fractional_seconds():
    rd = relativedelta(hours=5, minutes=30, seconds=30.5)
    d1 = datetime(2009, 9, 3, 0, 0)
    assert d1 + rd == datetime(2009, 9, 3, 5, 30, 30, 500000)


def test_relative_delta_relative_delta_fractional_positive_overflow():
    # Equivalent to (days=1, hours=14)
    rd1 = relativedelta(days=1.5, hours=2)
    d1 = datetime(2009, 9, 3, 0, 0)
    assert d1 + rd1 == datetime(2009, 9, 4, 14, 0, 0)

    # Equivalent to (days=1, hours=14, minutes=45)
    rd2 = relativedelta(days=1.5, hours=2.5, minutes=15)
    d1 = datetime(2009, 9, 3, 0, 0)
    assert d1 + rd2 == datetime(2009, 9, 4, 14, 45)

    # Carry back up - equivalent to (days=2, hours=2, minutes=0, seconds=1)
    rd3 = relativedelta(days=1.5, hours=13, minutes=59.5, seconds=31)
    assert d1 + rd3 == datetime(2009, 9, 5, 2, 0, 1)


def test_relative_delta_relative_delta_fractional_negative_days():
    # Equivalent to (days=-1, hours=-1)
    rd1 = relativedelta(days=-1.5, hours=11)
    d1 = datetime(2009, 9, 3, 12, 0)
    assert d1 + rd1 == datetime(2009, 9, 2, 11, 0, 0)

    # Equivalent to (days=-1, hours=-9)
    rd2 = relativedelta(days=-1.25, hours=-3)
    assert d1 + rd2 == datetime(2009, 9, 2, 3)


def test_relative_delta_relative_delta_normalize_fractional_days():
    # Equivalent to (days=2, hours=18)
    rd1 = relativedelta(days=2.75)

    assert rd1.normalized() == relativedelta(days=2, hours=18)

    # Equivalent to (days=1, hours=11, minutes=31, seconds=12)
    rd2 = relativedelta(days=1.48)

    assert rd2.normalized() == relativedelta(days=1, hours=11, minutes=31, seconds=12)


def test_relative_delta_relative_delta_normalize_fractional_days2():
    # Equivalent to (hours=1, minutes=30)
    rd1 = relativedelta(hours=1.5)

    assert rd1.normalized(), relativedelta(hours=1, minutes=30)

    # Equivalent to (hours=3, minutes=17, seconds=5, microseconds=100)
    rd2 = relativedelta(hours=3.28472225)

    assert rd2.normalized() == relativedelta(hours=3, minutes=17, seconds=5, microseconds=100)


def test_relative_delta_relative_delta_normalize_fractional_minutes():
    # Equivalent to (minutes=15, seconds=36)
    rd1 = relativedelta(minutes=15.6)

    assert rd1.normalized() == relativedelta(minutes=15, seconds=36)

    # Equivalent to (minutes=25, seconds=20, microseconds=25000)
    rd2 = relativedelta(minutes=25.33375)

    assert rd2.normalized() == relativedelta(minutes=25, seconds=20, microseconds=25000)

def test_relative_delta_relative_delta_normalize_fractional_seconds():
    # Equivalent to (seconds=45, microseconds=25000)
    rd1 = relativedelta(seconds=45.025)
    assert rd1.normalized() == relativedelta(seconds=45, microseconds=25000)


def test_relative_delta_relative_delta_fractional_positive_overflow2():
    # Equivalent to (days=1, hours=14)
    rd1 = relativedelta(days=1.5, hours=2)
    assert rd1.normalized() == relativedelta(days=1, hours=14)

    # Equivalent to (days=1, hours=14, minutes=45)
    rd2 = relativedelta(days=1.5, hours=2.5, minutes=15)
    assert rd2.normalized() == relativedelta(days=1, hours=14, minutes=45)

    # Carry back up - equivalent to:
    # (days=2, hours=2, minutes=0, seconds=2, microseconds=3)
    rd3 = relativedelta(days=1.5, hours=13, minutes=59.50045, seconds=31.473, microseconds=500003)
    assert rd3.normalized() == relativedelta(days=2, hours=2, minutes=0, seconds=2, microseconds=3)


def test_relative_delta_relative_delta_fractional_negative_overflow():
    # Equivalent to (days=-1)
    rd1 = relativedelta(days=-0.5, hours=-12)
    assert rd1.normalized() == relativedelta(days=-1)

    # Equivalent to (days=-1)
    rd2 = relativedelta(days=-1.5, hours=12)
    assert rd2.normalized() == relativedelta(days=-1)

    # Equivalent to (days=-1, hours=-14, minutes=-45)
    rd3 = relativedelta(days=-1.5, hours=-2.5, minutes=-15)
    assert rd3.normalized() == relativedelta(days=-1, hours=-14, minutes=-45)

    # Equivalent to (days=-1, hours=-14, minutes=+15)
    rd4 = relativedelta(days=-1.5, hours=-2.5, minutes=45)
    assert rd4.normalized() == relativedelta(days=-1, hours=-14, minutes=+15)

    # Carry back up - equivalent to:
    # (days=-2, hours=-2, minutes=0, seconds=-2, microseconds=-3)
    rd3 = relativedelta(days=-1.5, hours=-13, minutes=-59.50045, seconds=-31.473, microseconds=-500003)
    assert rd3.normalized() == relativedelta(days=-2, hours=-2, minutes=0, seconds=-2, microseconds=-3)


def test_relative_delta_invalid_year_day():
    with pytest.raises (ValueError):
        relativedelta(yearday=367)


def test_relative_delta_add_timedelta_to_unpopulated_relativedelta():
    td = timedelta(
        days=1,
        seconds=1,
        microseconds=1,
        milliseconds=1,
        minutes=1,
        hours=1,
        weeks=1
    )

    expected = relativedelta(
        weeks=1,
        days=1,
        hours=1,
        minutes=1,
        seconds=1,
        microseconds=1001
    )

    assert expected ==  relativedelta() + td


def test_relative_delta_add_timedelta_to_populated_relative_delta():
    td = timedelta(
        days=1,
        seconds=1,
        microseconds=1,
        milliseconds=1,
        minutes=1,
        hours=1,
        weeks=1
    )

    rd = relativedelta(
        year=1,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        microsecond=1,
        years=1,
        months=1,
        days=1,
        weeks=1,
        hours=1,
        minutes=1,
        seconds=1,
        microseconds=1
    )

    expected = relativedelta(
        year=1,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        microsecond=1,
        years=1,
        months=1,
        weeks=2,
        days=2,
        hours=2,
        minutes=2,
        seconds=2,
        microseconds=1002,
    )

    assert expected == rd + td


def test_relative_delta_hashable():
    try:
        {relativedelta(minute=1): 'test'}
    except:
        pytest.fail("relativedelta() failed to hash!")


# Test the weeks property getter
def test_relative_delta_weeks_getter_one_day():
    rd = relativedelta(days=1)
    assert rd.days == 1
    assert rd.weeks == 0


def test_relative_delta_weeks_getter_minus_on_day():
    rd = relativedelta(days=-1)
    assert rd.days == -1
    assert rd.weeks == 0


def test_relative_delta_weeks_getter_height_days():
    rd = relativedelta(days=8)
    assert rd.days == 8
    assert rd.weeks == 1


def test_relative_delta_weeks_getter_minus_height_days():
    rd = relativedelta(days=-8)
    assert rd.days == -8
    assert rd.weeks == -1


# Test the weeks setter which makes a "smart" update of the days attribute
def test_relative_delta_weeks_setter_one_day_set_one_week():
    rd = relativedelta(days=1)
    rd.weeks = 1  # add 7 days
    assert rd.days == 8
    assert rd.weeks == 1


def test_relative_delta_weeks_setter_minus_one_day_set_one_week():
    rd = relativedelta(days=-1)
    rd.weeks = 1  # add 7 days
    assert rd.days == 6
    assert rd.weeks == 0


def test_relative_delta_weeks_setter_height_days_set_minus_one_week():
    rd = relativedelta(days=8)
    rd.weeks = -1  # change from 1 week, 1 day to -1 week, 1 day
    assert rd.days == -6
    assert rd.weeks == 0


def test_relative_delta_weeks_setter_minus_height_days_set_minus_one_week():
    rd = relativedelta(days=-8)
    rd.weeks = -1  # does not change anything
    assert rd.days == -8
    assert rd.weeks == -1

# vim:ts=4:sw=4:et
