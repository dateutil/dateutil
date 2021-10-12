=============
relativedelta
=============
.. automodule:: dateutil.relativedelta
   :members:
   :undoc-members:

.. testsetup:: relativedelta

Examples
--------

    >>> from datetime import *; from dateutil.relativedelta import *
    >>> import calendar
    >>> NOW = datetime(2003, 9, 17, 20, 54, 47, 282310)
    >>> TODAY = date(2003, 9, 17)

Let's begin our trip::

    >>> from datetime import *; from dateutil.relativedelta import *
    >>> import calendar

Store some values::

    >>> NOW = datetime.now()
    >>> TODAY = date.today()
    >>> NOW
    datetime.datetime(2003, 9, 17, 20, 54, 47, 282310)
    >>> TODAY
    datetime.date(2003, 9, 17)

Next month

.. doctest:: relativedelta

    >>> NOW+relativedelta(months=+1)
    datetime.datetime(2003, 10, 17, 20, 54, 47, 282310)

Next month, plus one week.

.. doctest:: relativedelta

    >>> NOW+relativedelta(months=+1, weeks=+1)
    datetime.datetime(2003, 10, 24, 20, 54, 47, 282310)

Next month, plus one week, at 10am.

.. doctest:: relativedelta

    >>> TODAY+relativedelta(months=+1, weeks=+1, hour=10)
    datetime.datetime(2003, 10, 24, 10, 0)

Here is another example using an absolute relativedelta.  Notice the use of
year and month (both singular) which causes the values to be *replaced* in the
original datetime rather than performing an arithmetic operation on them.

.. doctest:: relativedelta

    >>> NOW+relativedelta(year=1, month=1)
    datetime.datetime(1, 1, 17, 20, 54, 47, 282310)

Let's try the other way around. Notice that the
hour setting we get in the relativedelta is relative,
since it's a difference, and the weeks parameter
has gone.

.. doctest:: relativedelta

    >>> relativedelta(datetime(2003, 10, 24, 10, 0), TODAY)
    relativedelta(months=+1, days=+7, hours=+10)

One month before one year.

.. doctest:: relativedelta

    >>> NOW+relativedelta(years=+1, months=-1)
    datetime.datetime(2004, 8, 17, 20, 54, 47, 282310)

How does it handle months with different numbers of days?
Notice that adding one month will never cross the month
boundary.

.. doctest:: relativedelta

    >>> date(2003,1,27)+relativedelta(months=+1)
    datetime.date(2003, 2, 27)
    >>> date(2003,1,31)+relativedelta(months=+1)
    datetime.date(2003, 2, 28)
    >>> date(2003,1,31)+relativedelta(months=+2)
    datetime.date(2003, 3, 31)

The logic for years is the same, even on leap years.

If the result falls on a day after the last one of the month, the last day of the month is used instead.

.. doctest::

    >>> date(2003,1,30)+relativedelta(months=+1)
    datetime.date(2003, 2, 28)
    >>> date(2003,5,31)+relativedelta(months=-1)
    datetime.date(2003, 4, 30)

.. doctest:: relativedelta

    >>> date(2000,2,28)+relativedelta(years=+1)
    datetime.date(2001, 2, 28)
    >>> date(2000,2,29)+relativedelta(years=+1)
    datetime.date(2001, 2, 28)

    >>> date(1999,2,28)+relativedelta(years=+1)
    datetime.date(2000, 2, 28)
    >>> date(1999,3,1)+relativedelta(years=+1)
    datetime.date(2000, 3, 1)

    >>> date(2001,2,28)+relativedelta(years=-1)
    datetime.date(2000, 2, 28)
    >>> date(2001,3,1)+relativedelta(years=-1)
    datetime.date(2000, 3, 1)

Next friday

.. doctest:: relativedelta

    >>> TODAY+relativedelta(weekday=FR)
    datetime.date(2003, 9, 19)

    >>> TODAY+relativedelta(weekday=calendar.FRIDAY)
    datetime.date(2003, 9, 19)

Last friday in this month.

.. doctest:: relativedelta

    >>> TODAY+relativedelta(day=31, weekday=FR(-1))
    datetime.date(2003, 9, 26)

Next wednesday (it's today!).

.. doctest:: relativedelta

    >>> TODAY+relativedelta(weekday=WE(+1))
    datetime.date(2003, 9, 17)

Next wednesday, but not today.

.. doctest:: relativedelta

    >>> TODAY+relativedelta(days=+1, weekday=WE(+1))
    datetime.date(2003, 9, 24)

Following
`ISO year week number notation <https://www.cl.cam.ac.uk/~mgk25/iso-time.html>`_
find the first day of the 15th week of 1997.

.. doctest:: relativedelta

    >>> datetime(1997,1,1)+relativedelta(day=4, weekday=MO(-1), weeks=+14)
    datetime.datetime(1997, 4, 7, 0, 0)

How long ago has the millennium changed?

.. doctest:: relativedelta
    :options: +NORMALIZE_WHITESPACE

    >>> relativedelta(NOW, date(2001,1,1))
    relativedelta(years=+2, months=+8, days=+16,
                  hours=+20, minutes=+54, seconds=+47, microseconds=+282310)

How old is John?

.. doctest:: relativedelta
    :options: +NORMALIZE_WHITESPACE

    >>> johnbirthday = datetime(1978, 4, 5, 12, 0)
    >>> relativedelta(NOW, johnbirthday)
    relativedelta(years=+25, months=+5, days=+12,
              hours=+8, minutes=+54, seconds=+47, microseconds=+282310)

It works with dates too.

.. doctest:: relativedelta

    >>> relativedelta(TODAY, johnbirthday)
    relativedelta(years=+25, months=+5, days=+11, hours=+12)

Obtain today's date using the yearday:

.. doctest:: relativedelta

    >>> date(2003, 1, 1)+relativedelta(yearday=260)
    datetime.date(2003, 9, 17)

We can use today's date, since yearday should be absolute
in the given year:

.. doctest:: relativedelta

    >>> TODAY+relativedelta(yearday=260)
    datetime.date(2003, 9, 17)

Last year it should be in the same day:

.. doctest:: relativedelta

    >>> date(2002, 1, 1)+relativedelta(yearday=260)
    datetime.date(2002, 9, 17)

But not in a leap year:

.. doctest:: relativedelta

    >>> date(2000, 1, 1)+relativedelta(yearday=260)
    datetime.date(2000, 9, 16)

We can use the non-leap year day to ignore this:

.. doctest:: relativedelta

    >>> date(2000, 1, 1)+relativedelta(nlyearday=260)
    datetime.date(2000, 9, 17)
