# -*- coding: utf-8 -*-
"""

Constructing datetime or other Parse results from an intermediate
representation.

"""
from calendar import monthrange
import collections  # py3.3 compat
import datetime
import time

from six import text_type, integer_types

from .. import tz
from .. import relativedelta


class _resultbase(object):

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def _repr(self, classname):
        l = []
        for attr in self.__slots__:
            value = getattr(self, attr)
            if value is not None:
                l.append("%s=%s" % (attr, repr(value)))
        return "%s(%s)" % (classname, ", ".join(l))

    def __len__(self):
        return (sum(getattr(self, attr) is not None
                    for attr in self.__slots__))

    def __repr__(self):
        return self._repr(self.__class__.__name__)


class ParseState(_resultbase):
    """
    ParseState contains an unfinished parsing

    Note: This is an internal class, is not considered part of the dateutil
    public API.
    """
    __slots__ = ["year", "month", "day", "weekday",
                 "hour", "minute", "second", "microsecond",
                 "tzname", "tzoffset", "ampm"]

    def _build_result(self, default, tzinfos, ignoretz):
        ret = self._build_naive(default)
        if not ignoretz:
            ret = self._build_tzaware(tzinfos, ret)

        return ret

    def _build_naive(self, default):
        replacement = {}
        for attr in ("year", "month", "day", "hour",
                     "minute", "second", "microsecond"):
            value = getattr(self, attr)
            if value is not None:
                replacement[attr] = value

        if 'day' not in replacement:
            # If the default day exceeds the last day of the month, fall back
            # to the end of the month.
            cyear = default.year if self.year is None else self.year
            cmonth = default.month if self.month is None else self.month
            cday = default.day if self.day is None else self.day

            if cday > monthrange(cyear, cmonth)[1]:
                replacement['day'] = monthrange(cyear, cmonth)[1]

        ret = default.replace(**replacement)

        if self.weekday is not None and not self.day:
            ret = ret + relativedelta.relativedelta(weekday=self.weekday)
        return ret

    def _build_tzaware(self, tzinfos, naive):
        if callable(tzinfos) or (tzinfos and self.tzname in tzinfos):
            tzinfo = self._build_tzinfo(tzinfos,
                                        self.tzname, self.tzoffset)
            aware = naive.replace(tzinfo=tzinfo)
        elif self.tzname and self.tzname in time.tzname:
            aware = naive.replace(tzinfo=tz.tzlocal())
        elif self.tzoffset == 0:
            aware = naive.replace(tzinfo=tz.tzutc())
        elif self.tzoffset:
            aware = naive.replace(tzinfo=tz.tzoffset(self.tzname,
                                                     self.tzoffset))
        else:
            # TODO: Should we do something else in this case?
            aware = naive
        return aware

    def _build_tzinfo(self, tzinfos, tzname, tzoffset):
        if isinstance(tzinfos, collections.Callable):
            tzdata = tzinfos(tzname, tzoffset)
        else:
            tzdata = tzinfos.get(tzname)

        if isinstance(tzdata, datetime.tzinfo):
            tzinfo = tzdata
        elif isinstance(tzdata, text_type):
            tzinfo = tz.tzstr(tzdata)
        elif isinstance(tzdata, integer_types):
            tzinfo = tz.tzoffset(tzname, tzdata)
        else:
            raise ValueError("Offset must be tzinfo subclass, "
                             "tz string, or int offset.")
        return tzinfo

    def _recombine_skipped(self, tokens, skipped_idxs):
        """
        >>> tokens = ["foo", " ", "bar", " ", "19June2000", "baz"]
        >>> skipped_idxs = [0, 1, 2, 5]
        >>> _recombine_skipped(tokens, skipped_idxs)
        ["foo bar", "baz"]
        """
        skipped_tokens = []
        for i, idx in enumerate(sorted(skipped_idxs)):
            if i > 0 and idx - 1 == skipped_idxs[i - 1]:
                skipped_tokens[-1] = skipped_tokens[-1] + tokens[idx]
            else:
                skipped_tokens.append(tokens[idx])

        return skipped_tokens
