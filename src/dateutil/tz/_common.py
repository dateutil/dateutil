from __future__ import annotations

from datetime import datetime, timedelta, tzinfo
from functools import wraps


TYPE_CHECKING = False

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Protocol, Self, TypeVar

    _TzInfoT = TypeVar("_TzInfoT", bound=tzinfo)
    _DatetimeT = TypeVar("_DatetimeT", bound=datetime)

    class _Foldable(Protocol):
        def replace(self, *, fold: int) -> Self: ...

    _FoldableT = TypeVar("_FoldableT", bound=_Foldable)


ZERO = timedelta(0)

__all__ = ["enfold"]


# The following is adapted from Alexander Belopolsky's tz library
# https://github.com/abalkin/tz
def enfold(dt: _FoldableT, fold: int = 1) -> _FoldableT:
    """Returns a datetime with the ``fold`` attribute set to ``fold``.

    :param fold:
        The value for the ``fold`` attribute, either 0 or 1.

    :return:
        A :class:`datetime.datetime` with the requested ``fold`` value.

    .. versionadded:: 2.6.0
    """
    return dt.replace(fold=fold)


def _validate_fromutc_inputs(
    f: Callable[[_TzInfoT, _DatetimeT], _DatetimeT],
) -> Callable[[_TzInfoT, _DatetimeT], _DatetimeT]:
    """
    The CPython version of ``fromutc`` checks that the input is a ``datetime``
    object and that ``self`` is attached as its ``tzinfo``.
    """
    @wraps(f)
    def fromutc(self: _TzInfoT, dt: _DatetimeT) -> _DatetimeT:
        if not isinstance(dt, datetime):
            raise TypeError("fromutc() requires a datetime argument")
        if dt.tzinfo is not self:
            raise ValueError("dt.tzinfo is not self")

        return f(self, dt)

    return fromutc


class _tzinfo(tzinfo):
    """
    Base class for all ``dateutil`` ``tzinfo`` objects.
    """

    def is_ambiguous(self, dt: datetime) -> bool:
        """
        Whether or not the "wall time" of a given datetime is ambiguous in this
        zone.

        :param dt:
            A :py:class:`datetime.datetime`, naive or time zone aware.


        :return:
            Returns ``True`` if ambiguous, ``False`` otherwise.

        .. versionadded:: 2.6.0
        """

        dt = dt.replace(tzinfo=self)

        wall_0 = enfold(dt, fold=0)
        wall_1 = enfold(dt, fold=1)

        same_offset = wall_0.utcoffset() == wall_1.utcoffset()
        same_dt = wall_0.replace(tzinfo=None) == wall_1.replace(tzinfo=None)

        return same_dt and not same_offset

    def _fold_status(self, dt_utc: datetime, dt_wall: datetime) -> int:
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
            utcoffset = dt_utc.utcoffset()
            dst = dt_utc.dst()
            assert utcoffset is not None and dst is not None
            _fold = int(delta_wall == (utcoffset - dst))
        else:
            _fold = 0

        return _fold

    def _fromutc(self, dt: datetime) -> datetime:
        """
        Given a timezone-aware datetime in a given timezone, calculates a
        timezone-aware datetime in a new timezone.

        Since this is the one time that we *know* we have an unambiguous
        datetime object, we take this opportunity to determine whether the
        datetime is ambiguous and in a "fold" state (e.g. if it's the first
        occurrence, chronologically, of the ambiguous datetime).

        :param dt:
            A timezone-aware :class:`datetime.datetime` object.
        """

        # Re-implement the algorithm from Python's datetime.py
        dtoff = dt.utcoffset()
        if dtoff is None:
            raise ValueError("fromutc() requires a non-None utcoffset() "
                             "result")

        # The original datetime.py code assumes that `dst()` defaults to
        # zero during ambiguous times. PEP 495 inverts this presumption, so
        # select fold=1 when calculating the DST adjustment below.
        dtdst = dt.dst()
        if dtdst is None:
            raise ValueError("fromutc() requires a non-None dst() result")
        delta = dtoff - dtdst

        dt += delta
        # Set fold=1 so we can default to being in the fold for
        # ambiguous dates.
        dtdst = enfold(dt, fold=1).dst()
        if dtdst is None:
            raise ValueError("fromutc(): dt.dst gave inconsistent "
                             "results; cannot convert")
        return dt + dtdst

    @_validate_fromutc_inputs
    def fromutc(self, dt: datetime) -> datetime:
        """
        Given a timezone-aware datetime in a given timezone, calculates a
        timezone-aware datetime in a new timezone.

        Since this is the one time that we *know* we have an unambiguous
        datetime object, we take this opportunity to determine whether the
        datetime is ambiguous and in a "fold" state (e.g. if it's the first
        occurrence, chronologically, of the ambiguous datetime).

        :param dt:
            A timezone-aware :class:`datetime.datetime` object.
        """
        dt_wall = self._fromutc(dt)

        # Calculate the fold status given the two datetimes.
        _fold = self._fold_status(dt, dt_wall)

        # Set the default fold value for ambiguous dates
        return enfold(dt_wall, fold=_fold)


