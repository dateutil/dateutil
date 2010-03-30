#!/usr/bin/python
# -*- encoding: utf-8 -*-
from cStringIO import StringIO
import unittest
import calendar
import time
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
from dateutil import zoneinfo

from datetime import *


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

    def testYearDayBug(self):
        # Tests a problem reported by Adam Ryan.
        self.assertEqual(date(2010, 1, 1)+relativedelta(yearday=15),
                         date(2010, 1, 15))

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
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testYearlyInterval(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0),
                          datetime(2001, 9, 2, 9, 0)])

    def testYearlyIntervalLarge(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              interval=100,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(2097, 9, 2, 9, 0),
                          datetime(2197, 9, 2, 9, 0)])

    def testYearlyByMonth(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 2, 9, 0),
                          datetime(1998, 3, 2, 9, 0),
                          datetime(1999, 1, 2, 9, 0)])

    def testYearlyByMonthDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testYearlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testYearlyByWeekDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testYearlyByNWeekDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 25, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 12, 31, 9, 0)])

    def testYearlyByNWeekDayLarge(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekday=(TU(3),TH(-3)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 11, 9, 0),
                          datetime(1998, 1, 20, 9, 0),
                          datetime(1998, 12, 17, 9, 0)])

    def testYearlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testYearlyByMonthAndNWeekDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 29, 9, 0),
                          datetime(1998, 3, 3, 9, 0)])

    def testYearlyByMonthAndNWeekDayLarge(self):
        # This is interesting because the TH(-3) ends up before
        # the TU(3).
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(3),TH(-3)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 15, 9, 0),
                          datetime(1998, 1, 20, 9, 0),
                          datetime(1998, 3, 12, 9, 0)])

    def testYearlyByMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 2, 3, 9, 0),
                          datetime(1998, 3, 3, 9, 0)])

    def testYearlyByMonthAndMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 3, 3, 9, 0),
                          datetime(2001, 3, 1, 9, 0)])

    def testYearlyByYearDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=4,
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testYearlyByYearDayNeg(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=4,
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testYearlyByMonthAndYearDay(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 4, 10, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])

    def testYearlyByMonthAndYearDayNeg(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 4, 10, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])

    def testYearlyByWeekNo(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekno=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 5, 11, 9, 0),
                          datetime(1998, 5, 12, 9, 0),
                          datetime(1998, 5, 13, 9, 0)])

    def testYearlyByWeekNoAndWeekDay(self):
        # That's a nice one. The first days of week number one
        # may be in the last year.
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekno=1,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 29, 9, 0),
                          datetime(1999, 1, 4, 9, 0),
                          datetime(2000, 1, 3, 9, 0)])

    def testYearlyByWeekNoAndWeekDayLarge(self):
        # Another nice test. The last days of week number 52/53
        # may be in the next year.
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekno=52,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1998, 12, 27, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testYearlyByWeekNoAndWeekDayLast(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekno=-1,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1999, 1, 3, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testYearlyByEaster(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byeaster=0,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 12, 9, 0),
                          datetime(1999, 4, 4, 9, 0),
                          datetime(2000, 4, 23, 9, 0)])

    def testYearlyByEasterPos(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byeaster=1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 13, 9, 0),
                          datetime(1999, 4, 5, 9, 0),
                          datetime(2000, 4, 24, 9, 0)])

    def testYearlyByEasterNeg(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byeaster=-1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 11, 9, 0),
                          datetime(1999, 4, 3, 9, 0),
                          datetime(2000, 4, 22, 9, 0)])

    def testYearlyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 9, 0),
                          datetime(2004, 12, 27, 9, 0),
                          datetime(2009, 12, 28, 9, 0)])

    def testYearlyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 9, 0),
                          datetime(2004, 12, 27, 9, 0),
                          datetime(2009, 12, 28, 9, 0)])

    def testYearlyByHour(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byhour=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0),
                          datetime(1998, 9, 2, 6, 0),
                          datetime(1998, 9, 2, 18, 0)])

    def testYearlyByMinute(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6),
                          datetime(1997, 9, 2, 9, 18),
                          datetime(1998, 9, 2, 9, 6)])

    def testYearlyBySecond(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 6),
                          datetime(1997, 9, 2, 9, 0, 18),
                          datetime(1998, 9, 2, 9, 0, 6)])

    def testYearlyByHourAndMinute(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6),
                          datetime(1997, 9, 2, 18, 18),
                          datetime(1998, 9, 2, 6, 6)])

    def testYearlyByHourAndSecond(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byhour=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 6),
                          datetime(1997, 9, 2, 18, 0, 18),
                          datetime(1998, 9, 2, 6, 0, 6)])

    def testYearlyByMinuteAndSecond(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 6),
                          datetime(1997, 9, 2, 9, 6, 18),
                          datetime(1997, 9, 2, 9, 18, 6)])

    def testYearlyByHourAndMinuteAndSecond(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 6),
                          datetime(1997, 9, 2, 18, 6, 18),
                          datetime(1997, 9, 2, 18, 18, 6)])

    def testYearlyBySetPos(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonthday=15,
                              byhour=(6,18),
                              bysetpos=(3,-3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 11, 15, 18, 0),
                          datetime(1998, 2, 15, 6, 0),
                          datetime(1998, 11, 15, 18, 0)])

    def testMonthly(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 10, 2, 9, 0),
                          datetime(1997, 11, 2, 9, 0)])

    def testMonthlyInterval(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 11, 2, 9, 0),
                          datetime(1998, 1, 2, 9, 0)])

    def testMonthlyIntervalLarge(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              interval=18,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1999, 3, 2, 9, 0),
                          datetime(2000, 9, 2, 9, 0)])

    def testMonthlyByMonth(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 2, 9, 0),
                          datetime(1998, 3, 2, 9, 0),
                          datetime(1999, 1, 2, 9, 0)])


    def testMonthlyByMonthDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testMonthlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testMonthlyByWeekDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testMonthlyByNWeekDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 25, 9, 0),
                          datetime(1997, 10, 7, 9, 0)])

    def testMonthlyByNWeekDayLarge(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekday=(TU(3),TH(-3)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 11, 9, 0),
                          datetime(1997, 9, 16, 9, 0),
                          datetime(1997, 10, 16, 9, 0)])

    def testMonthlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testMonthlyByMonthAndNWeekDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 29, 9, 0),
                          datetime(1998, 3, 3, 9, 0)])

    def testMonthlyByMonthAndNWeekDayLarge(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(3),TH(-3)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 15, 9, 0),
                          datetime(1998, 1, 20, 9, 0),
                          datetime(1998, 3, 12, 9, 0)])

    def testMonthlyByMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 2, 3, 9, 0),
                          datetime(1998, 3, 3, 9, 0)])

    def testMonthlyByMonthAndMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 3, 3, 9, 0),
                          datetime(2001, 3, 1, 9, 0)])

    def testMonthlyByYearDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=4,
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testMonthlyByYearDayNeg(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=4,
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testMonthlyByMonthAndYearDay(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 4, 10, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])

    def testMonthlyByMonthAndYearDayNeg(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 4, 10, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])


    def testMonthlyByWeekNo(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekno=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 5, 11, 9, 0),
                          datetime(1998, 5, 12, 9, 0),
                          datetime(1998, 5, 13, 9, 0)])

    def testMonthlyByWeekNoAndWeekDay(self):
        # That's a nice one. The first days of week number one
        # may be in the last year.
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekno=1,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 29, 9, 0),
                          datetime(1999, 1, 4, 9, 0),
                          datetime(2000, 1, 3, 9, 0)])

    def testMonthlyByWeekNoAndWeekDayLarge(self):
        # Another nice test. The last days of week number 52/53
        # may be in the next year.
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekno=52,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1998, 12, 27, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testMonthlyByWeekNoAndWeekDayLast(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekno=-1,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1999, 1, 3, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testMonthlyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 9, 0),
                          datetime(2004, 12, 27, 9, 0),
                          datetime(2009, 12, 28, 9, 0)])

    def testMonthlyByEaster(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byeaster=0,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 12, 9, 0),
                          datetime(1999, 4, 4, 9, 0),
                          datetime(2000, 4, 23, 9, 0)])

    def testMonthlyByEasterPos(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byeaster=1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 13, 9, 0),
                          datetime(1999, 4, 5, 9, 0),
                          datetime(2000, 4, 24, 9, 0)])

    def testMonthlyByEasterNeg(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byeaster=-1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 11, 9, 0),
                          datetime(1999, 4, 3, 9, 0),
                          datetime(2000, 4, 22, 9, 0)])

    def testMonthlyByHour(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byhour=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0),
                          datetime(1997, 10, 2, 6, 0),
                          datetime(1997, 10, 2, 18, 0)])

    def testMonthlyByMinute(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6),
                          datetime(1997, 9, 2, 9, 18),
                          datetime(1997, 10, 2, 9, 6)])

    def testMonthlyBySecond(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 6),
                          datetime(1997, 9, 2, 9, 0, 18),
                          datetime(1997, 10, 2, 9, 0, 6)])

    def testMonthlyByHourAndMinute(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6),
                          datetime(1997, 9, 2, 18, 18),
                          datetime(1997, 10, 2, 6, 6)])

    def testMonthlyByHourAndSecond(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byhour=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 6),
                          datetime(1997, 9, 2, 18, 0, 18),
                          datetime(1997, 10, 2, 6, 0, 6)])

    def testMonthlyByMinuteAndSecond(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 6),
                          datetime(1997, 9, 2, 9, 6, 18),
                          datetime(1997, 9, 2, 9, 18, 6)])

    def testMonthlyByHourAndMinuteAndSecond(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 6),
                          datetime(1997, 9, 2, 18, 6, 18),
                          datetime(1997, 9, 2, 18, 18, 6)])

    def testMonthlyBySetPos(self):
        self.assertEqual(list(rrule(MONTHLY,
                              count=3,
                              bymonthday=(13,17),
                              byhour=(6,18),
                              bysetpos=(3,-3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 13, 18, 0),
                          datetime(1997, 9, 17, 6, 0),
                          datetime(1997, 10, 13, 18, 0)])

    def testWeekly(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testWeeklyInterval(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 16, 9, 0),
                          datetime(1997, 9, 30, 9, 0)])

    def testWeeklyIntervalLarge(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              interval=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 1, 20, 9, 0),
                          datetime(1998, 6, 9, 9, 0)])

    def testWeeklyByMonth(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 13, 9, 0),
                          datetime(1998, 1, 20, 9, 0)])

    def testWeeklyByMonthDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testWeeklyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testWeeklyByWeekDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testWeeklyByNWeekDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testWeeklyByMonthAndWeekDay(self):
        # This test is interesting, because it crosses the year
        # boundary in a weekly period to find day '1' as a
        # valid recurrence.
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testWeeklyByMonthAndNWeekDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testWeeklyByMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 2, 3, 9, 0),
                          datetime(1998, 3, 3, 9, 0)])

    def testWeeklyByMonthAndMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 3, 3, 9, 0),
                          datetime(2001, 3, 1, 9, 0)])

    def testWeeklyByYearDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=4,
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testWeeklyByYearDayNeg(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=4,
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testWeeklyByMonthAndYearDay(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=4,
                              bymonth=(1,7),
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 1, 1, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])

    def testWeeklyByMonthAndYearDayNeg(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=4,
                              bymonth=(1,7),
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 1, 1, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])

    def testWeeklyByWeekNo(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekno=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 5, 11, 9, 0),
                          datetime(1998, 5, 12, 9, 0),
                          datetime(1998, 5, 13, 9, 0)])

    def testWeeklyByWeekNoAndWeekDay(self):
        # That's a nice one. The first days of week number one
        # may be in the last year.
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekno=1,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 29, 9, 0),
                          datetime(1999, 1, 4, 9, 0),
                          datetime(2000, 1, 3, 9, 0)])

    def testWeeklyByWeekNoAndWeekDayLarge(self):
        # Another nice test. The last days of week number 52/53
        # may be in the next year.
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekno=52,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1998, 12, 27, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testWeeklyByWeekNoAndWeekDayLast(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekno=-1,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1999, 1, 3, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testWeeklyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 9, 0),
                          datetime(2004, 12, 27, 9, 0),
                          datetime(2009, 12, 28, 9, 0)])

    def testWeeklyByEaster(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byeaster=0,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 12, 9, 0),
                          datetime(1999, 4, 4, 9, 0),
                          datetime(2000, 4, 23, 9, 0)])

    def testWeeklyByEasterPos(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byeaster=1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 13, 9, 0),
                          datetime(1999, 4, 5, 9, 0),
                          datetime(2000, 4, 24, 9, 0)])

    def testWeeklyByEasterNeg(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byeaster=-1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 11, 9, 0),
                          datetime(1999, 4, 3, 9, 0),
                          datetime(2000, 4, 22, 9, 0)])

    def testWeeklyByHour(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byhour=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0),
                          datetime(1997, 9, 9, 6, 0),
                          datetime(1997, 9, 9, 18, 0)])

    def testWeeklyByMinute(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6),
                          datetime(1997, 9, 2, 9, 18),
                          datetime(1997, 9, 9, 9, 6)])

    def testWeeklyBySecond(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 6),
                          datetime(1997, 9, 2, 9, 0, 18),
                          datetime(1997, 9, 9, 9, 0, 6)])

    def testWeeklyByHourAndMinute(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6),
                          datetime(1997, 9, 2, 18, 18),
                          datetime(1997, 9, 9, 6, 6)])

    def testWeeklyByHourAndSecond(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byhour=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 6),
                          datetime(1997, 9, 2, 18, 0, 18),
                          datetime(1997, 9, 9, 6, 0, 6)])

    def testWeeklyByMinuteAndSecond(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 6),
                          datetime(1997, 9, 2, 9, 6, 18),
                          datetime(1997, 9, 2, 9, 18, 6)])

    def testWeeklyByHourAndMinuteAndSecond(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 6),
                          datetime(1997, 9, 2, 18, 6, 18),
                          datetime(1997, 9, 2, 18, 18, 6)])

    def testWeeklyBySetPos(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              byweekday=(TU,TH),
                              byhour=(6,18),
                              bysetpos=(3,-3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0),
                          datetime(1997, 9, 4, 6, 0),
                          datetime(1997, 9, 9, 18, 0)])

    def testDaily(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testDailyInterval(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 6, 9, 0)])

    def testDailyIntervalLarge(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              interval=92,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 12, 3, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testDailyByMonth(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 2, 9, 0),
                          datetime(1998, 1, 3, 9, 0)])

    def testDailyByMonthDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 10, 1, 9, 0),
                          datetime(1997, 10, 3, 9, 0)])

    def testDailyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 9, 0),
                          datetime(1998, 1, 7, 9, 0),
                          datetime(1998, 3, 5, 9, 0)])

    def testDailyByWeekDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testDailyByNWeekDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testDailyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testDailyByMonthAndNWeekDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 1, 8, 9, 0)])

    def testDailyByMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 2, 3, 9, 0),
                          datetime(1998, 3, 3, 9, 0)])

    def testDailyByMonthAndMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 3, 3, 9, 0),
                          datetime(2001, 3, 1, 9, 0)])

    def testDailyByYearDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=4,
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testDailyByYearDayNeg(self):
        self.assertEqual(list(rrule(DAILY,
                              count=4,
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 9, 0),
                          datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 4, 10, 9, 0),
                          datetime(1998, 7, 19, 9, 0)])

    def testDailyByMonthAndYearDay(self):
        self.assertEqual(list(rrule(DAILY,
                              count=4,
                              bymonth=(1,7),
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 1, 1, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])

    def testDailyByMonthAndYearDayNeg(self):
        self.assertEqual(list(rrule(DAILY,
                              count=4,
                              bymonth=(1,7),
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 9, 0),
                          datetime(1998, 7, 19, 9, 0),
                          datetime(1999, 1, 1, 9, 0),
                          datetime(1999, 7, 19, 9, 0)])

    def testDailyByWeekNo(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byweekno=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 5, 11, 9, 0),
                          datetime(1998, 5, 12, 9, 0),
                          datetime(1998, 5, 13, 9, 0)])

    def testDailyByWeekNoAndWeekDay(self):
        # That's a nice one. The first days of week number one
        # may be in the last year.
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byweekno=1,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 29, 9, 0),
                          datetime(1999, 1, 4, 9, 0),
                          datetime(2000, 1, 3, 9, 0)])

    def testDailyByWeekNoAndWeekDayLarge(self):
        # Another nice test. The last days of week number 52/53
        # may be in the next year.
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byweekno=52,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1998, 12, 27, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testDailyByWeekNoAndWeekDayLast(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byweekno=-1,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 9, 0),
                          datetime(1999, 1, 3, 9, 0),
                          datetime(2000, 1, 2, 9, 0)])

    def testDailyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 9, 0),
                          datetime(2004, 12, 27, 9, 0),
                          datetime(2009, 12, 28, 9, 0)])

    def testDailyByEaster(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byeaster=0,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 12, 9, 0),
                          datetime(1999, 4, 4, 9, 0),
                          datetime(2000, 4, 23, 9, 0)])

    def testDailyByEasterPos(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byeaster=1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 13, 9, 0),
                          datetime(1999, 4, 5, 9, 0),
                          datetime(2000, 4, 24, 9, 0)])

    def testDailyByEasterNeg(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byeaster=-1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 11, 9, 0),
                          datetime(1999, 4, 3, 9, 0),
                          datetime(2000, 4, 22, 9, 0)])

    def testDailyByHour(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byhour=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0),
                          datetime(1997, 9, 3, 6, 0),
                          datetime(1997, 9, 3, 18, 0)])

    def testDailyByMinute(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6),
                          datetime(1997, 9, 2, 9, 18),
                          datetime(1997, 9, 3, 9, 6)])

    def testDailyBySecond(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 6),
                          datetime(1997, 9, 2, 9, 0, 18),
                          datetime(1997, 9, 3, 9, 0, 6)])

    def testDailyByHourAndMinute(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6),
                          datetime(1997, 9, 2, 18, 18),
                          datetime(1997, 9, 3, 6, 6)])

    def testDailyByHourAndSecond(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byhour=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 6),
                          datetime(1997, 9, 2, 18, 0, 18),
                          datetime(1997, 9, 3, 6, 0, 6)])

    def testDailyByMinuteAndSecond(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 6),
                          datetime(1997, 9, 2, 9, 6, 18),
                          datetime(1997, 9, 2, 9, 18, 6)])

    def testDailyByHourAndMinuteAndSecond(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 6),
                          datetime(1997, 9, 2, 18, 6, 18),
                          datetime(1997, 9, 2, 18, 18, 6)])

    def testDailyBySetPos(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              byhour=(6,18),
                              byminute=(15,45),
                              bysetpos=(3,-3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 15),
                          datetime(1997, 9, 3, 6, 45),
                          datetime(1997, 9, 3, 18, 15)])

    def testHourly(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 10, 0),
                          datetime(1997, 9, 2, 11, 0)])

    def testHourlyInterval(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 11, 0),
                          datetime(1997, 9, 2, 13, 0)])

    def testHourlyIntervalLarge(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              interval=769,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 10, 4, 10, 0),
                          datetime(1997, 11, 5, 11, 0)])

    def testHourlyByMonth(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 1, 0),
                          datetime(1998, 1, 1, 2, 0)])

    def testHourlyByMonthDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 0, 0),
                          datetime(1997, 9, 3, 1, 0),
                          datetime(1997, 9, 3, 2, 0)])

    def testHourlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 0, 0),
                          datetime(1998, 1, 5, 1, 0),
                          datetime(1998, 1, 5, 2, 0)])

    def testHourlyByWeekDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 10, 0),
                          datetime(1997, 9, 2, 11, 0)])

    def testHourlyByNWeekDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 10, 0),
                          datetime(1997, 9, 2, 11, 0)])

    def testHourlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 1, 0),
                          datetime(1998, 1, 1, 2, 0)])

    def testHourlyByMonthAndNWeekDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 1, 0),
                          datetime(1998, 1, 1, 2, 0)])

    def testHourlyByMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 1, 0),
                          datetime(1998, 1, 1, 2, 0)])

    def testHourlyByMonthAndMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 1, 0),
                          datetime(1998, 1, 1, 2, 0)])

    def testHourlyByYearDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=4,
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 0, 0),
                          datetime(1997, 12, 31, 1, 0),
                          datetime(1997, 12, 31, 2, 0),
                          datetime(1997, 12, 31, 3, 0)])

    def testHourlyByYearDayNeg(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=4,
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 0, 0),
                          datetime(1997, 12, 31, 1, 0),
                          datetime(1997, 12, 31, 2, 0),
                          datetime(1997, 12, 31, 3, 0)])

    def testHourlyByMonthAndYearDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 0, 0),
                          datetime(1998, 4, 10, 1, 0),
                          datetime(1998, 4, 10, 2, 0),
                          datetime(1998, 4, 10, 3, 0)])

    def testHourlyByMonthAndYearDayNeg(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 0, 0),
                          datetime(1998, 4, 10, 1, 0),
                          datetime(1998, 4, 10, 2, 0),
                          datetime(1998, 4, 10, 3, 0)])

    def testHourlyByWeekNo(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byweekno=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 5, 11, 0, 0),
                          datetime(1998, 5, 11, 1, 0),
                          datetime(1998, 5, 11, 2, 0)])

    def testHourlyByWeekNoAndWeekDay(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byweekno=1,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 29, 0, 0),
                          datetime(1997, 12, 29, 1, 0),
                          datetime(1997, 12, 29, 2, 0)])

    def testHourlyByWeekNoAndWeekDayLarge(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byweekno=52,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 0, 0),
                          datetime(1997, 12, 28, 1, 0),
                          datetime(1997, 12, 28, 2, 0)])

    def testHourlyByWeekNoAndWeekDayLast(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byweekno=-1,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 0, 0),
                          datetime(1997, 12, 28, 1, 0),
                          datetime(1997, 12, 28, 2, 0)])

    def testHourlyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 0, 0),
                          datetime(1998, 12, 28, 1, 0),
                          datetime(1998, 12, 28, 2, 0)])

    def testHourlyByEaster(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byeaster=0,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 12, 0, 0),
                          datetime(1998, 4, 12, 1, 0),
                          datetime(1998, 4, 12, 2, 0)])

    def testHourlyByEasterPos(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byeaster=1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 13, 0, 0),
                          datetime(1998, 4, 13, 1, 0),
                          datetime(1998, 4, 13, 2, 0)])

    def testHourlyByEasterNeg(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byeaster=-1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 11, 0, 0),
                          datetime(1998, 4, 11, 1, 0),
                          datetime(1998, 4, 11, 2, 0)])

    def testHourlyByHour(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byhour=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0),
                          datetime(1997, 9, 3, 6, 0),
                          datetime(1997, 9, 3, 18, 0)])

    def testHourlyByMinute(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6),
                          datetime(1997, 9, 2, 9, 18),
                          datetime(1997, 9, 2, 10, 6)])

    def testHourlyBySecond(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 6),
                          datetime(1997, 9, 2, 9, 0, 18),
                          datetime(1997, 9, 2, 10, 0, 6)])

    def testHourlyByHourAndMinute(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6),
                          datetime(1997, 9, 2, 18, 18),
                          datetime(1997, 9, 3, 6, 6)])

    def testHourlyByHourAndSecond(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byhour=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 6),
                          datetime(1997, 9, 2, 18, 0, 18),
                          datetime(1997, 9, 3, 6, 0, 6)])

    def testHourlyByMinuteAndSecond(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 6),
                          datetime(1997, 9, 2, 9, 6, 18),
                          datetime(1997, 9, 2, 9, 18, 6)])

    def testHourlyByHourAndMinuteAndSecond(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 6),
                          datetime(1997, 9, 2, 18, 6, 18),
                          datetime(1997, 9, 2, 18, 18, 6)])

    def testHourlyBySetPos(self):
        self.assertEqual(list(rrule(HOURLY,
                              count=3,
                              byminute=(15,45),
                              bysecond=(15,45),
                              bysetpos=(3,-3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 15, 45),
                          datetime(1997, 9, 2, 9, 45, 15),
                          datetime(1997, 9, 2, 10, 15, 45)])

    def testMinutely(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 1),
                          datetime(1997, 9, 2, 9, 2)])

    def testMinutelyInterval(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 2),
                          datetime(1997, 9, 2, 9, 4)])

    def testMinutelyIntervalLarge(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              interval=1501,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 10, 1),
                          datetime(1997, 9, 4, 11, 2)])

    def testMinutelyByMonth(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 0, 1),
                          datetime(1998, 1, 1, 0, 2)])

    def testMinutelyByMonthDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 0, 0),
                          datetime(1997, 9, 3, 0, 1),
                          datetime(1997, 9, 3, 0, 2)])

    def testMinutelyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 0, 0),
                          datetime(1998, 1, 5, 0, 1),
                          datetime(1998, 1, 5, 0, 2)])

    def testMinutelyByWeekDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 1),
                          datetime(1997, 9, 2, 9, 2)])

    def testMinutelyByNWeekDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 2, 9, 1),
                          datetime(1997, 9, 2, 9, 2)])

    def testMinutelyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 0, 1),
                          datetime(1998, 1, 1, 0, 2)])

    def testMinutelyByMonthAndNWeekDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 0, 1),
                          datetime(1998, 1, 1, 0, 2)])

    def testMinutelyByMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 0, 1),
                          datetime(1998, 1, 1, 0, 2)])

    def testMinutelyByMonthAndMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0),
                          datetime(1998, 1, 1, 0, 1),
                          datetime(1998, 1, 1, 0, 2)])

    def testMinutelyByYearDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=4,
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 0, 0),
                          datetime(1997, 12, 31, 0, 1),
                          datetime(1997, 12, 31, 0, 2),
                          datetime(1997, 12, 31, 0, 3)])

    def testMinutelyByYearDayNeg(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=4,
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 0, 0),
                          datetime(1997, 12, 31, 0, 1),
                          datetime(1997, 12, 31, 0, 2),
                          datetime(1997, 12, 31, 0, 3)])

    def testMinutelyByMonthAndYearDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 0, 0),
                          datetime(1998, 4, 10, 0, 1),
                          datetime(1998, 4, 10, 0, 2),
                          datetime(1998, 4, 10, 0, 3)])

    def testMinutelyByMonthAndYearDayNeg(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 0, 0),
                          datetime(1998, 4, 10, 0, 1),
                          datetime(1998, 4, 10, 0, 2),
                          datetime(1998, 4, 10, 0, 3)])

    def testMinutelyByWeekNo(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byweekno=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 5, 11, 0, 0),
                          datetime(1998, 5, 11, 0, 1),
                          datetime(1998, 5, 11, 0, 2)])

    def testMinutelyByWeekNoAndWeekDay(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byweekno=1,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 29, 0, 0),
                          datetime(1997, 12, 29, 0, 1),
                          datetime(1997, 12, 29, 0, 2)])

    def testMinutelyByWeekNoAndWeekDayLarge(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byweekno=52,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 0, 0),
                          datetime(1997, 12, 28, 0, 1),
                          datetime(1997, 12, 28, 0, 2)])

    def testMinutelyByWeekNoAndWeekDayLast(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byweekno=-1,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 0, 0),
                          datetime(1997, 12, 28, 0, 1),
                          datetime(1997, 12, 28, 0, 2)])

    def testMinutelyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 0, 0),
                          datetime(1998, 12, 28, 0, 1),
                          datetime(1998, 12, 28, 0, 2)])

    def testMinutelyByEaster(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byeaster=0,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 12, 0, 0),
                          datetime(1998, 4, 12, 0, 1),
                          datetime(1998, 4, 12, 0, 2)])

    def testMinutelyByEasterPos(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byeaster=1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 13, 0, 0),
                          datetime(1998, 4, 13, 0, 1),
                          datetime(1998, 4, 13, 0, 2)])

    def testMinutelyByEasterNeg(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byeaster=-1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 11, 0, 0),
                          datetime(1998, 4, 11, 0, 1),
                          datetime(1998, 4, 11, 0, 2)])

    def testMinutelyByHour(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byhour=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0),
                          datetime(1997, 9, 2, 18, 1),
                          datetime(1997, 9, 2, 18, 2)])

    def testMinutelyByMinute(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6),
                          datetime(1997, 9, 2, 9, 18),
                          datetime(1997, 9, 2, 10, 6)])

    def testMinutelyBySecond(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 6),
                          datetime(1997, 9, 2, 9, 0, 18),
                          datetime(1997, 9, 2, 9, 1, 6)])

    def testMinutelyByHourAndMinute(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6),
                          datetime(1997, 9, 2, 18, 18),
                          datetime(1997, 9, 3, 6, 6)])

    def testMinutelyByHourAndSecond(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byhour=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 6),
                          datetime(1997, 9, 2, 18, 0, 18),
                          datetime(1997, 9, 2, 18, 1, 6)])

    def testMinutelyByMinuteAndSecond(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 6),
                          datetime(1997, 9, 2, 9, 6, 18),
                          datetime(1997, 9, 2, 9, 18, 6)])

    def testMinutelyByHourAndMinuteAndSecond(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 6),
                          datetime(1997, 9, 2, 18, 6, 18),
                          datetime(1997, 9, 2, 18, 18, 6)])

    def testMinutelyBySetPos(self):
        self.assertEqual(list(rrule(MINUTELY,
                              count=3,
                              bysecond=(15,30,45),
                              bysetpos=(3,-3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 15),
                          datetime(1997, 9, 2, 9, 0, 45),
                          datetime(1997, 9, 2, 9, 1, 15)])

    def testSecondly(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 1),
                          datetime(1997, 9, 2, 9, 0, 2)])

    def testSecondlyInterval(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              interval=2,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 2),
                          datetime(1997, 9, 2, 9, 0, 4)])

    def testSecondlyIntervalLarge(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              interval=90061,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 3, 10, 1, 1),
                          datetime(1997, 9, 4, 11, 2, 2)])

    def testSecondlyByMonth(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0, 0),
                          datetime(1998, 1, 1, 0, 0, 1),
                          datetime(1998, 1, 1, 0, 0, 2)])

    def testSecondlyByMonthDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bymonthday=(1,3),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 3, 0, 0, 0),
                          datetime(1997, 9, 3, 0, 0, 1),
                          datetime(1997, 9, 3, 0, 0, 2)])

    def testSecondlyByMonthAndMonthDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(5,7),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 5, 0, 0, 0),
                          datetime(1998, 1, 5, 0, 0, 1),
                          datetime(1998, 1, 5, 0, 0, 2)])

    def testSecondlyByWeekDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 1),
                          datetime(1997, 9, 2, 9, 0, 2)])

    def testSecondlyByNWeekDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 0),
                          datetime(1997, 9, 2, 9, 0, 1),
                          datetime(1997, 9, 2, 9, 0, 2)])

    def testSecondlyByMonthAndWeekDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0, 0),
                          datetime(1998, 1, 1, 0, 0, 1),
                          datetime(1998, 1, 1, 0, 0, 2)])

    def testSecondlyByMonthAndNWeekDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              byweekday=(TU(1),TH(-1)),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0, 0),
                          datetime(1998, 1, 1, 0, 0, 1),
                          datetime(1998, 1, 1, 0, 0, 2)])

    def testSecondlyByMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0, 0),
                          datetime(1998, 1, 1, 0, 0, 1),
                          datetime(1998, 1, 1, 0, 0, 2)])

    def testSecondlyByMonthAndMonthDayAndWeekDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bymonth=(1,3),
                              bymonthday=(1,3),
                              byweekday=(TU,TH),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 1, 1, 0, 0, 0),
                          datetime(1998, 1, 1, 0, 0, 1),
                          datetime(1998, 1, 1, 0, 0, 2)])

    def testSecondlyByYearDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=4,
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 0, 0, 0),
                          datetime(1997, 12, 31, 0, 0, 1),
                          datetime(1997, 12, 31, 0, 0, 2),
                          datetime(1997, 12, 31, 0, 0, 3)])

    def testSecondlyByYearDayNeg(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=4,
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 31, 0, 0, 0),
                          datetime(1997, 12, 31, 0, 0, 1),
                          datetime(1997, 12, 31, 0, 0, 2),
                          datetime(1997, 12, 31, 0, 0, 3)])

    def testSecondlyByMonthAndYearDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(1,100,200,365),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 0, 0, 0),
                          datetime(1998, 4, 10, 0, 0, 1),
                          datetime(1998, 4, 10, 0, 0, 2),
                          datetime(1998, 4, 10, 0, 0, 3)])

    def testSecondlyByMonthAndYearDayNeg(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=4,
                              bymonth=(4,7),
                              byyearday=(-365,-266,-166,-1),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 10, 0, 0, 0),
                          datetime(1998, 4, 10, 0, 0, 1),
                          datetime(1998, 4, 10, 0, 0, 2),
                          datetime(1998, 4, 10, 0, 0, 3)])

    def testSecondlyByWeekNo(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byweekno=20,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 5, 11, 0, 0, 0),
                          datetime(1998, 5, 11, 0, 0, 1),
                          datetime(1998, 5, 11, 0, 0, 2)])

    def testSecondlyByWeekNoAndWeekDay(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byweekno=1,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 29, 0, 0, 0),
                          datetime(1997, 12, 29, 0, 0, 1),
                          datetime(1997, 12, 29, 0, 0, 2)])

    def testSecondlyByWeekNoAndWeekDayLarge(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byweekno=52,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 0, 0, 0),
                          datetime(1997, 12, 28, 0, 0, 1),
                          datetime(1997, 12, 28, 0, 0, 2)])

    def testSecondlyByWeekNoAndWeekDayLast(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byweekno=-1,
                              byweekday=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 12, 28, 0, 0, 0),
                          datetime(1997, 12, 28, 0, 0, 1),
                          datetime(1997, 12, 28, 0, 0, 2)])

    def testSecondlyByWeekNoAndWeekDay53(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byweekno=53,
                              byweekday=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 12, 28, 0, 0, 0),
                          datetime(1998, 12, 28, 0, 0, 1),
                          datetime(1998, 12, 28, 0, 0, 2)])

    def testSecondlyByEaster(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byeaster=0,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 12, 0, 0, 0),
                          datetime(1998, 4, 12, 0, 0, 1),
                          datetime(1998, 4, 12, 0, 0, 2)])

    def testSecondlyByEasterPos(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byeaster=1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 13, 0, 0, 0),
                          datetime(1998, 4, 13, 0, 0, 1),
                          datetime(1998, 4, 13, 0, 0, 2)])

    def testSecondlyByEasterNeg(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byeaster=-1,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1998, 4, 11, 0, 0, 0),
                          datetime(1998, 4, 11, 0, 0, 1),
                          datetime(1998, 4, 11, 0, 0, 2)])

    def testSecondlyByHour(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byhour=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 0),
                          datetime(1997, 9, 2, 18, 0, 1),
                          datetime(1997, 9, 2, 18, 0, 2)])

    def testSecondlyByMinute(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 0),
                          datetime(1997, 9, 2, 9, 6, 1),
                          datetime(1997, 9, 2, 9, 6, 2)])

    def testSecondlyBySecond(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0, 6),
                          datetime(1997, 9, 2, 9, 0, 18),
                          datetime(1997, 9, 2, 9, 1, 6)])

    def testSecondlyByHourAndMinute(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 0),
                          datetime(1997, 9, 2, 18, 6, 1),
                          datetime(1997, 9, 2, 18, 6, 2)])

    def testSecondlyByHourAndSecond(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byhour=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 0, 6),
                          datetime(1997, 9, 2, 18, 0, 18),
                          datetime(1997, 9, 2, 18, 1, 6)])

    def testSecondlyByMinuteAndSecond(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 6, 6),
                          datetime(1997, 9, 2, 9, 6, 18),
                          datetime(1997, 9, 2, 9, 18, 6)])

    def testSecondlyByHourAndMinuteAndSecond(self):
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              byhour=(6,18),
                              byminute=(6,18),
                              bysecond=(6,18),
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 18, 6, 6),
                          datetime(1997, 9, 2, 18, 6, 18),
                          datetime(1997, 9, 2, 18, 18, 6)])

    def testSecondlyByHourAndMinuteAndSecondBug(self):
        # This explores a bug found by Mathieu Bridon.
        self.assertEqual(list(rrule(SECONDLY,
                              count=3,
                              bysecond=(0,),
                              byminute=(1,),
                              dtstart=parse("20100322120100"))),
                         [datetime(2010, 3, 22, 12, 1),
                          datetime(2010, 3, 22, 13, 1),
                          datetime(2010, 3, 22, 14, 1)])

    def testUntilNotMatching(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970905T080000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testUntilMatching(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970904T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testUntilSingle(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0)])

    def testUntilEmpty(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=parse("19970901T090000"))),
                         [])

    def testUntilWithDate(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=parse("19970902T090000"),
                              until=date(1997, 9, 5))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testWkStIntervalMO(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              interval=2,
                              byweekday=(TU,SU),
                              wkst=MO,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 7, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testWkStIntervalSU(self):
        self.assertEqual(list(rrule(WEEKLY,
                              count=3,
                              interval=2,
                              byweekday=(TU,SU),
                              wkst=SU,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 14, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testDTStartIsDate(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=date(1997, 9, 2))),
                         [datetime(1997, 9, 2, 0, 0),
                          datetime(1997, 9, 3, 0, 0),
                          datetime(1997, 9, 4, 0, 0)])

    def testDTStartWithMicroseconds(self):
        self.assertEqual(list(rrule(DAILY,
                              count=3,
                              dtstart=parse("19970902T090000.5"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testMaxYear(self):
        self.assertEqual(list(rrule(YEARLY,
                              count=3,
                              bymonth=2,
                              bymonthday=31,
                              dtstart=parse("99970902T090000"))),
                         [])

    def testGetItem(self):
        self.assertEqual(rrule(DAILY,
                               count=3,
                               dtstart=parse("19970902T090000"))[0],
                         datetime(1997, 9, 2, 9, 0))

    def testGetItemNeg(self):
        self.assertEqual(rrule(DAILY,
                               count=3,
                               dtstart=parse("19970902T090000"))[-1],
                         datetime(1997, 9, 4, 9, 0))

    def testGetItemSlice(self):
        self.assertEqual(rrule(DAILY,
                               #count=3,
                               dtstart=parse("19970902T090000"))[1:2],
                         [datetime(1997, 9, 3, 9, 0)])

    def testGetItemSliceEmpty(self):
        self.assertEqual(rrule(DAILY,
                               count=3,
                               dtstart=parse("19970902T090000"))[:],
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testGetItemSliceStep(self):
        self.assertEqual(rrule(DAILY,
                               count=3,
                               dtstart=parse("19970902T090000"))[::-2],
                         [datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 2, 9, 0)])

    def testCount(self):
        self.assertEqual(rrule(DAILY,
                               count=3,
                               dtstart=parse("19970902T090000")).count(),
                         3)

    def testContains(self):
        rr = rrule(DAILY, count=3, dtstart=parse("19970902T090000"))
        self.assertEqual(datetime(1997, 9, 3, 9, 0) in rr, True)

    def testContainsNot(self):
        rr = rrule(DAILY, count=3, dtstart=parse("19970902T090000"))
        self.assertEqual(datetime(1997, 9, 3, 9, 0) not in rr, False)

    def testBefore(self):
        self.assertEqual(rrule(DAILY,
                               #count=5,
                               dtstart=parse("19970902T090000"))
                               .before(parse("19970905T090000")),
                         datetime(1997, 9, 4, 9, 0))

    def testBeforeInc(self):
        self.assertEqual(rrule(DAILY,
                               #count=5,
                               dtstart=parse("19970902T090000"))
                               .before(parse("19970905T090000"), inc=True),
                         datetime(1997, 9, 5, 9, 0))

    def testAfter(self):
        self.assertEqual(rrule(DAILY,
                               #count=5,
                               dtstart=parse("19970902T090000"))
                               .after(parse("19970904T090000")),
                         datetime(1997, 9, 5, 9, 0))

    def testAfterInc(self):
        self.assertEqual(rrule(DAILY,
                               #count=5,
                               dtstart=parse("19970902T090000"))
                               .after(parse("19970904T090000"), inc=True),
                         datetime(1997, 9, 4, 9, 0))

    def testBetween(self):
        self.assertEqual(rrule(DAILY,
                               #count=5,
                               dtstart=parse("19970902T090000"))
                               .between(parse("19970902T090000"),
                                        parse("19970906T090000")),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 5, 9, 0)])

    def testBetweenInc(self):
        self.assertEqual(rrule(DAILY,
                               #count=5,
                               dtstart=parse("19970902T090000"))
                               .between(parse("19970902T090000"),
                                        parse("19970906T090000"), inc=True),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 5, 9, 0),
                          datetime(1997, 9, 6, 9, 0)])

    def testCachePre(self):
        rr = rrule(DAILY, count=15, cache=True,
                   dtstart=parse("19970902T090000"))
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 5, 9, 0),
                          datetime(1997, 9, 6, 9, 0),
                          datetime(1997, 9, 7, 9, 0),
                          datetime(1997, 9, 8, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 10, 9, 0),
                          datetime(1997, 9, 11, 9, 0),
                          datetime(1997, 9, 12, 9, 0),
                          datetime(1997, 9, 13, 9, 0),
                          datetime(1997, 9, 14, 9, 0),
                          datetime(1997, 9, 15, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testCachePost(self):
        rr = rrule(DAILY, count=15, cache=True,
                   dtstart=parse("19970902T090000"))
        for x in rr: pass
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 5, 9, 0),
                          datetime(1997, 9, 6, 9, 0),
                          datetime(1997, 9, 7, 9, 0),
                          datetime(1997, 9, 8, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 10, 9, 0),
                          datetime(1997, 9, 11, 9, 0),
                          datetime(1997, 9, 12, 9, 0),
                          datetime(1997, 9, 13, 9, 0),
                          datetime(1997, 9, 14, 9, 0),
                          datetime(1997, 9, 15, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testCachePostInternal(self):
        rr = rrule(DAILY, count=15, cache=True,
                   dtstart=parse("19970902T090000"))
        for x in rr: pass
        self.assertEqual(rr._cache,
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 5, 9, 0),
                          datetime(1997, 9, 6, 9, 0),
                          datetime(1997, 9, 7, 9, 0),
                          datetime(1997, 9, 8, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 10, 9, 0),
                          datetime(1997, 9, 11, 9, 0),
                          datetime(1997, 9, 12, 9, 0),
                          datetime(1997, 9, 13, 9, 0),
                          datetime(1997, 9, 14, 9, 0),
                          datetime(1997, 9, 15, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testCachePreContains(self):
        rr = rrule(DAILY, count=3, cache=True,
                   dtstart=parse("19970902T090000"))
        self.assertEqual(datetime(1997, 9, 3, 9, 0) in rr, True)

    def testCachePostContains(self):
        rr = rrule(DAILY, count=3, cache=True,
                   dtstart=parse("19970902T090000"))
        for x in rr: pass
        self.assertEqual(datetime(1997, 9, 3, 9, 0) in rr, True)

    def testSet(self):
        set = rruleset()
        set.rrule(rrule(YEARLY, count=2, byweekday=TU,
                        dtstart=parse("19970902T090000")))
        set.rrule(rrule(YEARLY, count=1, byweekday=TH,
                        dtstart=parse("19970902T090000")))
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testSetDate(self):
        set = rruleset()
        set.rrule(rrule(YEARLY, count=1, byweekday=TU,
                        dtstart=parse("19970902T090000")))
        set.rdate(datetime(1997, 9, 4, 9))
        set.rdate(datetime(1997, 9, 9, 9))
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testSetExRule(self):
        set = rruleset()
        set.rrule(rrule(YEARLY, count=6, byweekday=(TU,TH),
                        dtstart=parse("19970902T090000")))
        set.exrule(rrule(YEARLY, count=3, byweekday=TH,
                        dtstart=parse("19970902T090000")))
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testSetExDate(self):
        set = rruleset()
        set.rrule(rrule(YEARLY, count=6, byweekday=(TU,TH),
                        dtstart=parse("19970902T090000")))
        set.exdate(datetime(1997, 9, 4, 9))
        set.exdate(datetime(1997, 9, 11, 9))
        set.exdate(datetime(1997, 9, 18, 9))
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testSetExDateRevOrder(self):
        set = rruleset()
        set.rrule(rrule(MONTHLY, count=5, bymonthday=10,
                        dtstart=parse("20040101T090000")))
        set.exdate(datetime(2004, 4, 10, 9, 0))
        set.exdate(datetime(2004, 2, 10, 9, 0))
        self.assertEqual(list(set),
                         [datetime(2004, 1, 10, 9, 0),
                          datetime(2004, 3, 10, 9, 0),
                          datetime(2004, 5, 10, 9, 0)])

    def testSetDateAndExDate(self):
        set = rruleset()
        set.rdate(datetime(1997, 9, 2, 9))
        set.rdate(datetime(1997, 9, 4, 9))
        set.rdate(datetime(1997, 9, 9, 9))
        set.rdate(datetime(1997, 9, 11, 9))
        set.rdate(datetime(1997, 9, 16, 9))
        set.rdate(datetime(1997, 9, 18, 9))
        set.exdate(datetime(1997, 9, 4, 9))
        set.exdate(datetime(1997, 9, 11, 9))
        set.exdate(datetime(1997, 9, 18, 9))
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testSetDateAndExRule(self):
        set = rruleset()
        set.rdate(datetime(1997, 9, 2, 9))
        set.rdate(datetime(1997, 9, 4, 9))
        set.rdate(datetime(1997, 9, 9, 9))
        set.rdate(datetime(1997, 9, 11, 9))
        set.rdate(datetime(1997, 9, 16, 9))
        set.rdate(datetime(1997, 9, 18, 9))
        set.exrule(rrule(YEARLY, count=3, byweekday=TH,
                        dtstart=parse("19970902T090000")))
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testSetCount(self):
        set = rruleset()
        set.rrule(rrule(YEARLY, count=6, byweekday=(TU,TH),
                        dtstart=parse("19970902T090000")))
        set.exrule(rrule(YEARLY, count=3, byweekday=TH,
                        dtstart=parse("19970902T090000")))
        self.assertEqual(set.count(), 3)

    def testSetCachePre(self):
        set = rruleset()
        set.rrule(rrule(YEARLY, count=2, byweekday=TU,
                        dtstart=parse("19970902T090000")))
        set.rrule(rrule(YEARLY, count=1, byweekday=TH,
                        dtstart=parse("19970902T090000")))
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testSetCachePost(self):
        set = rruleset(cache=True)
        set.rrule(rrule(YEARLY, count=2, byweekday=TU,
                        dtstart=parse("19970902T090000")))
        set.rrule(rrule(YEARLY, count=1, byweekday=TH,
                        dtstart=parse("19970902T090000")))
        for x in set: pass
        self.assertEqual(list(set),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testSetCachePostInternal(self):
        set = rruleset(cache=True)
        set.rrule(rrule(YEARLY, count=2, byweekday=TU,
                        dtstart=parse("19970902T090000")))
        set.rrule(rrule(YEARLY, count=1, byweekday=TH,
                        dtstart=parse("19970902T090000")))
        for x in set: pass
        self.assertEqual(list(set._cache),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testStr(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=3\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrType(self):
        self.assertEqual(isinstance(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=3\n"
                              ), rrule), True)

    def testStrForceSetType(self):
        self.assertEqual(isinstance(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=3\n"
                              , forceset=True), rruleset), True)

    def testStrSetType(self):
        self.assertEqual(isinstance(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=2;BYDAY=TU\n"
                              "RRULE:FREQ=YEARLY;COUNT=1;BYDAY=TH\n"
                              ), rruleset), True)

    def testStrCase(self):
        self.assertEqual(list(rrulestr(
                              "dtstart:19970902T090000\n"
                              "rrule:freq=yearly;count=3\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrSpaces(self):
        self.assertEqual(list(rrulestr(
                              " DTSTART:19970902T090000 "
                              " RRULE:FREQ=YEARLY;COUNT=3 "
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrSpacesAndLines(self):
        self.assertEqual(list(rrulestr(
                              " DTSTART:19970902T090000 \n"
                              " \n"
                              " RRULE:FREQ=YEARLY;COUNT=3 \n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrNoDTStart(self):
        self.assertEqual(list(rrulestr(
                              "RRULE:FREQ=YEARLY;COUNT=3\n"
                              , dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrValueOnly(self):
        self.assertEqual(list(rrulestr(
                              "FREQ=YEARLY;COUNT=3\n"
                              , dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrUnfold(self):
        self.assertEqual(list(rrulestr(
                              "FREQ=YEA\n RLY;COUNT=3\n", unfold=True,
                              dtstart=parse("19970902T090000"))),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1998, 9, 2, 9, 0),
                          datetime(1999, 9, 2, 9, 0)])

    def testStrSet(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=2;BYDAY=TU\n"
                              "RRULE:FREQ=YEARLY;COUNT=1;BYDAY=TH\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testStrSetDate(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=1;BYDAY=TU\n"
                              "RDATE:19970904T090000\n"
                              "RDATE:19970909T090000\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 9, 9, 0)])

    def testStrSetExRule(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=6;BYDAY=TU,TH\n"
                              "EXRULE:FREQ=YEARLY;COUNT=3;BYDAY=TH\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testStrSetExDate(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=6;BYDAY=TU,TH\n"
                              "EXDATE:19970904T090000\n"
                              "EXDATE:19970911T090000\n"
                              "EXDATE:19970918T090000\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testStrSetDateAndExDate(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RDATE:19970902T090000\n"
                              "RDATE:19970904T090000\n"
                              "RDATE:19970909T090000\n"
                              "RDATE:19970911T090000\n"
                              "RDATE:19970916T090000\n"
                              "RDATE:19970918T090000\n"
                              "EXDATE:19970904T090000\n"
                              "EXDATE:19970911T090000\n"
                              "EXDATE:19970918T090000\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testStrSetDateAndExRule(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RDATE:19970902T090000\n"
                              "RDATE:19970904T090000\n"
                              "RDATE:19970909T090000\n"
                              "RDATE:19970911T090000\n"
                              "RDATE:19970916T090000\n"
                              "RDATE:19970918T090000\n"
                              "EXRULE:FREQ=YEARLY;COUNT=3;BYDAY=TH\n"
                              )),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 9, 9, 0),
                          datetime(1997, 9, 16, 9, 0)])

    def testStrKeywords(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=3;INTERVAL=3;"
                                    "BYMONTH=3;BYWEEKDAY=TH;BYMONTHDAY=3;"
                                    "BYHOUR=3;BYMINUTE=3;BYSECOND=3\n"
                              )),
                         [datetime(2033, 3, 3, 3, 3, 3),
                          datetime(2039, 3, 3, 3, 3, 3),
                          datetime(2072, 3, 3, 3, 3, 3)])

    def testStrNWeekDay(self):
        self.assertEqual(list(rrulestr(
                              "DTSTART:19970902T090000\n"
                              "RRULE:FREQ=YEARLY;COUNT=3;BYDAY=1TU,-1TH\n"
                              )),
                         [datetime(1997, 12, 25, 9, 0),
                          datetime(1998, 1, 6, 9, 0),
                          datetime(1998, 12, 31, 9, 0)])

    def testBadBySetPos(self):
        self.assertRaises(ValueError,
                          rrule, MONTHLY,
                                 count=1,
                                 bysetpos=0,
                                 dtstart=parse("19970902T090000"))

    def testBadBySetPosMany(self):
        self.assertRaises(ValueError,
                          rrule, MONTHLY,
                                 count=1,
                                 bysetpos=(-1,0,1),
                                 dtstart=parse("19970902T090000"))


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

    def testDateCommandFormatUnicode(self):
        self.assertEqual(parse(u"Thu Sep 25 10:36:28 BRST 2003",
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

    def testNoSeparator1(self):
        self.assertEqual(parse("199709020908"),
                         datetime(1997, 9, 2, 9, 8))

    def testNoSeparator2(self):
        self.assertEqual(parse("19970902090807"),
                         datetime(1997, 9, 2, 9, 8, 7))

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
        
    def testZeroYear(self):
        self.assertEqual(parse("31-Dec-00", default=self.default),
                         datetime(2000, 12, 31))

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

    def testRandomFormat35(self):
        self.assertEqual(parse("2004 10 Apr 11h30m", default=self.default),
                         datetime(2004, 4, 10, 11, 30))

    def testIncreasingCTime(self):
        # This test will check 200 different years, every month, every day,
        # every hour, every minute, every second, and every weekday, using
        # a delta of more or less 1 year, 1 month, 1 day, 1 minute and
        # 1 second.
        delta = timedelta(days=365+31+1, seconds=1+60+60*60)
        dt = datetime(1900, 1, 1, 0, 0, 0, 0)
        for i in range(200):
            self.assertEqual(parse(dt.ctime()), dt)
            dt += delta

    def testIncreasingISOFormat(self):
        delta = timedelta(days=365+31+1, seconds=1+60+60*60)
        dt = datetime(1900, 1, 1, 0, 0, 0, 0)
        for i in range(200):
            self.assertEqual(parse(dt.isoformat()), dt)
            dt += delta

    def testMicrosecondsPrecisionError(self):
        # Skip found out that sad precision problem. :-(
        dt1 = parse("00:11:25.01")
        dt2 = parse("00:12:10.01")
        self.assertEquals(dt1.microsecond, 10000)
        self.assertEquals(dt2.microsecond, 10000)

    def testMicrosecondPrecisionErrorReturns(self):
        # One more precision issue, discovered by Eric Brown.  This should
        # be the last one, as we're no longer using floating points.
        for ms in [100001, 100000, 99999, 99998,
                    10001,  10000,  9999,  9998,
                     1001,   1000,   999,   998,
                      101,    100,    99,    98]:
            dt = datetime(2008, 2, 27, 21, 26, 1, ms)
            self.assertEquals(parse(dt.isoformat()), dt)

    def testHighPrecisionSeconds(self):
        self.assertEquals(parse("20080227T21:26:01.123456789"),
                          datetime(2008, 2, 27, 21, 26, 1, 123456))

    def testCustomParserInfo(self):
        # Custom parser info wasn't working, as Michael Elsdörfer discovered.
        from dateutil.parser import parserinfo, parser
        class myparserinfo(parserinfo):
            MONTHS = parserinfo.MONTHS[:]
            MONTHS[0] = ("Foo", "Foo")
        myparser = parser(myparserinfo())
        dt = myparser.parse("01/Foo/2007")
        self.assertEquals(dt, datetime(2007, 1, 1))


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

    EUROPE_HELSINKI = """
VFppZgAAAAAAAAAAAAAAAAAAAAAAAAAFAAAABQAAAAAAAAB1AAAABQAAAA2kc28Yy85RYMy/hdAV
I+uQFhPckBcDzZAX876QGOOvkBnToJAaw5GQG7y9EBysrhAdnJ8QHoyQEB98gRAgbHIQIVxjECJM
VBAjPEUQJCw2ECUcJxAmDBgQJwVDkCf1NJAo5SWQKdUWkCrFB5ArtPiQLKTpkC2U2pAuhMuQL3S8
kDBkrZAxXdkQMnK0EDM9uxA0UpYQNR2dEDYyeBA2/X8QOBuUkDjdYRA5+3aQOr1DEDvbWJA8pl+Q
Pbs6kD6GQZA/mxyQQGYjkEGEORBCRgWQQ2QbEEQl55BFQ/0QRgXJkEcj3xBH7uYQSQPBEEnOyBBK
46MQS66qEEzMv5BNjowQTqyhkE9ubhBQjIOQUVeKkFJsZZBTN2yQVExHkFUXTpBWLCmQVvcwkFgV
RhBY1xKQWfUoEFq29JBb1QoQXKAREF207BBef/MQX5TOEGBf1RBhfeqQYj+3EGNdzJBkH5kQZT2u
kGYItZBnHZCQZ+iXkGj9cpBpyHmQat1UkGuoW5BsxnEQbYg9kG6mUxBvaB+QcIY1EHFRPBByZhcQ
czEeEHRF+RB1EQAQdi8VkHbw4hB4DveQeNDEEHnu2ZB6sKYQe867kHyZwpB9rp2QfnmkkH+Of5AC
AQIDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQD
BAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAMEAwQDBAME
AwQAABdoAAAAACowAQQAABwgAAkAACowAQQAABwgAAlITVQARUVTVABFRVQAAAAAAQEAAAABAQ==
    """

    NEW_YORK = """
VFppZgAAAAAAAAAAAAAAAAAAAAAAAAAEAAAABAAAABcAAADrAAAABAAAABCeph5wn7rrYKCGAHCh
ms1gomXicKOD6eCkaq5wpTWnYKZTyvCnFYlgqDOs8Kj+peCqE47wqt6H4KvzcPCsvmngrdNS8K6e
S+CvszTwsH4t4LGcUXCyZ0pgs3wzcLRHLGC1XBVwticOYLc793C4BvBguRvZcLnm0mC7BPXwu8a0
YLzk1/C9r9DgvsS58L+PsuDApJvwwW+U4MKEffDDT3bgxGRf8MUvWODGTXxwxw864MgtXnDI+Fdg
yg1AcMrYOWDLiPBw0iP0cNJg++DTdeTw1EDd4NVVxvDWIL/g1zWo8NgAoeDZFYrw2eCD4Nr+p3Db
wGXg3N6JcN2pgmDevmtw34lkYOCeTXDhaUZg4n4vcONJKGDkXhFw5Vcu4OZHLfDnNxDg6CcP8OkW
8uDqBvHw6vbU4Ovm0/Ds1rbg7ca18O6/02Dvr9Jw8J+1YPGPtHDyf5dg82+WcPRfeWD1T3hw9j9b
YPcvWnD4KHfg+Q88cPoIWeD6+Fjw++g74PzYOvD9yB3g/rgc8P+n/+AAl/7wAYfh4AJ34PADcP5g
BGD9cAVQ4GEGQN9yBzDCYgeNGXMJEKRjCa2U9ArwhmQL4IV1DNmi5Q3AZ3YOuYTmD6mD9xCZZucR
iWX4EnlI6BNpR/kUWSrpFUkp+RY5DOoXKQv6GCIpaxkI7fsaAgtsGvIKfBvh7Wwc0ex8HcHPbR6x
zn0fobFtIHYA/SGBk20iVeL+I2qv7iQ1xP4lSpHuJhWm/ycqc+8n/sOAKQpV8CnepYAq6jfxK76H
gSzTVHItnmmCLrM2cy9+S4MwkxhzMWdoBDJy+nQzR0oENFLcdTUnLAU2Mr51NwcOBjgb2vY45vAG
Ofu89jrG0gY72572PK/uhj27gPY+j9CGP5ti9kBvsoZBhH92Qk+UhkNkYXZEL3aHRURDd0XzqQdH
LV/3R9OLB0kNQfdJs20HSu0j90uciYdM1kB3TXxrh062IndPXE2HUJYEd1E8L4dSdeZ3UxwRh1RV
yHdU+/OHVjWqd1blEAdYHsb3WMTyB1n+qPdapNQHW96K91yEtgddvmz3XmSYB1+eTvdgTbSHYYdr
d2ItlodjZ013ZA14h2VHL3dl7VqHZycRd2fNPIdpBvN3aa0eh2rm1XdrljsHbM/x9212HQdur9P3
b1X/B3CPtfdxNeEHcm+X93MVwwd0T3n3dP7fh3Y4lnd23sGHeBh4d3i+o4d5+Fp3ep6Fh3vYPHd8
fmeHfbged35eSYd/mAB3AAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAgMBAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEA
AQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQAB
AAEAAQABAAEAAQABAAEAAQABAAEAAf//x8ABAP//ubAABP//x8ABCP//x8ABDEVEVABFU1QARVdU
AEVQVAAEslgAAAAAAQWk7AEAAAACB4YfggAAAAMJZ1MDAAAABAtIhoQAAAAFDSsLhQAAAAYPDD8G
AAAABxDtcocAAAAIEs6mCAAAAAkVn8qJAAAACheA/goAAAALGWIxiwAAAAwdJeoMAAAADSHa5Q0A
AAAOJZ6djgAAAA8nf9EPAAAAECpQ9ZAAAAARLDIpEQAAABIuE1ySAAAAEzDnJBMAAAAUM7hIlAAA
ABU2jBAVAAAAFkO3G5YAAAAXAAAAAQAAAAE=
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

    def testZoneInfoFileStart1(self):
        tz = zoneinfo.gettz("EST5EDT")
        self.assertEqual(datetime(2003,4,6,1,59,tzinfo=tz).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,tzinfo=tz).tzname(), "EDT")

    def testZoneInfoFileEnd1(self):
        tz = zoneinfo.gettz("EST5EDT")
        self.assertEqual(datetime(2003,10,26,0,59,tzinfo=tz).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,tzinfo=tz).tzname(), "EST")

    def testZoneInfoOffsetSignal(self):
        utc = gettz("UTC")
        nyc = zoneinfo.gettz("America/New_York")
        t0 = datetime(2007,11,4,0,30, tzinfo=nyc)
        t1 = t0.astimezone(utc)
        t2 = t1.astimezone(nyc)
        self.assertEquals(t0, t2)
        self.assertEquals(nyc.dst(t0), timedelta(hours=1))

    def testICalStart1(self):
        tz = tzical(StringIO(self.TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003,4,6,1,59,tzinfo=tz).tzname(), "EST")
        self.assertEqual(datetime(2003,4,6,2,00,tzinfo=tz).tzname(), "EDT")

    def testICalEnd1(self):
        tz = tzical(StringIO(self.TZICAL_EST5EDT)).get()
        self.assertEqual(datetime(2003,10,26,0,59,tzinfo=tz).tzname(), "EDT")
        self.assertEqual(datetime(2003,10,26,1,00,tzinfo=tz).tzname(), "EST")

    def testRoundNonFullMinutes(self):
        # This timezone has an offset of 5992 seconds in 1900-01-01.
        tz = tzfile(StringIO(base64.decodestring(self.EUROPE_HELSINKI)))
        self.assertEquals(str(datetime(1900,1,1,0,0, tzinfo=tz)),
                          "1900-01-01 00:00:00+01:40")

    def testLeapCountDecodesProperly(self):
        # This timezone has leapcnt, and failed to decode until
        # Eugene Oden notified about the issue.
        tz = tzfile(StringIO(base64.decodestring(self.NEW_YORK)))
        self.assertEquals(datetime(2007,3,31,20,12).tzname(), None)

    def testBrokenIsDstHandling(self):
        # tzrange._isdst() was using a date() rather than a datetime().
        # Issue reported by Lennart Regebro.
        dt = datetime(2007,8,6,4,10, tzinfo=tzutc())
        self.assertEquals(dt.astimezone(tz=gettz("GMT+2")),
                          datetime(2007,8,6,6,10, tzinfo=tzstr("GMT+2")))

    def testGMTHasNoDaylight(self):
        # tzstr("GMT+2") improperly considered daylight saving time.
        # Issue reported by Lennart Regebro.
        dt = datetime(2007,8,6,4,10)
        self.assertEquals(gettz("GMT+2").dst(dt), timedelta(0))

    def testGMTOffset(self):
        # GMT and UTC offsets have inverted signal when compared to the
        # usual TZ variable handling.
        dt = datetime(2007,8,6,4,10, tzinfo=tzutc())
        self.assertEquals(dt.astimezone(tz=tzstr("GMT+2")),
                          datetime(2007,8,6,6,10, tzinfo=tzstr("GMT+2")))
        self.assertEquals(dt.astimezone(tz=gettz("UTC-2")),
                          datetime(2007,8,6,2,10, tzinfo=tzstr("UTC-2")))


if __name__ == "__main__":
	unittest.main()

# vim:ts=4:sw=4
