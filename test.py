#!/usr/bin/python
import unittest
from cStringIO import StringIO
import base64
import os

# Add build directory to search path
if os.path.exists("build"):
	from distutils.util import get_platform
	import sys
	s = "build/lib.%s-%.3s" % (get_platform(), sys.version)
	s = os.path.join(os.getcwd(), s)
	sys.path.insert(0,s)

from dateutil.relativedelta import *
from dateutil.parser import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.tz import *

from datetime import *

import calendar
import time

class RelativeDeltaTest(unittest.TestCase):
    now = datetime(2003, 9, 17, 20, 54, 47, 282310)
    today = date(2003, 9, 17)

    def testNextMonth(self):
        self.assertEqual(self.now+relativedelta(months=+1),
                         datetime(2003, 10, 17, 20, 54, 47, 282310))

    def testNextMonthPlusOneWeek(self):
        self.assertEqual(self.now+relativedelta(months=+1, weeks=+1),
                         datetime(2003, 10, 24, 20, 54, 47, 282310))
    def testNextMonthPlusOneWeek10am(self):
        self.assertEqual(self.today +
                         relativedelta(months=+1, weeks=+1, hour=10),
                         datetime(2003, 10, 24, 10, 0))

    def testNextMonthPlusOneWeek10amDiff(self):
        self.assertEqual(relativedelta(datetime(2003, 10, 24, 10, 0),
                                       self.today),
                         relativedelta(months=+1, days=+7, hours=+10))

    def testOneMonthBeforeOneYear(self):
        self.assertEqual(self.now+relativedelta(years=+1, months=-1),
                         datetime(2004, 8, 17, 20, 54, 47, 282310))

    def testMonthsOfDiffNumOfDays(self):
        self.assertEqual(date(2003, 1, 27)+relativedelta(months=+1),
                         date(2003, 2, 27))
        self.assertEqual(date(2003, 1, 31)+relativedelta(months=+1),
                         date(2003, 2, 28))
        self.assertEqual(date(2003, 1, 31)+relativedelta(months=+2),
                         date(2003, 3, 31))

    def testMonthsOfDiffNumOfDaysWithYears(self):
        self.assertEqual(date(2000, 2, 28)+relativedelta(years=+1),
                         date(2001, 2, 28))
        self.assertEqual(date(2000, 2, 29)+relativedelta(years=+1),
                         date(2001, 2, 28))

        self.assertEqual(date(1999, 2, 28)+relativedelta(years=+1),
                         date(2000, 2, 28))
        self.assertEqual(date(1999, 3, 1)+relativedelta(years=+1),
                         date(2000, 3, 1))
        self.assertEqual(date(1999, 3, 1)+relativedelta(years=+1),
                         date(2000, 3, 1))

        self.assertEqual(date(2001, 2, 28)+relativedelta(years=-1),
                         date(2000, 2, 28))
        self.assertEqual(date(2001, 3, 1)+relativedelta(years=-1),
                         date(2000, 3, 1))

    def testNextFriday(self):
        self.assertEqual(self.today+relativedelta(weekday=FR),
                         date(2003, 9, 19))

    def testNextFridayInt(self):
        self.assertEqual(self.today+relativedelta(weekday=calendar.FRIDAY),
                         date(2003, 9, 19))

    def testLastFridayInThisMonth(self):
        self.assertEqual(self.today+relativedelta(day=31, weekday=FR(-1)),
                         date(2003, 9, 26))

    def testNextWednesdayIsToday(self):
        self.assertEqual(self.today+relativedelta(weekday=WE),
                         date(2003, 9, 17))


    def testNextWenesdayNotToday(self):
        self.assertEqual(self.today+relativedelta(days=+1, weekday=WE),
                         date(2003, 9, 24))
        
    def test15thISOYearWeek(self):
        self.assertEqual(date(2003, 1, 1) +
                         relativedelta(day=4, weeks=+14, weekday=MO(-1)),
                         date(2003, 4, 7))

    def testMillenniumAge(self):
        self.assertEqual(relativedelta(self.now, date(2001,1,1)),
                         relativedelta(years=+2, months=+8, days=+16,
                                       hours=+20, minutes=+54, seconds=+47,
                                       microseconds=+282310))

    def testJohnAge(self):
        self.assertEqual(relativedelta(self.now,
                                       datetime(1978, 4, 5, 12, 0)),
                         relativedelta(years=+25, months=+5, days=+12,
                                       hours=+8, minutes=+54, seconds=+47,
                                       microseconds=+282310))

    def testJohnAgeWithDate(self):
        self.assertEqual(relativedelta(self.today,
                                       datetime(1978, 4, 5, 12, 0)),
                         relativedelta(years=+25, months=+5, days=+11,
                                       hours=+12))

    def testYearDay(self):
        self.assertEqual(date(2003, 1, 1)+relativedelta(yearday=260),
                         date(2003, 9, 17))
        self.assertEqual(date(2002, 1, 1)+relativedelta(yearday=260),
                         date(2002, 9, 17))
        self.assertEqual(date(2000, 1, 1)+relativedelta(yearday=260),
                         date(2000, 9, 16))
        self.assertEqual(self.today+relativedelta(yearday=261),
                         date(2003, 9, 18))

    def testNonLeapYearDay(self):
        self.assertEqual(date(2003, 1, 1)+relativedelta(nlyearday=260),
                         date(2003, 9, 17))
        self.assertEqual(date(2002, 1, 1)+relativedelta(nlyearday=260),
                         date(2002, 9, 17))
        self.assertEqual(date(2000, 1, 1)+relativedelta(nlyearday=260),
                         date(2000, 9, 17))
        self.assertEqual(self.today+relativedelta(yearday=261),
                         date(2003, 9, 18))

