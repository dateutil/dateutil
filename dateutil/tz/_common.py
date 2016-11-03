from six import PY3
from six.moves import _thread

from datetime import datetime, tzinfo
import copy

__all__ = ['tzname_in_python2', 'enfold']


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


# The following is adapted from Alexander Belopolsky's tz library
# https://github.com/abalkin/tz
if hasattr(datetime, 'fold'):
    # This is the pre-python 3.6 fold situation
    def enfold(dt, fold=1):
        return dt.replace(fold=fold)

else:
    class _DatetimeWithFold(datetime):
        """
        This is a class designed to provide a PEP 495-compliant interface for
        Python versions before 3.6.
        """
        __slots__ = ()

        @property
        def fold(self):
            return 1

    def enfold(dt, fold=1):
        if getattr(dt, 'fold', 0) == fold:
            return dt

        args = dt.timetuple()[:6]
        args += (dt.microsecond, dt.tzinfo)

        if fold:
            return _DatetimeWithFold(*args)
        else:
            return datetime.datetime(*args)

def _fromutc(self, dt):
    """
    Given a timezone-aware datetime in a given timezone, calculates a
    timezone-aware datetime in a new timezone.

    Since this is the one time that we *know* we have an unambiguous
    datetime object, we take this opportunity to determine whether the
    datetime is ambiguous and in a "fold" state (e.g. if it's the first
    occurence, chronologically, of the ambiguous datetime).

    :param dt:
        A timezone-aware :class:`datetime.dateime` object.
    """

    # Re-implement the algorithm from Python's datetime.py
    if not isinstance(dt, datetime):
        raise TypeError("fromutc() requires a datetime argument")
    if dt.tzinfo is not self:
        raise ValueError("dt.tzinfo is not self")

    dtoff = dt.utcoffset()
    if dtoff is None:
        raise ValueError("fromutc() requires a non-None utcoffset() "
                         "result")

    # The original datetime.py code assumes that `dst()` defaults to
    # zero during ambiguous times. PEP 495 inverts this presumption, so
    # for pre-PEP 495 versions of python, we need to tweak the algorithm.
    dtdst = dt.dst()
    if dtdst is None:
        raise ValueError("fromutc() requires a non-None dst() result")
    delta = dtoff - dtdst
    if delta:
        dt += delta
        # Set fold=1 so we can default to being in the fold for
        # ambiguous dates.
        dtdst = enfold(dt, fold=1).dst()
        if dtdst is None:
            raise ValueError("fromutc(): dt.dst gave inconsistent "
                             "results; cannot convert")
    return dt + dtdst


class _tzinfo(tzinfo):
    """
    Base class for all ``dateutil`` ``tzinfo`` objects.
    """
    
    def __init__(self, *args, **kwargs):
        super(_tzinfo, self).__init__(*args, **kwargs)

    def is_ambiguous(self, dt):
        """
        Determines whether a given datetime is an ambiguous dat
        """

        dt = dt.replace(tzinfo=self)

        wall_0 = enfold(dt, fold=0)
        wall_1 = enfold(dt, fold=1)

        same_offset = wall_0.utcoffset() == wall_1.utcoffset()
        same_dt = wall_0.replace(tzinfo=None) == wall_1.replace(tzinfo=None)
        
        return same_dt and not same_offset

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
        if self.is_ambiguous(dt_wall):
            delta_wall = dt_wall - dt_utc
            _fold = int(delta_wall == (dt_utc.utcoffset() - dt_utc.dst()))
        else:
            _fold = 0

        return _fold

    def _fold(self, dt):
        return getattr(dt, 'fold', 0)

    def fromutc(self, dt):
        """
        Given a timezone-aware datetime in a given timezone, calculates a
        timezone-aware datetime in a new timezone.

        Since this is the one time that we *know* we have an unambiguous
        datetime object, we take this opportunity to determine whether the
        datetime is ambiguous and in a "fold" state (e.g. if it's the first
        occurance, chronologically, of the ambiguous datetime).

        :param dt:
            A timezone-aware :class:`datetime.dateime` object.
        """
        dt_wall = self._fromutc(dt)

        # Calculate the fold status given the two datetimes.
        _fold = self._fold_status(dt, dt_wall)

        # Set the default fold value for ambiguous dates
        return enfold(dt_wall, fold=_fold)

_tzinfo._fromutc = _fromutc