class tzrangebase(_tzinfo):
    """
    This is an abstract base class for time zones represented by an annual
    transition into and out of DST. Child classes should implement the following
    methods:

        * ``__init__(self, *args, **kwargs)``
        * ``transitions(self, year)`` - this is expected to return a tuple of
          datetimes representing the DST on and off transitions in standard
          time.

    A fully initialized ``tzrangebase`` subclass should also provide the
    following attributes:
        * ``hasdst``: Boolean whether or not the zone uses DST.
        * ``_dst_offset`` / ``_std_offset``: :class:`datetime.timedelta` objects
          representing the respective UTC offsets.
        * ``_dst_abbr`` / ``_std_abbr``: Strings representing the timezone short
          abbreviations in DST and STD, respectively.
        * ``_hasdst``: Whether or not the zone has DST.

    .. versionadded:: 2.6.0
    """

    hasdst: bool
    _std_offset: timedelta
    _dst_offset: timedelta
    _std_abbr: str | None
    _dst_abbr: str | None
    if TYPE_CHECKING:

        def transitions(
            self, year: int
        ) -> tuple[datetime, datetime] | None: ...

    def __init__(self) -> None:
        raise NotImplementedError('tzrangebase is an abstract base class')

    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        isdst = self._isdst(dt)

        if isdst is None:
            return None
        elif isdst:
            return self._dst_offset
        else:
            return self._std_offset

    def dst(self, dt: datetime | None) -> timedelta | None:
        isdst = self._isdst(dt)

        if isdst is None:
            return None
        elif isdst:
            return self._dst_base_offset
        else:
            return ZERO

    def tzname(self, dt: datetime | None) -> str | None:
        if self._isdst(dt):
            return self._dst_abbr
        else:
            return self._std_abbr

    def fromutc(self, dt: datetime) -> datetime:
        """ Given a datetime in UTC, return local time """
        if not isinstance(dt, datetime):
            raise TypeError("fromutc() requires a datetime argument")

        if dt.tzinfo is not self:
            raise ValueError("dt.tzinfo is not self")

        # Get transitions - if there are none, fixed offset
        transitions = self.transitions(dt.year)
        if transitions is None:
            offset = self.utcoffset(dt)
            assert offset is not None
            return dt + offset

        # Get the transition times in UTC
        dston, dstoff = transitions

        dston -= self._std_offset
        dstoff -= self._std_offset

        utc_transitions = (dston, dstoff)
        dt_utc = dt.replace(tzinfo=None)

        isdst = self._naive_isdst(dt_utc, utc_transitions)

        if isdst:
            dt_wall = dt + self._dst_offset
        else:
            dt_wall = dt + self._std_offset

        _fold = int(not isdst and self.is_ambiguous(dt_wall))

        return enfold(dt_wall, fold=_fold)

    def is_ambiguous(self, dt: datetime) -> bool:
        """
        Whether or not the "wall time" of a given datetime is ambiguous in this
        zone.

        :param dt:
            A :py:class:`datetime.datetime`, naive or time zone aware.


        :return:
            Returns ``True`` if ambiguous, ``False`` otherwise.

        .. versionadded:: 2.6.0
        """
        if not self.hasdst:
            return False

        transitions = self.transitions(dt.year)
        assert transitions is not None
        start, end = transitions

        dt = dt.replace(tzinfo=None)
        return (end <= dt < end + self._dst_base_offset)

    def _isdst(self, dt: datetime | None) -> bool | None:
        if not self.hasdst:
            return False
        elif dt is None:
            return None

        transitions = self.transitions(dt.year)

        if transitions is None:
            return False

        dt = dt.replace(tzinfo=None)

        isdst = self._naive_isdst(dt, transitions)

        # Handle ambiguous dates
        if not isdst and self.is_ambiguous(dt):
            return not dt.fold
        else:
            return isdst

    def _naive_isdst(
        self, dt: datetime, transitions: tuple[datetime, datetime]
    ) -> bool:
        dston, dstoff = transitions

        dt = dt.replace(tzinfo=None)

        if dston < dstoff:
            isdst = dston <= dt < dstoff
        else:
            isdst = not dstoff <= dt < dston

        return isdst

    @property
    def _dst_base_offset(self) -> timedelta:
        return self._dst_offset - self._std_offset

    __hash__ = None

    def __repr__(self) -> str:
        return "%s(...)" % self.__class__.__name__

    __reduce__ = object.__reduce__
