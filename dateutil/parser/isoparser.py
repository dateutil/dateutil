# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
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
            return self.isoparse_quick(dt_str)
        except ValueError as e:
            raise

    _ISO_LENGTHS = (4, 2, 2, 2, 2, 2)   # Lengths of ISO components
    _MICROSECOND_END_REGEX = re.compile('[-+Z]+')
    def isoparse_quick(self, dt_str):
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
        len_str = len(dt_str)

        if len_str < 4:
            raise ValueError('ISO string too short')

        # Parse the year first
        components = [1, 1, 1, 0, 0, 0, 0, None]
        pos = 0
        comp = -1
        sep = '-'
        has_sep = len_str > 4 and dt_str[4] == sep

        while pos < len_str and comp <= 7:
            comp += 1

            if comp == 3:
                # After component 2 has been processed, check for the separators
                if dt_str[pos] != self._sep:
                    raise ValueError('Invalid separator in ISO string')

                pos += 1
                sep = ':'
                has_sep = len_str > pos + 2 and dt_str[pos + 2] == sep

            if has_sep and comp in {1, 2, 4, 5} and dt_str[pos] == sep:
                pos += 1

            if dt_str[pos] in '+-Z':
                components[-1] = self.process_tzstr(dt_str[pos:])
                pos = len_str
                break

            if comp <= 5:
                # First 5 components just read an integer
                components[comp], pos = self._read_int(dt_str, pos,
                                                       self._ISO_LENGTHS[comp])
                continue

            if comp == 6:
                # Parse the microseconds portion
                if dt_str[pos] != '.':
                    continue

                pos += 1
                us_str = self._MICROSECOND_END_REGEX.split(dt_str[pos:pos+6], 1)[0]

                components[comp] = int(us_str) * 10**(6 - len(us_str))
                pos += len(us_str)

        if pos < len_str:
            raise ValueError('String contains unknown ISO components')

        return datetime(*components)

    @classmethod
    def process_tzstr(cls, tzstr, zero_as_utc=True):
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