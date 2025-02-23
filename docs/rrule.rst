=====
rrule
=====

.. automodule:: dateutil.rrule
   :undoc-members:

Classes
-------

.. autoclass:: rrule
   :members:
   :undoc-members:
   :inherited-members:
.. autoclass:: rruleset
   :members:
   :undoc-members:
   :inherited-members:

Functions
---------

.. autofunction:: rrulestr


rrule examples
--------------
These examples were converted from the RFC.

Prepare the environment.

.. testsetup:: rrule

    from dateutil.rrule import *
    from dateutil.parser import *
    from datetime import *
    import pprint
    import sys
    sys.displayhook = pprint.pprint

.. doctest:: rrule

    >>> from dateutil.rrule import *
    >>> from dateutil.parser import *
    >>> from datetime import *

    >>> import pprint
    >>> import sys
    >>> sys.displayhook = pprint.pprint

Daily, for 10 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(DAILY, count=10,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 3, 9, 0),
     datetime.datetime(1997, 9, 4, 9, 0),
     datetime.datetime(1997, 9, 5, 9, 0),
     datetime.datetime(1997, 9, 6, 9, 0),
     datetime.datetime(1997, 9, 7, 9, 0),
     datetime.datetime(1997, 9, 8, 9, 0),
     datetime.datetime(1997, 9, 9, 9, 0),
     datetime.datetime(1997, 9, 10, 9, 0),
     datetime.datetime(1997, 9, 11, 9, 0)]

Daily until December 24, 1997

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

    >>> list(rrule(DAILY,
    ...            dtstart=parse("19970902T090000"),
    ...            until=parse("19971224T000000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 3, 9, 0),
     datetime.datetime(1997, 9, 4, 9, 0),
     ...
     datetime.datetime(1997, 12, 21, 9, 0),
     datetime.datetime(1997, 12, 22, 9, 0),
     datetime.datetime(1997, 12, 23, 9, 0)]

Every other day, 5 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(DAILY, interval=2, count=5,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 4, 9, 0),
     datetime.datetime(1997, 9, 6, 9, 0),
     datetime.datetime(1997, 9, 8, 9, 0),
     datetime.datetime(1997, 9, 10, 9, 0)]

Every 10 days, 5 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(DAILY, interval=10, count=5,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 12, 9, 0),
     datetime.datetime(1997, 9, 22, 9, 0),
     datetime.datetime(1997, 10, 2, 9, 0),
     datetime.datetime(1997, 10, 12, 9, 0)]

Everyday in January, for 3 years.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

    >>> list(rrule(YEARLY, bymonth=1, byweekday=range(7),
    ...            dtstart=parse("19980101T090000"),
    ...            until=parse("20000131T090000")))
    [datetime.datetime(1998, 1, 1, 9, 0),
     datetime.datetime(1998, 1, 2, 9, 0),
     ...
     datetime.datetime(1998, 1, 30, 9, 0),
     datetime.datetime(1998, 1, 31, 9, 0),
     datetime.datetime(1999, 1, 1, 9, 0),
     datetime.datetime(1999, 1, 2, 9, 0),
     ...
     datetime.datetime(1999, 1, 30, 9, 0),
     datetime.datetime(1999, 1, 31, 9, 0),
     datetime.datetime(2000, 1, 1, 9, 0),
     datetime.datetime(2000, 1, 2, 9, 0),
     ...
     datetime.datetime(2000, 1, 30, 9, 0),
     datetime.datetime(2000, 1, 31, 9, 0)]

Same thing, in another way.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

    >>> list(rrule(DAILY, bymonth=1,
    ...            dtstart=parse("19980101T090000"),
    ...            until=parse("20000131T090000")))
    [datetime.datetime(1998, 1, 1, 9, 0),
     ...
     datetime.datetime(2000, 1, 31, 9, 0)]

Weekly for 10 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, count=10,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 9, 9, 0),
     datetime.datetime(1997, 9, 16, 9, 0),
     datetime.datetime(1997, 9, 23, 9, 0),
     datetime.datetime(1997, 9, 30, 9, 0),
     datetime.datetime(1997, 10, 7, 9, 0),
     datetime.datetime(1997, 10, 14, 9, 0),
     datetime.datetime(1997, 10, 21, 9, 0),
     datetime.datetime(1997, 10, 28, 9, 0),
     datetime.datetime(1997, 11, 4, 9, 0)]

