# -*- coding: utf-8 -*-
"""
The absolutedelta module handles functions related to absolute elapsed time
between timestamps.

.. versionadded:: 2.6.0
"""

from datetime import datetime, timedelta
from dateutil.tz import tzutc

__all__ = ['absolutedelta']

_UTC = tzutc()

class absolutedelta(object):
    """
    The absolutedelta type is used to represent the absolute duration elapsed
    between two datetimes, whether or not they are timezone aware.

    An :class:`absolutedelta` uses the same interface as
    :class:`datetime.timedelta`, but rather than operating on "wall times",
    all datetime operations are converted to UTC before application.
    
    Example:

    >>> from dateutil.absolutedelta import absolutedelta
    >>> from dateutil.tz import gettz
    >>> from datetime import datetime, timedelta
    >>> NYC = gettz('America/New_York')
    >>> dt = datetime(2016, 3, 13, 1, 30, tzinfo=NYC)
    >>> print(dt + timedelta(hours=2))
    2016-03-13 03:30:00-04:00
    >>> print(dt + absolutedelta(hours=2))
    2016-03-13 04:30:00-04:00
    """

    def __init__(self, days=0, 
                 seconds=0, microseconds=0, milliseconds=0,
                 minutes=0, hours=0, weeks=0):
        self._base_delta = timedelta(days=days,
                                     seconds=seconds, 
                                     microseconds=microseconds,
                                     milliseconds=milliseconds,
                                     minutes=minutes,
                                     hours=hours,
                                     weeks=weeks)

    @classmethod
    def sub(cls, dt1, dt2):
        """
        Calculate the absolute elapsed time between two `datetime`s. These
        datetimes must be either both naive or both timezone-aware, otherwise
        the problem is ill-defined.

        :param dt1:
            A :class:`datetime.datetime` instance or equivalent.

        :param dt2:
            A :class:`datetime.datetime` instance or equivalent, this time
            will be subtracted from ``dt1``.

        :return:
            Returns a :class:`absolutedelta` object representing the absolute
            elapsed time difference between the datetimes.
        """

        if (dt1.tzinfo is None) != (dt2.tzinfo is None):
            raise ValueError('Sub is only defined for two naive datetimes or'
                             'two timezone aware datetimes, not one of each.')

        if dt1.tzinfo is None:
            td = dt1 - dt2
        else:
            td = dt1.astimezone(_UTC) - dt2.astimezone(_UTC)

        return cls.from_timedelta(td)

    @classmethod
    def from_timedelta(cls, td):
        """
        Alternate constructor for :class:`absolutedelta` objects - pass this
        an existing :class:`datetime.timedelta` to get it as an absolute
        delta.

        :param td:
            A :class:`datetime.timedelta` or equivalent.

        :return:
            Returns an equivalent :class:`absolutdelta` object.
        """
        return cls(days=td.days,
                   seconds=td.seconds,
                   microseconds=td.microseconds)

    @property
    def days(self):
        return self._base_delta.days

    @property
    def seconds(self):
        return self._base_delta.seconds

    @property
    def microseconds(self):
        return self._base_delta.microseconds

    def total_seconds(self):
        return _total_seconds(self._base_delta)

    def __add__(self, other):
        if isinstance(other, timedelta):
            return self.__class__.from_timedelta(self._base_delta + other)
        elif isinstance(other, absolutedelta):
            return self.__class__.from_timedelta(self._base_delta + other._base_delta)
        elif isinstance(other, datetime):
            # If it's a naive datetime, just add the base delta
            if other.tzinfo is None:
                return self._base_delta + other
            else:
                dt = self._base_delta + other.astimezone(_UTC)
                return dt.astimezone(other.tzinfo)
        else:
            return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, (timedelta, absolutedelta)):
            return self + -other
        else:
            return NotImplemented

    def __rsub__(self, other):
        return -self + other

    def __neg__(self):
        return self.__class__.from_timedelta(-self._base_delta)

    def __pos__(self):
        return self

    def __abs__(self):
        return self.__class__.from_timedelta(abs(self._base_delta))

    def __eq__(self, other):
        if isinstance(other, timedelta):
            return self._base_delta == other
        elif isinstance(other, absolutedelta):
            return self._base_delta == other._base_delta
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if isinstance(other, timedelta):
            return self._base_delta < other
        elif isinstance(other, absolutedelta):
            return self._base_delta < other._base_delta
        else:
            return NotImplemented

    def __le__(self, other):
        return self < other or self == other

    def __repr__(self):
        if self.microseconds:
            args = (self.days, self.seconds, self.microseconds)
        elif self.seconds:
            args = (self.days, self.seconds)
        else:
            args = '({})'.format(self.days)

        return '{cls}{args}'.format(cls=self.__class__.__name__,
                                    args=args)


    max = timedelta.max
    min = timedelta.min
    resolution = timedelta.resolution


def _total_seconds(td):
    # Python 2.6 doesn't have a total_seconds() method on timedelta objects
    return ((td.seconds + td.days * 86400) * 1000000 +
            td.microseconds) // 1000000

_total_seconds = getattr(timedelta, 'total_seconds', _total_seconds)