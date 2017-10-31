# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time
from dateutil import tz

import re

class Isoparser(object):
    def __init__(self, sep='T'):
        if len(sep) != 1:
            raise ValueError('Separator must be a single character')

        self._sep = sep

    def _read_int(self, cstr, pos, comp_len):
        out = int(cstr[pos:pos + comp_len])
        return out, pos + comp_len

    def isoparse(self, dt_str):
        dt_str = getattr(dt_str, 'read', lambda: dt_str)()
        try:
            return self.isoparse_common(dt_str)
        except ValueError:
            raise

    _ISO_LENGTHS = (4, 2, 2, 2, 2, 2)   # Lengths of ISO components
    _MICROSECOND_END_REGEX = re.compile('[-+Z]+')
    def isoparse_common(self, dt_str):
        """
        This handles the most common subset of ISO-8601 date times, with the
        following formats:

        - ``YYYY``
        - ``YYYYMM``
        - ``YYYY-MM``
        - ``YYYYMMDD``
        - ``YYYY-MM-DD``
        - ``YYYYMMDDTHH``
        - ``YYYYMMDDTHHMM``
        - ``YYYY-MM-DDTHH``
        - ``YYYYMMDDTHH:MM``
        - ``YYYYMMDDTHHMMSS``
        - ``YYYY-MM-DDTHHMM``
        - ``YYYY-MM-DDTHH:MM``
        - ``YYYYMMDDTHH:MM:SS``
        - ``YYYY-MM-DDTHHMMSS``
        - ``YYYYMMDDTHHMMSS.fff``
        - ``YYYY-MM-DDTHH:MM:SS``
        - ``YYYYMMDDTHH:MM:SS.fff``
        - ``YYYY-MM-DDTHHMMSS.fff``
        - ``YYYYMMDDTHHMMSS.ffffff``
        - ``YYYY-MM-DDTHH:MM:SS.fff``
        - ``YYYYMMDDTHH:MM:SS.ffffff``
        - ``YYYY-MM-DDTHHMMSS.ffffff``
        - ``YYYY-MM-DDTHH:MM:SS.ffffff``

        Additionally, anything with a specified time may also have a time zone
        with the forms:

        - `Z`
        - `±HH:MM`
        - `±HHMM`
        - `±HH`
        """
        # Parse the year first
        components, pos = self._parse_isodate_common(dt_str)
        if len(dt_str) > pos:
            if dt_str[pos] == self._sep:
                components += self._parse_isotime(dt_str[pos + 1:])
            else:
                raise ValueError('String contains unknown ISO components')

        return datetime(*components)

    def isoparse_uncommon(self, dt_str):
        """
        This handles the uncommon subset of ISO-8601 datetime formats, including

        - ``--MM-DD``
        - ``--MMDD``
        - ``YYYY-Www``
        - ``YYYYWww``
        - ``YYYY-Www-D``
        - ``YYYYWwwD``
        - ``YYYY-DDD``
        - ``YYYYDDD``
        """

        raise NotImplementedError

    @classmethod
    def parse_isotime(cls, timestr):
        return time(*cls._parse_isotime(timestr))

    @classmethod
    def _parse_isodate_common(cls, dt_str):
        len_str = len(dt_str)
        components = [1, 1, 1]

        pos = 0
        if len_str < 4:
            raise ValueError('ISO string too short')

        # Year
        components[0] = int(dt_str[0:4])
        pos = 4
        if pos >= len_str:
            return components, pos

        has_sep = dt_str[pos] == '-'
        if has_sep:
            pos += 1

        # Month
        components[1] = int(dt_str[pos:pos + 2])
        pos += 2

        if pos >= len_str:
            return components, pos

        if has_sep:
            if dt_str[pos] != '-':
                raise ValueError('Invalid separator in ISO string')
            pos += 1

        # Day
        components[2] = int(dt_str[pos:pos + 2])
        return components, pos + 2

    @classmethod
    def _parse_isotime(cls, timestr):
        len_str = len(timestr)
        components = [0, 0, 0, 0, None]
        pos = 0
        comp = -1

        has_sep = len_str >= 3 and timestr[2] == ':'

        while pos < len_str and comp < 5:
            comp += 1

            if timestr[pos] in '-+Z':
                components[-1] = cls.parse_tzstr(timestr[pos:])
                pos = len_str
                break

            if comp < 3:
                # Hour, minute, second
                components[comp] = int(timestr[pos:pos + 2])
                pos += 2
                if has_sep and pos < len_str and timestr[pos] == ':':
                    pos += 1

            if comp == 3:
                # Microsecond
                if timestr[pos] != '.':
                    continue

                pos += 1
                us_str = cls._MICROSECOND_END_REGEX.split(timestr[pos:pos + 6],
                                                          1)[0]

                components[comp] = int(us_str) * 10**(6 - len(us_str))
                pos += len(us_str)

        if pos < len_str:
            raise ValueError('Unused components in ISO string')

        return components

    @classmethod
    def parse_tzstr(cls, tzstr, zero_as_utc=True):
        if tzstr == 'Z':
            return tz.tzutc()

        if 6 < len(tzstr) < 3:
            raise ValueError('Time zone offset must be 1 or 3-6 characters')

        if tzstr[0] == '-':
            mult = -1
        elif tzstr[0] == '+':
            mult = 1
        else:
            raise ValueError('Time zone offset requires sign')

        hours = int(tzstr[1:3])
        if len(tzstr) == 3:
            minutes = 0
        else:
            minutes = int(tzstr[(4 if tzstr[3] == ':' else 3):])

        if zero_as_utc and hours == 0 and minutes == 0:
            return tz.tzutc()
        else:
            return tz.tzoffset(None, mult * timedelta(hours=hours,
                                                      minutes=minutes))

DEFAULT_ISOPARSER = Isoparser()
def isoparse(dt_str):
    return DEFAULT_ISOPARSER.isoparse(dt_str)