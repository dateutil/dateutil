from six import PY3
from six.moves import _thread

import datetime
import copy

__all__ = ['tzname_in_python2']

def tzname_in_python2(namefunc):
    """Change unicode output into bytestrings in Python 2

    tzname() API changed in Python 3. It used to return bytes, but was changed
    to unicode strings
    """
    def adjust_encoding(*args, **kwargs):
        name = namefunc(*args, **kwargs)
        if name is not None and not PY3:
            name = name.encode()

        return name

    return adjust_encoding


class _tzinfo(datetime.tzinfo):
    """
    Base class for all `dateutil` `tzinfo` objects.
    """
    
    def __init__(self, *args, **kwargs):
        super(_tzinfo, self).__init__(*args, **kwargs)

        self._fold = None

    def _as_fold_naive(self):
        tzi = copy.copy(self)
        tzi._fold = None

        return tzi

    def _fold_status(self, dt_utc, dt_wall):
        """
        Determine the fold status of a "wall" datetime, given a representation
        of the same datetime as a (naive) UTC datetime. This is calculated based
        on the assumption that ``dt.utcoffset() - dt.dst()`` is constant for all
        datetimes, and that this offset is the actual number of hours separating
        ``dt_utc`` and ``dt_wall``.

        :param dt_utc:
            Representation of the datetime as UTC

        :param dt_wall:
            Representation of the datetime as "wall time". This parameter must
            either have a `fold` attribute or have a fold-naive
            :class:`datetime.tzinfo` attached, otherwise the calculation may
            fail.
        """
        _fold = getattr(dt_wall, 'fold', None)          # PEP 495

        if _fold is None:
            # This is always true on the DST side, but _fold has no meaning
            # outside of ambiguous times.
            _fold = (dt_wall - dt_utc) != (dt_utc.utcoffset() - dt_utc.dst())

        return _fold

    def fromutc(self, dt):
        """
        Given a timezone-aware datetime in a given timezone, calculates a
        timezone-aware datetime in a new timezone.

        Since this is the one time that we *know* we have an unambiguous
        datetime object, we take this opportunity to determine whether the
        datetime is ambiguous and in a "fold" state (e.g. if it's the first
        occurance, chronologically, of the ambiguous datetime).

        .. caution ::

            This creates a stateful ``tzinfo`` object that may not behave as
            expected when performing arithmetic on timezone-aware datetimes.

        :param dt:
            A timezone-aware :class:`datetime.dateime` object.
        """
        # Use a fold-naive version of this tzinfo for calculations
        tzi = self._as_fold_naive()
        dt = dt.replace(tzinfo=tzi)

        dt_wall = super(_tzinfo, tzi).fromutc(dt)

        # Calculate the fold status given the two datetimes.
        _fold = self._fold_status(dt, dt_wall)

        # Set the default fold value for ambiguous dates
        if _fold != self._fold:
            tzi._fold = _fold
        else:
            dt_wall = dt_wall.replace(tzinfo=self)

        return dt_wall
    
