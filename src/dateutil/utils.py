"""
This module offers general convenience and utility functions for dealing with
datetimes.

.. versionadded:: 2.7.0
"""

from __future__ import annotations

from datetime import datetime, time

TYPE_CHECKING = False

if TYPE_CHECKING:
    import datetime as _datetime
    from typing import TypeVar

    from . import _typing

    _WithTimezoneT = TypeVar("_WithTimezoneT", bound=_typing._WithTimezone)
    _DeltaT = TypeVar("_DeltaT", bound=_typing._Delta)
    _OperandT = TypeVar("_OperandT")


def today(tzinfo: _datetime.tzinfo | None = None) -> datetime:
    """
    Returns a :py:class:`datetime` representing the current day at midnight

    :param tzinfo:
        The time zone to attach (also used to determine the current day).

    :return:
        A :py:class:`datetime.datetime` object representing the current day
        at midnight.
    """

    dt = datetime.now(tzinfo)
    return datetime.combine(dt.date(), time(0, tzinfo=tzinfo))


def default_tzinfo(
    dt: _WithTimezoneT, tzinfo: _datetime.tzinfo | None
) -> _WithTimezoneT:
    """
    Sets the ``tzinfo`` parameter on naive datetimes only

    This is useful for example when you are provided a datetime that may have
    either an implicit or explicit time zone, such as when parsing a time zone
    string.

    .. doctest::

        >>> from dateutil.tz import tzoffset
        >>> from dateutil.parser import parse
        >>> from dateutil.utils import default_tzinfo
        >>> dflt_tz = tzoffset("EST", -18000)
        >>> print(default_tzinfo(parse('2014-01-01 12:30 UTC'), dflt_tz))
        2014-01-01 12:30:00+00:00
        >>> print(default_tzinfo(parse('2014-01-01 12:30'), dflt_tz))
        2014-01-01 12:30:00-05:00

    :param dt:
        The datetime on which to replace the time zone

    :param tzinfo:
        The :py:class:`datetime.tzinfo` subclass instance to assign to
        ``dt`` if (and only if) it is naive.

    :return:
        Returns an aware :py:class:`datetime.datetime`.
    """
    if dt.tzinfo is not None:
        return dt
    else:
        return dt.replace(tzinfo=tzinfo)


def within_delta(
    dt1: _typing._Subtractable[_OperandT, _DeltaT],
    dt2: _OperandT,
    delta: _DeltaT,
) -> bool:
    """
    Useful for comparing two datetimes that may have a negligible difference
    to be considered equal.
    """
    delta = abs(delta)
    difference = dt1 - dt2
    return -delta <= difference <= delta