Every other week, 6 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, interval=2, count=6,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 16, 9, 0),
     datetime.datetime(1997, 9, 30, 9, 0),
     datetime.datetime(1997, 10, 14, 9, 0),
     datetime.datetime(1997, 10, 28, 9, 0),
     datetime.datetime(1997, 11, 11, 9, 0)]

Weekly on Tuesday and Thursday for 5 weeks.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, count=10, wkst=SU, byweekday=(TU,TH),
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 4, 9, 0),
     datetime.datetime(1997, 9, 9, 9, 0),
     datetime.datetime(1997, 9, 11, 9, 0),
     datetime.datetime(1997, 9, 16, 9, 0),
     datetime.datetime(1997, 9, 18, 9, 0),
     datetime.datetime(1997, 9, 23, 9, 0),
     datetime.datetime(1997, 9, 25, 9, 0),
     datetime.datetime(1997, 9, 30, 9, 0),
     datetime.datetime(1997, 10, 2, 9, 0)]

Every other week on Tuesday and Thursday, for 8 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, interval=2, count=8,
    ...            wkst=SU, byweekday=(TU,TH),
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 4, 9, 0),
     datetime.datetime(1997, 9, 16, 9, 0),
     datetime.datetime(1997, 9, 18, 9, 0),
     datetime.datetime(1997, 9, 30, 9, 0),
     datetime.datetime(1997, 10, 2, 9, 0),
     datetime.datetime(1997, 10, 14, 9, 0),
     datetime.datetime(1997, 10, 16, 9, 0)]

Monthly on the 1st Friday for ten occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, count=10, byweekday=FR(1),
    ...            dtstart=parse("19970905T090000")))
    [datetime.datetime(1997, 9, 5, 9, 0),
     datetime.datetime(1997, 10, 3, 9, 0),
     datetime.datetime(1997, 11, 7, 9, 0),
     datetime.datetime(1997, 12, 5, 9, 0),
     datetime.datetime(1998, 1, 2, 9, 0),
     datetime.datetime(1998, 2, 6, 9, 0),
     datetime.datetime(1998, 3, 6, 9, 0),
     datetime.datetime(1998, 4, 3, 9, 0),
     datetime.datetime(1998, 5, 1, 9, 0),
     datetime.datetime(1998, 6, 5, 9, 0)]

Every other month on the 1st and last Sunday of the month for 10 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, interval=2, count=10,
    ...            byweekday=(SU(1), SU(-1)),
    ...            dtstart=parse("19970907T090000")))
    [datetime.datetime(1997, 9, 7, 9, 0),
     datetime.datetime(1997, 9, 28, 9, 0),
     datetime.datetime(1997, 11, 2, 9, 0),
     datetime.datetime(1997, 11, 30, 9, 0),
     datetime.datetime(1998, 1, 4, 9, 0),
     datetime.datetime(1998, 1, 25, 9, 0),
     datetime.datetime(1998, 3, 1, 9, 0),
     datetime.datetime(1998, 3, 29, 9, 0),
     datetime.datetime(1998, 5, 3, 9, 0),
     datetime.datetime(1998, 5, 31, 9, 0)]

Monthly on the second to last Monday of the month for 6 months.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, count=6, byweekday=MO(-2),
    ...            dtstart=parse("19970922T090000")))
    [datetime.datetime(1997, 9, 22, 9, 0),
     datetime.datetime(1997, 10, 20, 9, 0),
     datetime.datetime(1997, 11, 17, 9, 0),
     datetime.datetime(1997, 12, 22, 9, 0),
     datetime.datetime(1998, 1, 19, 9, 0),
     datetime.datetime(1998, 2, 16, 9, 0)]