class RRuleTest(unittest.TestCase):

    def testYearly(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrYearly(self):
        self.assertEqual(list(rrulestr("""
                              DTSTART:19970902T090000
                              RRULE:FREQ=YEARLY;COUNT=3
                              """)),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testYearlyInterval(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0),
                          datetime(2001, 9, 2, 9, 0)])

    def testYearlyIntervalLarge(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              interval=100,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(2097, 9, 2, 9, 0),
                          datetime(2197, 9, 2, 9, 0)])

    def testYearlyByMonth(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 2, 9, 0),
                          datetime(1998, 3, 2, 9, 0),
                          datetime(1999, 1, 2, 9, 0)])

    def testYearlyByMonthDay(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testYearlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testYearlyByWeekDay(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testYearlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(FREQ_YEARLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testMonthly(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 10, 2, 9, 0),
                          datetime(1997, 11, 2, 9, 0)])

    def testStrMonthly(self):
        self.assertEqual(list(rrulestr("""
                              DTSTART:19970902T090000
                              RRULE:FREQ=MONTHLY;COUNT=3
                              """)),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 10, 2, 9, 0),
                          datetime(1997, 11, 2, 9, 0)])

    def testMonthlyInterval(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 11, 2, 9, 0),
                          datetime(1998, 1, 2, 9, 0)])

    def testMonthlyIntervalLarge(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              interval=18,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1999, 3, 2, 9, 0),
                          datetime(2000, 9, 2, 9, 0)])

    def testMonthlyByMonth(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 2, 9, 0),
                          datetime(1998, 3, 2, 9, 0),
                          datetime(1999, 1, 2, 9, 0)])


    def testMonthlyByMonthDay(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testMonthlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testMonthlyByWeekDay(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testMonthlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(FREQ_MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testWeekly(self):
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testStrWeekly(self):
        self.assertEqual(list(rrulestr("""
                              DTSTART:19970902T090000
                              RRULE:FREQ=WEEKLY;COUNT=3
                              """)),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testWeeklyInterval(self):
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 16, 9, 0),
                          datetime(1997, 9, 30, 9, 0)])

    def testWeeklyIntervalLarge(self):
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              interval=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 1, 20, 9, 0),
                          datetime(1998, 6, 9, 9, 0)])

    def testWeeklyByMonth(self):
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 13, 9, 0),
                          datetime(1998, 1, 20, 9, 0)])

    def testWeeklyByMonthDay(self):
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testWeeklyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testWeeklyByWeekDay(self):
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testWeeklyByMonthAndWeekDay(self):
        # This test is interesting, because it crosses the year
        # boundary in a weekly period to find day '1' as a
        # valid recurrence.
        self.assertEqual(list(rrule(FREQ_WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testDaily(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testStrDaily(self):
        self.assertEqual(list(rrulestr("""
                              DTSTART:19970902T090000
                              RRULE:FREQ=DAILY;COUNT=3
                              """)),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testDailyInterval(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 6, 9, 0)])

    def testDailyIntervalLarge(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              interval=92,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 12, 3, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testDailyByMonth(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 2, 9, 0),
                          datetime(1998, 1, 3, 9, 0)])

    def testDailyByMonthDay(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testDailyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testDailyByWeekDay(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testDailyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testHourly(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 10, 0),
                          datetime(1997, 9, 2, 11, 0)])

    def testStrHourly(self):
        self.assertEqual(list(rrulestr("""
                              DTSTART:19970902T090000
                              RRULE:FREQ=HOURLY;COUNT=3
                              """)),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 10, 0),
                          datetime(1997, 9, 2, 11, 0)])

    def testHourlyInterval(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 11, 0),
                          datetime(1997, 9, 2, 13, 0)])

    def testHourlyIntervalLarge(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              interval=769,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 10, 4, 10, 0),
                          datetime(1997, 11, 5, 11, 0)])

    def testHourlyByMonth(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 1, 0),
                          datetime(1998, 1, 1, 2, 0)])

    def testHourlyByMonthDay(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 0, 0),
                          datetime(1997, 9, 3, 1, 0),
                          datetime(1997, 9, 3, 2, 0)])

    def testHourlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 0, 0),
                          datetime(1998, 1, 5, 1, 0),
                          datetime(1998, 1, 5, 2, 0)])

    def testHourlyByWeekDay(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 10, 0),
                          datetime(1997, 9, 2, 11, 0)])

    def testHourlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(FREQ_HOURLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 1, 0),
                          datetime(1998, 1, 1, 2, 0)])

    def testMinutely(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 1),
                          datetime(1997, 9, 2, 9, 2)])

    def testStrMinutely(self):
        self.assertEqual(list(rrulestr("""
                              DTSTART:19970902T090000
                              RRULE:FREQ=MINUTELY;COUNT=3
                              """)),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 1),
                          datetime(1997, 9, 2, 9, 2)])

    def testMinutelyInterval(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 2),
                          datetime(1997, 9, 2, 9, 4)])

    def testMinutelyIntervalLarge(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              interval=1501,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 10, 1),
                          datetime(1997, 9, 4, 11, 2)])

    def testMinutelyByMonth(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 0, 1),
                          datetime(1998, 1, 1, 0, 2)])

    def testMinutelyByMonthDay(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 0, 0),
                          datetime(1997, 9, 3, 0, 1),
                          datetime(1997, 9, 3, 0, 2)])

    def testMinutelyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 0, 0),
                          datetime(1998, 1, 5, 0, 1),
                          datetime(1998, 1, 5, 0, 2)])

    def testMinutelyByWeekDay(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 1),
                          datetime(1997, 9, 2, 9, 2)])

    def testMinutelyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(FREQ_MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 0, 1),
                          datetime(1998, 1, 1, 0, 2)])

    def testSecondly(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 1),
                          datetime(1997, 9, 2, 9, 0, 2)])

    def testStrSecondly(self):
        self.assertEqual(list(rrulestr("""
                              DTSTART:19970902T090000
                              RRULE:FREQ=SECONDLY;COUNT=3
                              """)),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 1),
                          datetime(1997, 9, 2, 9, 0, 2)])

    def testSecondlyInterval(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 2),
                          datetime(1997, 9, 2, 9, 0, 4)])

    def testSecondlyIntervalLarge(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              interval=90061,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 3, 10, 1, 1),
                          datetime(1997, 9, 4, 11, 2, 2)])

    def testSecondlyByMonth(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0, 0),
                          datetime(1998, 1, 1, 0, 0, 1),
                          datetime(1998, 1, 1, 0, 0, 2)])

    def testSecondlyByMonthDay(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 0, 0, 0),
                          datetime(1997, 9, 3, 0, 0, 1),
                          datetime(1997, 9, 3, 0, 0, 2)])

    def testSecondlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 0, 0, 0),
                          datetime(1998, 1, 5, 0, 0, 1),
                          datetime(1998, 1, 5, 0, 0, 2)])

    def testSecondlyByWeekDay(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 1),
                          datetime(1997, 9, 2, 9, 0, 2)])

    def testSecondlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(FREQ_SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0, 0),
                          datetime(1998, 1, 1, 0, 0, 1),
                          datetime(1998, 1, 1, 0, 0, 2)])

    def testUntilNotMatching(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970905T080000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testUntilMatching(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970904T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testUntilSingle(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0)])

    def testUntilEmpty(self):
        self.assertEqual(list(rrule(FREQ_DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970901T090000"))),
                         [])

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.tzinfos = {"BRST": -10800}
        self.brsttz = tzoffset("BRST", -10800)
        self.default = datetime(2003, 9, 25)

    def testDateCommandFormat(self):
        self.assertEqual(parse("Thu Sep 25 10:36:28 BRST 2003",
                               tzinfos=self.tzinfos),
                         datetime(2003, 9, 25, 10, 36, 28,
                                  tzinfo=self.brsttz))

    def testDateCommandFormatReversed(self):
        self.assertEqual(parse("2003 10:36:28 BRST 25 Sep Thu",
                               tzinfos=self.tzinfos),
                         datetime(2003, 9, 25, 10, 36, 28,
                                  tzinfo=self.brsttz))

    def testDateCommandFormatIgnoreTz(self):
        self.assertEqual(parse("Thu Sep 25 10:36:28 BRST 2003",
                               ignoretz=True),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testDateCommandFormatStrip1(self):
        self.assertEqual(parse("Thu Sep 25 10:36:28 2003"),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testDateCommandFormatStrip2(self):
        self.assertEqual(parse("Thu Sep 25 10:36:28", default=self.default),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testDateCommandFormatStrip3(self):
        self.assertEqual(parse("Thu Sep 10:36:28", default=self.default),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testDateCommandFormatStrip4(self):
        self.assertEqual(parse("Thu 10:36:28", default=self.default),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testDateCommandFormatStrip5(self):
        self.assertEqual(parse("Sep 10:36:28", default=self.default),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testDateCommandFormatStrip6(self):
        self.assertEqual(parse("10:36:28", default=self.default),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testDateCommandFormatStrip7(self):
        self.assertEqual(parse("10:36", default=self.default),
                         datetime(2003, 9, 25, 10, 36))

    def testDateCommandFormatStrip8(self):
        self.assertEqual(parse("Thu Sep 25 2003"),
                         datetime(2003, 9, 25))

    def testDateCommandFormatStrip9(self):
        self.assertEqual(parse("Sep 25 2003"),
                         datetime(2003, 9, 25))

    def testDateCommandFormatStrip9(self):
        self.assertEqual(parse("Sep 2003", default=self.default),
                         datetime(2003, 9, 25))

    def testDateCommandFormatStrip10(self):
        self.assertEqual(parse("Sep", default=self.default),
                         datetime(2003, 9, 25))

    def testDateCommandFormatStrip11(self):
        self.assertEqual(parse("2003", default=self.default),
                         datetime(2003, 9, 25))

    def testDateRCommandFormat(self):
        self.assertEqual(parse("Thu, 25 Sep 2003 10:49:41 -0300"),
                         datetime(2003, 9, 25, 10, 49, 41,
                                  tzinfo=self.brsttz))

    def testISOFormat(self):
        self.assertEqual(parse("2003-09-25T10:49:41.5-03:00"),
                         datetime(2003, 9, 25, 10, 49, 41, 500000,
                                  tzinfo=self.brsttz))

    def testISOFormatStrip1(self):
        self.assertEqual(parse("2003-09-25T10:49:41-03:00"),
                         datetime(2003, 9, 25, 10, 49, 41,
                                  tzinfo=self.brsttz))

    def testISOFormatStrip2(self):
        self.assertEqual(parse("2003-09-25T10:49:41"),
                         datetime(2003, 9, 25, 10, 49, 41))

    def testISOFormatStrip3(self):
        self.assertEqual(parse("2003-09-25T10:49"),
                         datetime(2003, 9, 25, 10, 49))

    def testISOFormatStrip4(self):
        self.assertEqual(parse("2003-09-25T10"),
                         datetime(2003, 9, 25, 10))

    def testISOFormatStrip5(self):
        self.assertEqual(parse("2003-09-25"),
                         datetime(2003, 9, 25))

    def testISOStrippedFormat(self):
        self.assertEqual(parse("20030925T104941.5-0300"),
                         datetime(2003, 9, 25, 10, 49, 41, 500000,
                                  tzinfo=self.brsttz))

    def testISOStrippedFormatStrip1(self):
        self.assertEqual(parse("20030925T104941-0300"),
                         datetime(2003, 9, 25, 10, 49, 41,
                                  tzinfo=self.brsttz))

    def testISOStrippedFormatStrip2(self):
        self.assertEqual(parse("20030925T104941"),
                         datetime(2003, 9, 25, 10, 49, 41))

    def testISOStrippedFormatStrip3(self):
        self.assertEqual(parse("20030925T1049"),
                         datetime(2003, 9, 25, 10, 49, 0))

    def testISOStrippedFormatStrip4(self):
        self.assertEqual(parse("20030925T10"),
                         datetime(2003, 9, 25, 10))

    def testISOStrippedFormatStrip5(self):
        self.assertEqual(parse("20030925"),
                         datetime(2003, 9, 25))

    def testDateWithDash1(self):
        self.assertEqual(parse("2003-09-25"),
                         datetime(2003, 9, 25))

    def testDateWithDash2(self):
        self.assertEqual(parse("2003-Sep-25"),
                         datetime(2003, 9, 25))

    def testDateWithDash3(self):
        self.assertEqual(parse("25-Sep-2003"),
                         datetime(2003, 9, 25))

    def testDateWithDash4(self):
        self.assertEqual(parse("25-Sep-2003"),
                         datetime(2003, 9, 25))

    def testDateWithDash5(self):
        self.assertEqual(parse("Sep-25-2003"),
                         datetime(2003, 9, 25))

    def testDateWithDash6(self):
        self.assertEqual(parse("09-25-2003"),
                         datetime(2003, 9, 25))

    def testDateWithDash7(self):
        self.assertEqual(parse("25-09-2003"),
                         datetime(2003, 9, 25))

    def testDateWithDash8(self):
        self.assertEqual(parse("10-09-2003", dayfirst=True),
                         datetime(2003, 9, 10))

    def testDateWithDash9(self):
        self.assertEqual(parse("10-09-2003"),
                         datetime(2003, 10, 9))

    def testDateWithDash10(self):
        self.assertEqual(parse("10-09-03"),
                         datetime(2003, 10, 9))

    def testDateWithDash11(self):
        self.assertEqual(parse("10-09-03", yearfirst=True),
                         datetime(2010, 9, 3))

    def testDateWithDot1(self):
        self.assertEqual(parse("2003.09.25"),
                         datetime(2003, 9, 25))

    def testDateWithDot2(self):
        self.assertEqual(parse("2003.Sep.25"),
                         datetime(2003, 9, 25))

    def testDateWithDot3(self):
        self.assertEqual(parse("25.Sep.2003"),
                         datetime(2003, 9, 25))

    def testDateWithDot4(self):
        self.assertEqual(parse("25.Sep.2003"),
                         datetime(2003, 9, 25))

    def testDateWithDot5(self):
        self.assertEqual(parse("Sep.25.2003"),
                         datetime(2003, 9, 25))

    def testDateWithDot6(self):
        self.assertEqual(parse("09.25.2003"),
                         datetime(2003, 9, 25))

    def testDateWithDot7(self):
        self.assertEqual(parse("25.09.2003"),
                         datetime(2003, 9, 25))

    def testDateWithDot8(self):
        self.assertEqual(parse("10.09.2003", dayfirst=True),
                         datetime(2003, 9, 10))

    def testDateWithDot9(self):
        self.assertEqual(parse("10.09.2003"),
                         datetime(2003, 10, 9))

    def testDateWithDot10(self):
        self.assertEqual(parse("10.09.03"),
                         datetime(2003, 10, 9))

    def testDateWithDot11(self):
        self.assertEqual(parse("10.09.03", yearfirst=True),
                         datetime(2010, 9, 3))

    def testDateWithSlash1(self):
        self.assertEqual(parse("2003/09/25"),
                         datetime(2003, 9, 25))

    def testDateWithSlash2(self):
        self.assertEqual(parse("2003/Sep/25"),
                         datetime(2003, 9, 25))

    def testDateWithSlash3(self):
        self.assertEqual(parse("25/Sep/2003"),
                         datetime(2003, 9, 25))

    def testDateWithSlash4(self):
        self.assertEqual(parse("25/Sep/2003"),
                         datetime(2003, 9, 25))

    def testDateWithSlash5(self):
        self.assertEqual(parse("Sep/25/2003"),
                         datetime(2003, 9, 25))

    def testDateWithSlash6(self):
        self.assertEqual(parse("09/25/2003"),
                         datetime(2003, 9, 25))

    def testDateWithSlash7(self):
        self.assertEqual(parse("25/09/2003"),
                         datetime(2003, 9, 25))

    def testDateWithSlash8(self):
        self.assertEqual(parse("10/09/2003", dayfirst=True),
                         datetime(2003, 9, 10))

    def testDateWithSlash9(self):
        self.assertEqual(parse("10/09/2003"),
                         datetime(2003, 10, 9))

    def testDateWithSlash10(self):
        self.assertEqual(parse("10/09/03"),
                         datetime(2003, 10, 9))

    def testDateWithSlash11(self):
        self.assertEqual(parse("10/09/03", yearfirst=True),
                         datetime(2010, 9, 3))

    def testDateWithSpace12(self):
        self.assertEqual(parse("25 09 03"),
                         datetime(2003, 9, 25))

    def testDateWithSpace13(self):
        self.assertEqual(parse("25 09 03"),
                         datetime(2003, 9, 25))

    def testDateWithSpace1(self):
        self.assertEqual(parse("2003 09 25"),
                         datetime(2003, 9, 25))

    def testDateWithSpace2(self):
        self.assertEqual(parse("2003 Sep 25"),
                         datetime(2003, 9, 25))

    def testDateWithSpace3(self):
        self.assertEqual(parse("25 Sep 2003"),
                         datetime(2003, 9, 25))

    def testDateWithSpace4(self):
        self.assertEqual(parse("25 Sep 2003"),
                         datetime(2003, 9, 25))

    def testDateWithSpace5(self):
        self.assertEqual(parse("Sep 25 2003"),
                         datetime(2003, 9, 25))

    def testDateWithSpace6(self):
        self.assertEqual(parse("09 25 2003"),
                         datetime(2003, 9, 25))

    def testDateWithSpace7(self):
        self.assertEqual(parse("25 09 2003"),
                         datetime(2003, 9, 25))

    def testDateWithSpace8(self):
        self.assertEqual(parse("10 09 2003", dayfirst=True),
                         datetime(2003, 9, 10))

    def testDateWithSpace9(self):
        self.assertEqual(parse("10 09 2003"),
                         datetime(2003, 10, 9))

    def testDateWithSpace10(self):
        self.assertEqual(parse("10 09 03"),
                         datetime(2003, 10, 9))

    def testDateWithSpace11(self):
        self.assertEqual(parse("10 09 03", yearfirst=True),
                         datetime(2010, 9, 3))

    def testDateWithSpace12(self):
        self.assertEqual(parse("25 09 03"),
                         datetime(2003, 9, 25))

    def testDateWithSpace13(self):
        self.assertEqual(parse("25 09 03"),
                         datetime(2003, 9, 25))

    def testStrangelyOrderedDate1(self):
        self.assertEqual(parse("03 25 Sep"),
                         datetime(2003, 9, 25))

    def testStrangelyOrderedDate2(self):
        self.assertEqual(parse("2003 25 Sep"),
                         datetime(2003, 9, 25))

    def testStrangelyOrderedDate3(self):
        self.assertEqual(parse("25 03 Sep"),
                         datetime(2025, 9, 3))

    def testHourWithLetters(self):
        self.assertEqual(parse("10h36m28.5s", default=self.default),
                         datetime(2003, 9, 25, 10, 36, 28, 500000))

    def testHourWithLettersStrip1(self):
        self.assertEqual(parse("10h36m28s", default=self.default),
                         datetime(2003, 9, 25, 10, 36, 28))

    def testHourWithLettersStrip1(self):
        self.assertEqual(parse("10h36m", default=self.default),
                         datetime(2003, 9, 25, 10, 36))

    def testHourWithLettersStrip2(self):
        self.assertEqual(parse("10h", default=self.default),
                         datetime(2003, 9, 25, 10))

    def testHourAmPm1(self):
        self.assertEqual(parse("10h am", default=self.default),
                         datetime(2003, 9, 25, 10))

    def testHourAmPm2(self):
        self.assertEqual(parse("10h pm", default=self.default),
                         datetime(2003, 9, 25, 22))

    def testHourAmPm3(self):
        self.assertEqual(parse("10am", default=self.default),
                         datetime(2003, 9, 25, 10))

    def testHourAmPm4(self):
        self.assertEqual(parse("10pm", default=self.default),
                         datetime(2003, 9, 25, 22))

    def testHourAmPm5(self):
        self.assertEqual(parse("10:00 am", default=self.default),
                         datetime(2003, 9, 25, 10))

    def testHourAmPm6(self):
        self.assertEqual(parse("10:00 pm", default=self.default),
                         datetime(2003, 9, 25, 22))

    def testHourAmPm7(self):
        self.assertEqual(parse("10:00am", default=self.default),
                         datetime(2003, 9, 25, 10))

    def testHourAmPm8(self):
        self.assertEqual(parse("10:00pm", default=self.default),
                         datetime(2003, 9, 25, 22))

    def testHourAmPm9(self):
        self.assertEqual(parse("10:00a.m", default=self.default),
                         datetime(2003, 9, 25, 10))

    def testHourAmPm10(self):
        self.assertEqual(parse("10:00p.m", default=self.default),
                         datetime(2003, 9, 25, 22))

    def testHourAmPm11(self):
        self.assertEqual(parse("10:00a.m.", default=self.default),
                         datetime(2003, 9, 25, 10))

    def testHourAmPm12(self):
        self.assertEqual(parse("10:00p.m.", default=self.default),
                         datetime(2003, 9, 25, 22))

    def testPertain(self):
        self.assertEqual(parse("Sep 03", default=self.default),
                         datetime(2003, 9, 3))
        self.assertEqual(parse("Sep of 03", default=self.default),
                         datetime(2003, 9, 25))

    def testWeekdayAlone(self):
        self.assertEqual(parse("Wed", default=self.default),
                         datetime(2003, 10, 1))

    def testLongWeekday(self):
        self.assertEqual(parse("Wednesday", default=self.default),
                         datetime(2003, 10, 1))

    def testLongMonth(self):
        self.assertEqual(parse("October", default=self.default),
                         datetime(2003, 10, 25))

    def testFuzzy(self):
        s = "Today is 25 of September of 2003, exactly " \
            "at 10:49:41 with timezone -03:00."
        self.assertEqual(parse(s, fuzzy=True),
                         datetime(2003, 9, 25, 10, 49, 41,
                                  tzinfo=self.brsttz))

    def testExtraSpace(self):
        self.assertEqual(parse("  July   4 ,  1976   12:01:02   am  "),
                         datetime(1976, 7, 4, 0, 1, 2))

    def testRandomFormat1(self):
        self.assertEqual(parse("Wed, July 10, '96"),
                         datetime(1996, 7, 10, 0, 0))

    def testRandomFormat2(self):
        self.assertEqual(parse("1996.07.10 AD at 15:08:56 PDT",
                               ignoretz=True),
                         datetime(1996, 7, 10, 15, 8, 56))

    def testRandomFormat3(self):
        self.assertEqual(parse("1996.July.10 AD 12:08 PM"),
                         datetime(1996, 7, 10, 12, 8))

    def testRandomFormat4(self):
        self.assertEqual(parse("Tuesday, April 12, 1952 AD 3:30:42pm PST",
                               ignoretz=True),
                         datetime(1952, 4, 12, 15, 30, 42))

    def testRandomFormat5(self):
        self.assertEqual(parse("November 5, 1994, 8:15:30 am EST",
                               ignoretz=True),
                         datetime(1994, 11, 5, 8, 15, 30))

    def testRandomFormat6(self):
        self.assertEqual(parse("1994-11-05T08:15:30-05:00",
                               ignoretz=True),
                         datetime(1994, 11, 5, 8, 15, 30))

    def testRandomFormat7(self):
        self.assertEqual(parse("1994-11-05T08:15:30Z",
                               ignoretz=True),
                         datetime(1994, 11, 5, 8, 15, 30))

    def testRandomFormat8(self):
        self.assertEqual(parse("July 4, 1976"), datetime(1976, 7, 4))

    def testRandomFormat9(self):
        self.assertEqual(parse("7 4 1976"), datetime(1976, 7, 4))

    def testRandomFormat10(self):
        self.assertEqual(parse("4 jul 1976"), datetime(1976, 7, 4))

    def testRandomFormat11(self):
        self.assertEqual(parse("7-4-76"), datetime(1976, 7, 4))

    def testRandomFormat12(self):
        self.assertEqual(parse("19760704"), datetime(1976, 7, 4))

    def testRandomFormat13(self):
        self.assertEqual(parse("0:01:02", default=self.default),
                         datetime(2003, 9, 25, 0, 1, 2))

    def testRandomFormat14(self):
        self.assertEqual(parse("12h 01m02s am", default=self.default),
                         datetime(2003, 9, 25, 0, 1, 2))

    def testRandomFormat15(self):
        self.assertEqual(parse("0:01:02 on July 4, 1976"),
                         datetime(1976, 7, 4, 0, 1, 2))

    def testRandomFormat16(self):
        self.assertEqual(parse("0:01:02 on July 4, 1976"),
                         datetime(1976, 7, 4, 0, 1, 2))

    def testRandomFormat17(self):
        self.assertEqual(parse("1976-07-04T00:01:02Z", ignoretz=True),
                         datetime(1976, 7, 4, 0, 1, 2))

    def testRandomFormat18(self):
        self.assertEqual(parse("July 4, 1976 12:01:02 am"),
                         datetime(1976, 7, 4, 0, 1, 2))

    def testRandomFormat19(self):
        self.assertEqual(parse("Mon Jan  2 04:24:27 1995"),
                         datetime(1995, 1, 2, 4, 24, 27))

    def testRandomFormat20(self):
        self.assertEqual(parse("Tue Apr 4 00:22:12 PDT 1995", ignoretz=True),
                         datetime(1995, 4, 4, 0, 22, 12))

    def testRandomFormat21(self):
        self.assertEqual(parse("04.04.95 00:22"),
                         datetime(1995, 4, 4, 0, 22))

    def testRandomFormat22(self):
        self.assertEqual(parse("Jan 1 1999 11:23:34.578"),
                         datetime(1999, 1, 1, 11, 23, 34, 578000))

    def testRandomFormat23(self):
        self.assertEqual(parse("950404 122212"),
                         datetime(1995, 4, 4, 12, 22, 12))

    def testRandomFormat24(self):
        self.assertEqual(parse("0:00 PM, PST", default=self.default,
                               ignoretz=True),
                         datetime(2003, 9, 25, 12, 0))

    def testRandomFormat25(self):
        self.assertEqual(parse("12:08 PM", default=self.default),
                         datetime(2003, 9, 25, 12, 8))

    def testRandomFormat26(self):
        self.assertEqual(parse("5:50 A.M. on June 13, 1990"),
                         datetime(1990, 6, 13, 5, 50))

    def testRandomFormat27(self):
        self.assertEqual(parse("3rd of May 2001"), datetime(2001, 5, 3))

    def testRandomFormat28(self):
        self.assertEqual(parse("5th of March 2001"), datetime(2001, 3, 5))

    def testRandomFormat29(self):
        self.assertEqual(parse("1st of May 2003"), datetime(2003, 5, 1))

    def testRandomFormat30(self):
        self.assertEqual(parse("01h02m03", default=self.default),
                         datetime(2003, 9, 25, 1, 2, 3))

    def testRandomFormat31(self):
        self.assertEqual(parse("01h02", default=self.default),
                         datetime(2003, 9, 25, 1, 2))

    def testRandomFormat32(self):
        self.assertEqual(parse("01h02s", default=self.default),
                         datetime(2003, 9, 25, 1, 0, 2))

    def testRandomFormat33(self):
        self.assertEqual(parse("01m02", default=self.default),
                         datetime(2003, 9, 25, 0, 1, 2))

    def testRandomFormat34(self):
        self.assertEqual(parse("01m02h", default=self.default),
                         datetime(2003, 9, 25, 2, 1))

class EasterTest(unittest.TestCase):
    easterlist = [
                 # WESTERN            ORTHODOX
                  (date(1990, 4, 15), date(1990, 4, 15)),
                  (date(1991, 3, 31), date(1991, 4,  7)),
                  (date(1992, 4, 19), date(1992, 4, 26)),
                  (date(1993, 4, 11), date(1993, 4, 18)),
                  (date(1994, 4,  3), date(1994, 5,  1)),
                  (date(1995, 4, 16), date(1995, 4, 23)),
                  (date(1996, 4,  7), date(1996, 4, 14)),
                  (date(1997, 3, 30), date(1997, 4, 27)),
                  (date(1998, 4, 12), date(1998, 4, 19)),
                  (date(1999, 4,  4), date(1999, 4, 11)),

                  (date(2000, 4, 23), date(2000, 4, 30)),
                  (date(2001, 4, 15), date(2001, 4, 15)),
                  (date(2002, 3, 31), date(2002, 5,  5)),
                  (date(2003, 4, 20), date(2003, 4, 27)),
                  (date(2004, 4, 11), date(2004, 4, 11)),
                  (date(2005, 3, 27), date(2005, 5,  1)),
                  (date(2006, 4, 16), date(2006, 4, 23)),
                  (date(2007, 4,  8), date(2007, 4,  8)),
                  (date(2008, 3, 23), date(2008, 4, 27)),
                  (date(2009, 4, 12), date(2009, 4, 19)),

                  (date(2010, 4,  4), date(2010, 4,  4)),
                  (date(2011, 4, 24), date(2011, 4, 24)),
                  (date(2012, 4,  8), date(2012, 4, 15)),
                  (date(2013, 3, 31), date(2013, 5,  5)),
                  (date(2014, 4, 20), date(2014, 4, 20)),
                  (date(2015, 4,  5), date(2015, 4, 12)),
                  (date(2016, 3, 27), date(2016, 5,  1)),
                  (date(2017, 4, 16), date(2017, 4, 16)),
                  (date(2018, 4,  1), date(2018, 4,  8)),
                  (date(2019, 4, 21), date(2019, 4, 28)),

                  (date(2020, 4, 12), date(2020, 4, 19)),
                  (date(2021, 4,  4), date(2021, 5,  2)),
                  (date(2022, 4, 17), date(2022, 4, 24)),
                  (date(2023, 4,  9), date(2023, 4, 16)),
                  (date(2024, 3, 31), date(2024, 5,  5)),
                  (date(2025, 4, 20), date(2025, 4, 20)),
                  (date(2026, 4,  5), date(2026, 4, 12)),
                  (date(2027, 3, 28), date(2027, 5,  2)),
                  (date(2028, 4, 16), date(2028, 4, 16)),
                  (date(2029, 4,  1), date(2029, 4,  8)),

                  (date(2030, 4, 21), date(2030, 4, 28)),
                  (date(2031, 4, 13), date(2031, 4, 13)),
                  (date(2032, 3, 28), date(2032, 5,  2)),
                  (date(2033, 4, 17), date(2033, 4, 24)),
                  (date(2034, 4,  9), date(2034, 4,  9)),
                  (date(2035, 3, 25), date(2035, 4, 29)),
                  (date(2036, 4, 13), date(2036, 4, 20)),
                  (date(2037, 4,  5), date(2037, 4,  5)),
                  (date(2038, 4, 25), date(2038, 4, 25)),
                  (date(2039, 4, 10), date(2039, 4, 17)),

                  (date(2040, 4,  1), date(2040, 5,  6)),
                  (date(2041, 4, 21), date(2041, 4, 21)),
                  (date(2042, 4,  6), date(2042, 4, 13)),
                  (date(2043, 3, 29), date(2043, 5,  3)),
                  (date(2044, 4, 17), date(2044, 4, 24)),
                  (date(2045, 4,  9), date(2045, 4,  9)),
                  (date(2046, 3, 25), date(2046, 4, 29)),
                  (date(2047, 4, 14), date(2047, 4, 21)),
                  (date(2048, 4,  5), date(2048, 4,  5)),
                  (date(2049, 4, 18), date(2049, 4, 25)),

                  (date(2050, 4, 10), date(2050, 4, 17)),
                ]

    def testEaster(self):
        for western, orthodox in self.easterlist:
            self.assertEqual(western,  easter(western.year,  EASTER_WESTERN))
            self.assertEqual(orthodox, easter(orthodox.year, EASTER_ORTHODOX))

class TZTest(unittest.TestCase):

    TZFILE_EST5EDT = """
VFppZgAAAAAAAAAAAAAAAAAAAAAAAAAEAAAABAAAAAAAAADrAAAABAAAABCeph5wn7rrYKCGAHCh
ms1gomXicKOD6eCkaq5wpTWnYKZTyvCnFYlgqDOs8Kj+peCqE47wqt6H4KvzcPCsvmngrdNS8K6e
S+CvszTwsH4t4LGcUXCyZ0pgs3wzcLRHLGC1XBVwticOYLc793C4BvBguRvZcLnm0mC7BPXwu8a0
YLzk1/C9r9DgvsS58L+PsuDApJvwwW+U4MKEffDDT3bgxGRf8MUvWODGTXxwxw864MgtXnDI+Fdg
yg1AcMrYOWDLiPBw0iP0cNJg++DTdeTw1EDd4NVVxvDWIL/g1zWo8NgAoeDZFYrw2eCD4Nr+p3Db
wGXg3N6JcN2pgmDevmtw34lkYOCeTXDhaUZg4n4vcONJKGDkXhFw5Vcu4OZHLfDnNxDg6CcP8OkW
8uDqBvHw6vbU4Ovm0/Ds1rbg7ca18O6/02Dvr9Jw8J+1YPGPtHDyf5dg82+WcPRfeWD1T3hw9j9b
YPcvWnD4KHfg+Q88cPoIWeD6+Fjw++g74PzYOvD9yB3g/rgc8P+n/+AAl/7wAYfh4AJ34PADcP5g
BGD9cAVQ4GAGQN9wBzDCYAeNGXAJEKRgCa2U8ArwhmAL4IVwDNmi4A3AZ3AOuYTgD6mD8BCZZuAR
iWXwEnlI4BNpR/AUWSrgFUkp8BY5DOAXKQvwGCIpYBkI7fAaAgtgGvIKcBvh7WAc0exwHcHPYB6x
znAfobFgIHYA8CGBk2AiVeLwI2qv4CQ1xPAlSpHgJhWm8Ccqc+An/sNwKQpV4CnepXAq6jfgK76H
cCzTVGAtnmlwLrM2YC9+S3AwkxhgMWdn8DJy+mAzR0nwNFLcYDUnK/A2Mr5gNwcN8Dgb2uA45u/w
Ofu84DrG0fA7257gPK/ucD27gOA+j9BwP5ti4EBvsnBBhH9gQk+UcENkYWBEL3ZwRURDYEYPWHBH
JCVgR/h08EkEB2BJ2FbwSuPpYEu4OPBMzQXgTZga8E6s5+BPd/zwUIzJ4FFhGXBSbKvgU0D7cFRM
jeBVIN1wVixv4FcAv3BYFYxgWOChcFn1bmBawINwW9VQYFypn/BdtTJgXomB8F+VFGBgaWPwYX4w
4GJJRfBjXhLgZCkn8GU99OBmEkRwZx3W4GfyJnBo/bjgadIIcGrdmuBrsepwbMa3YG2RzHBupplg
b3GucHCGe2BxWsrwcmZdYHM6rPB0Rj9gdRqO8HYvW+B2+nDweA894HjaUvB57x/gero08HvPAeB8
o1Fwfa7j4H6DM3B/jsXgAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAgMBAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEA
AQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAf//x8ABAP//ubAABP//x8ABCP//x8ABDEVEVABFU1QARVdU
AEVQVAAAAAABAAAAAQ==
    """

    TZICAL_EST5EDT = """
BEGIN:VTIMEZONE
TZID:US-Eastern
LAST-MODIFIED:19870101T000000Z
TZURL:http://zones.stds_r_us.net/tz/US-Eastern
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
END:DAYLIGHT
END:VTIMEZONE
    """

    def testStrStart1(self):
        self.assertEqual(datetime(2003,4,6,1,59,
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EDT")

    def testStrEnd1(self):
        self.assertEqual(datetime(2003,10,26,0,59,
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,
                                  tzinfo=tzstr("EST5EDT")).tzname(), "EST")

    def testStrStart2(self):
        s = "EST5EDT,4,0,6,7200,10,0,26,7200,3600"
        self.assertEqual(datetime(2003,4,6,1,59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd2(self):
        s = "EST5EDT,4,0,6,7200,10,0,26,7200,3600"
        self.assertEqual(datetime(2003,10,26,0,59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart3(self):
        s = "EST5EDT,4,1,0,7200,10,-1,0,7200,3600"
        self.assertEqual(datetime(2003,4,6,1,59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd3(self):
        s = "EST5EDT,4,1,0,7200,10,-1,0,7200,3600"
        self.assertEqual(datetime(2003,10,26,0,59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart4(self):
        s = "EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"
        self.assertEqual(datetime(2003,4,6,1,59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd4(self):
        s = "EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"
        self.assertEqual(datetime(2003,10,26,0,59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart5(self):
        s = "EST5EDT4,95/02:00:00,298/02:00"
        self.assertEqual(datetime(2003,4,6,1,59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd5(self):
        s = "EST5EDT4,95/02:00:00,298/02"
        self.assertEqual(datetime(2003,10,26,0,59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrStart6(self):
        s = "EST5EDT4,J96/02:00:00,J299/02:00"
        self.assertEqual(datetime(2003,4,6,1,59,
                                  tzinfo=tzstr(s)).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,
                                  tzinfo=tzstr(s)).tzname(), "EDT")

    def testStrEnd6(self):
        s = "EST5EDT4,J96/02:00:00,J299/02"
        self.assertEqual(datetime(2003,10,26,0,59,
                                  tzinfo=tzstr(s)).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,
                                  tzinfo=tzstr(s)).tzname(), "EST")

    def testStrCmp1(self):
        self.assertEqual(tzstr("EST5EDT"),
                         tzstr("EST5EDT4,M4.1.0/02:00:00,M10-5-0/02:00"))
        
    def testStrCmp2(self):
        self.assertEqual(tzstr("EST5EDT"),
                         tzstr("EST5EDT,4,1,0,7200,10,-1,0,7200,3600"))

    def testRangeCmp1(self):
        self.assertEqual(tzstr("EST5EDT"),
                         tzrange("EST", -18000, "EDT", -14400,
                                 relativedelta(hours=+2,
                                               month=4, day=1,
                                               weekday=SU(+1)),
                                 relativedelta(hours=+1,
                                               month=10, day=31,
                                               weekday=SU(-1))))

    def testRangeCmp2(self):
        self.assertEqual(tzstr("EST5EDT"),
                         tzrange("EST", -18000, "EDT"))

    def testFileStart1(self):
        tz = tzfile(StringIO(base64.decodestring(self.TZFILE_EST5EDT)))
        self.assertEqual(datetime(2003,4,6,1,59,tzinfo=tz).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,tzinfo=tz).tzname(), "EDT")
        
    def testFileEnd1(self):
        tz = tzfile(StringIO(base64.decodestring(self.TZFILE_EST5EDT)))
        self.assertEqual(datetime(2003,10,26,0,59,tzinfo=tz).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,tzinfo=tz).tzname(), "EST")

    def testICalStart1(self):
        tz = tzical(StringIO(self.TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003,4,6,1,59,tzinfo=tz).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,tzinfo=tz).tzname(), "EDT")

    def testICalEnd1(self):
        tz = tzical(StringIO(self.TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003,10,26,0,59,tzinfo=tz).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,tzinfo=tz).tzname(), "EST")

if __name__ == "__main__":
	unittest.main()

# vim:ts=4:sw=4
