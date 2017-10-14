# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, time


def today(tzinfo=None):
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


def default_tzinfo(dt, tzinfo):
    """
    Sets the the ``tzinfo`` parameter on naive datetimes only

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


def within_delta(dt1, dt2, delta):
    """
    Useful for comparing two datetimes that may a negilible difference
    to be considered equal.
    """
    delta = abs(delta)
    difference = dt1 - dt2
    return -delta <= difference <= delta