Monthly on the third to the last day of the month, for 6 months.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, count=6, bymonthday=-3,
    ...            dtstart=parse("19970928T090000")))
    [datetime.datetime(1997, 9, 28, 9, 0),
     datetime.datetime(1997, 10, 29, 9, 0),
     datetime.datetime(1997, 11, 28, 9, 0),
     datetime.datetime(1997, 12, 29, 9, 0),
     datetime.datetime(1998, 1, 29, 9, 0),
     datetime.datetime(1998, 2, 26, 9, 0)]


Monthly on the 2nd and 15th of the month for 5 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, count=5, bymonthday=(2,15),
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 15, 9, 0),
     datetime.datetime(1997, 10, 2, 9, 0),
     datetime.datetime(1997, 10, 15, 9, 0),
     datetime.datetime(1997, 11, 2, 9, 0)]


Monthly on the first and last day of the month for 3 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, count=5, bymonthday=(-1,1,),
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 30, 9, 0),
     datetime.datetime(1997, 10, 1, 9, 0),
     datetime.datetime(1997, 10, 31, 9, 0),
     datetime.datetime(1997, 11, 1, 9, 0),
     datetime.datetime(1997, 11, 30, 9, 0)]


Every 18 months on the 10th thru 15th of the month for 10 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, interval=18, count=10,
    ...            bymonthday=range(10,16),
    ...            dtstart=parse("19970910T090000")))
    [datetime.datetime(1997, 9, 10, 9, 0),
     datetime.datetime(1997, 9, 11, 9, 0),
     datetime.datetime(1997, 9, 12, 9, 0),
     datetime.datetime(1997, 9, 13, 9, 0),
     datetime.datetime(1997, 9, 14, 9, 0),
     datetime.datetime(1997, 9, 15, 9, 0),
     datetime.datetime(1999, 3, 10, 9, 0),
     datetime.datetime(1999, 3, 11, 9, 0),
     datetime.datetime(1999, 3, 12, 9, 0),
     datetime.datetime(1999, 3, 13, 9, 0)]


Every Tuesday, every other month, 6 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, interval=2, count=6, byweekday=TU,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 9, 9, 0),
     datetime.datetime(1997, 9, 16, 9, 0),
     datetime.datetime(1997, 9, 23, 9, 0),
     datetime.datetime(1997, 9, 30, 9, 0),
     datetime.datetime(1997, 11, 4, 9, 0)]


Yearly in June and July for 4 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(YEARLY, count=4, bymonth=(6,7),
    ...            dtstart=parse("19970610T090000")))
    [datetime.datetime(1997, 6, 10, 9, 0),
     datetime.datetime(1997, 7, 10, 9, 0),
     datetime.datetime(1998, 6, 10, 9, 0),
     datetime.datetime(1998, 7, 10, 9, 0)]


Every 3rd year on the 1st, 100th and 200th day for 4 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(YEARLY, count=4, interval=3, byyearday=(1,100,200),
    ...            dtstart=parse("19970101T090000")))
    [datetime.datetime(1997, 1, 1, 9, 0),
     datetime.datetime(1997, 4, 10, 9, 0),
     datetime.datetime(1997, 7, 19, 9, 0),
     datetime.datetime(2000, 1, 1, 9, 0)]


Every 20th Monday of the year, 3 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(YEARLY, count=3, byweekday=MO(20),
    ...            dtstart=parse("19970519T090000")))
    [datetime.datetime(1997, 5, 19, 9, 0),
     datetime.datetime(1998, 5, 18, 9, 0),
     datetime.datetime(1999, 5, 17, 9, 0)]


Monday of week number 20 (where the default start of the week is Monday),
3 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(YEARLY, count=3, byweekno=20, byweekday=MO,
    ...            dtstart=parse("19970512T090000")))
    [datetime.datetime(1997, 5, 12, 9, 0),
     datetime.datetime(1998, 5, 11, 9, 0),
     datetime.datetime(1999, 5, 17, 9, 0)]


The week number 1 may be in the last year.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, count=3, byweekno=1, byweekday=MO,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 12, 29, 9, 0),
     datetime.datetime(1999, 1, 4, 9, 0),
     datetime.datetime(2000, 1, 3, 9, 0)]


And the week numbers greater than 51 may be in the next year.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, count=3, byweekno=52, byweekday=SU,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 12, 28, 9, 0),
     datetime.datetime(1998, 12, 27, 9, 0),
     datetime.datetime(2000, 1, 2, 9, 0)]


