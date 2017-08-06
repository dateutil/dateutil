# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def within_delta(dt1, dt2, delta):
    """
    Useful for comparing two datetimes that may a negilible difference
    to be considered equal.
    """
    delta = abs(delta)
    difference = dt1 - dt2
    return -delta <= difference <= delta