Only some years have week number 53:

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, count=3, byweekno=53, byweekday=MO,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1998, 12, 28, 9, 0),
     datetime.datetime(2004, 12, 27, 9, 0),
     datetime.datetime(2009, 12, 28, 9, 0)]


Every Friday the 13th, 4 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(YEARLY, count=4, byweekday=FR, bymonthday=13,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1998, 2, 13, 9, 0),
     datetime.datetime(1998, 3, 13, 9, 0),
     datetime.datetime(1998, 11, 13, 9, 0),
     datetime.datetime(1999, 8, 13, 9, 0)]


Every four years, the first Tuesday after a Monday in November,
3 occurrences (U.S. Presidential Election day):

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(YEARLY, interval=4, count=3, bymonth=11,
    ...            byweekday=TU, bymonthday=(2,3,4,5,6,7,8),
    ...            dtstart=parse("19961105T090000")))
    [datetime.datetime(1996, 11, 5, 9, 0),
     datetime.datetime(2000, 11, 7, 9, 0),
     datetime.datetime(2004, 11, 2, 9, 0)]


The 3rd instance into the month of one of Tuesday, Wednesday or
Thursday, for the next 3 months:

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, count=3, byweekday=(TU,WE,TH),
    ...            bysetpos=3, dtstart=parse("19970904T090000")))
    [datetime.datetime(1997, 9, 4, 9, 0),
     datetime.datetime(1997, 10, 7, 9, 0),
     datetime.datetime(1997, 11, 6, 9, 0)]


The 2nd to last weekday of the month, 3 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MONTHLY, count=3, byweekday=(MO,TU,WE,TH,FR),
    ...            bysetpos=-2, dtstart=parse("19970929T090000")))
    [datetime.datetime(1997, 9, 29, 9, 0),
     datetime.datetime(1997, 10, 30, 9, 0),
     datetime.datetime(1997, 11, 27, 9, 0)]


Every 3 hours from 9:00 AM to 5:00 PM on a specific day.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(HOURLY, interval=3,
    ...            dtstart=parse("19970902T090000"),
    ...            until=parse("19970902T170000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 2, 12, 0),
     datetime.datetime(1997, 9, 2, 15, 0)]


Every 15 minutes for 6 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MINUTELY, interval=15, count=6,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 2, 9, 15),
     datetime.datetime(1997, 9, 2, 9, 30),
     datetime.datetime(1997, 9, 2, 9, 45),
     datetime.datetime(1997, 9, 2, 10, 0),
     datetime.datetime(1997, 9, 2, 10, 15)]


Every hour and a half for 4 occurrences.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(MINUTELY, interval=90, count=4,
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 2, 10, 30),
     datetime.datetime(1997, 9, 2, 12, 0),
     datetime.datetime(1997, 9, 2, 13, 30)]


Every 20 minutes from 9:00 AM to 4:40 PM for two days.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

    >>> list(rrule(MINUTELY, interval=20, count=48,
    ...            byhour=range(9,17), byminute=(0,20,40),
    ...            dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 2, 9, 20),
     ...
     datetime.datetime(1997, 9, 2, 16, 20),
     datetime.datetime(1997, 9, 2, 16, 40),
     datetime.datetime(1997, 9, 3, 9, 0),
     datetime.datetime(1997, 9, 3, 9, 20),
     ...
     datetime.datetime(1997, 9, 3, 16, 20),
     datetime.datetime(1997, 9, 3, 16, 40)]


An example where the days generated makes a difference because of `wkst`.

.. doctest:: rrule
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrule(WEEKLY, interval=2, count=4,
    ...            byweekday=(TU,SU), wkst=MO,
    ...            dtstart=parse("19970805T090000")))
    [datetime.datetime(1997, 8, 5, 9, 0),
     datetime.datetime(1997, 8, 10, 9, 0),
     datetime.datetime(1997, 8, 19, 9, 0),
     datetime.datetime(1997, 8, 24, 9, 0)]

    >>> list(rrule(WEEKLY, interval=2, count=4,
    ...            byweekday=(TU,SU), wkst=SU,
    ...            dtstart=parse("19970805T090000")))
    [datetime.datetime(1997, 8, 5, 9, 0),
     datetime.datetime(1997, 8, 17, 9, 0),
     datetime.datetime(1997, 8, 19, 9, 0),
     datetime.datetime(1997, 8, 31, 9, 0)]


rruleset examples
-----------------
Daily, for 7 days, jumping Saturday and Sunday occurrences.

.. testsetup:: rruleset

    import datetime

    from dateutil.parser import parse
    from dateutil.rrule import rrule, rruleset
    from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
    from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU

    import pprint
    import sys
    sys.displayhook = pprint.pprint

.. doctest:: rruleset
   :options: +NORMALIZE_WHITESPACE

    >>> set = rruleset()
    >>> set.rrule(rrule(DAILY, count=7,
    ...                 dtstart=parse("19970902T090000")))
    >>> set.exrule(rrule(YEARLY, byweekday=(SA,SU),
    ...                  dtstart=parse("19970902T090000")))
    >>> list(set)
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 3, 9, 0),
     datetime.datetime(1997, 9, 4, 9, 0),
     datetime.datetime(1997, 9, 5, 9, 0),
     datetime.datetime(1997, 9, 8, 9, 0)]


Weekly, for 4 weeks, plus one time on day 7, and not on day 16.

.. doctest:: rruleset
   :options: +NORMALIZE_WHITESPACE

    >>> set = rruleset()
    >>> set.rrule(rrule(WEEKLY, count=4,
    ...           dtstart=parse("19970902T090000")))
    >>> set.rdate(datetime.datetime(1997, 9, 7, 9, 0))
    >>> set.exdate(datetime.datetime(1997, 9, 16, 9, 0))
    >>> list(set)
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 7, 9, 0),
     datetime.datetime(1997, 9, 9, 9, 0),
     datetime.datetime(1997, 9, 23, 9, 0)]


rrulestr() examples
-------------------

Every 10 days, 5 occurrences.

.. testsetup:: rrulestr

    from dateutil.parser import parse
    from dateutil.rrule import rruleset, rrulestr

    import pprint
    import sys
    sys.displayhook = pprint.pprint

.. doctest:: rrulestr
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrulestr("""
    ... DTSTART:19970902T090000
    ... RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5
    ... """))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 12, 9, 0),
     datetime.datetime(1997, 9, 22, 9, 0),
     datetime.datetime(1997, 10, 2, 9, 0),
     datetime.datetime(1997, 10, 12, 9, 0)]


Same thing, but passing only the `RRULE` value.

.. doctest:: rrulestr
   :options: +NORMALIZE_WHITESPACE

    >>> list(rrulestr("FREQ=DAILY;INTERVAL=10;COUNT=5",
    ...               dtstart=parse("19970902T090000")))
    [datetime.datetime(1997, 9, 2, 9, 0),
     datetime.datetime(1997, 9, 12, 9, 0),
     datetime.datetime(1997, 9, 22, 9, 0),
     datetime.datetime(1997, 10, 2, 9, 0),
     datetime.datetime(1997, 10, 12, 9, 0)]


Notice that when using a single rule, it returns an
`rrule` instance, unless `forceset` was used.

.. doctest:: rrulestr
   :options: +ELLIPSIS

    >>> rrulestr("FREQ=DAILY;INTERVAL=10;COUNT=5")
    <dateutil.rrule.rrule object at 0x...>

    >>> rrulestr("""
    ... DTSTART:19970902T090000
    ... RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5
    ... """)
    <dateutil.rrule.rrule object at 0x...>

    >>> rrulestr("FREQ=DAILY;INTERVAL=10;COUNT=5", forceset=True)
    <dateutil.rrule.rruleset object at 0x...>


But when an `rruleset` is needed, it is automatically used.

.. doctest:: rrulestr
   :options: +ELLIPSIS

    >>> rrulestr("""
    ... DTSTART:19970902T090000
    ... RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5
    ... RRULE:FREQ=DAILY;INTERVAL=5;COUNT=3
    ... """)
    <dateutil.rrule.rruleset object at 0x...>
