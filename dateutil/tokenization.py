#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import re
import calendar

from six import text_type as unicode


class Token:
    @staticmethod
    def is_valid_day(year, month, day):
        """is_valid_day(year, month, day)

        >>> Token.is_valid_day(None, None, 14)
        True

        >>> Token.is_valid_day(None, 11, 30)
        True

        >>> Token.is_valid_day(None, 11, 31)
        False

        >>> Token.is_valid_day(None, 11, 31)
        False

        """
        if year is None and month is None:
            ub = 31
        elif year is None:
            # Default to assuming leap year
            ub = {
                1: 31,
                2: 29,
                3: 31,
                4: 30,
                5: 31,
                6: 30,
                7: 31,
                8: 31,
                9: 30,
                10: 31,
                11: 30,
                12: 31,
                }.get(int(month), 31)
        else:
            try:
                ub = calendar.monthrange(int(year), int(month))[1]
            except (calendar.IllegalMonthError, ValueError):
                # monthrange calls weekday, which calls
                # datetime.date(y, m, d).weekday(), which will raise a
                # ValueError if this is invalid.
                return False
        return 1 <= day <= ub

    @staticmethod
    def is_valid_hour(token):
        """is_valid_hour(token)

        >>> Token.is_valid_hour('6')
        True

        >>> Token.is_valid_hour('r')
        False
        
        >>> Token.is_valid_hour('25')
        False

        >>> Token.is_valid_hour('0011')
        False


        return valid_hour_bool
        """
        try:
            value = float(token)
        except ValueError:
            return False
        # Require that this be an integer
        return '.' not in token and len(token) <= 2 and 0 <= value < 24

    @staticmethod
    def is_valid_minute(token):
        try:
            value = float(token)
        except ValueError:
            return False
        # Require that this be an integer
        return '.' not in token and len(token) == 2 and 0 <= value < 60

    @staticmethod
    def is_valid_second(token):
        """is_valid_second(token)

        >>> Token.is_valid_second('d4')
        False

        >>> Token.is_valid_second('4.67')
        False

        >>> Token.is_valid_second('44.67')
        True

        return valid_second_bool
        """
        try:
            value = float(token)
        except ValueError:
            return False
        return len(token.split('.', 1)[0]) == 2 and 0 <= value < 60

    @staticmethod
    def is_valid_hhmm(token):
        return (Token.is_valid_hour(token[:2])
            and Token.is_valid_minute(token[2:])
            )

    @staticmethod
    def is_valid_hhmmss(token):
        return (Token.is_valid_hour(token[:2])
            and Token.is_valid_minute(token[2:4])
            and Token.is_valid_second(token[4:])
                )

    @staticmethod
    def is_valid_yyyymmdd(token):
        """is_valid_yyyymmdd(token)

        >>> Token.is_valid_yyyymmdd('20141232')
        False

        >>> Token.is_valid_yyyymmdd('18121224')
        True

        return valid_bool
        """
        year = token[:4]
        month = token[4:6]
        day = token[6:]
        return (len(token) == 8
            and token.isdigit()
            and 1 <= int(month) <= 12
            and Token.is_valid_day(int(year), int(month), int(day))
            )

    @staticmethod
    def is_ordinal(token):
        """is_ordinal(token)

        >>> Token.is_ordinal('4th')
        True

        >>> Token.is_ordinal('Bar')
        False

        return is_ord
        """
        match = re.search('^1st|2nd|3rd|\d{1,2}th$', token)
        return match is not None

    @staticmethod
    def is_tzlike(token):
        # Requiring a lower-bound on the token length helps prevent
        # False-positives
        return ((token == 'Z' or 3 <= len(token) <= 5)
            and all(c in string.ascii_uppercase for c in token)
            )

    @staticmethod
    def is_buoyant(token):
        """is_buoyant(token)

        buoyant --> will it float

        return buoyancy
        """
        return check_float_like(token)


class Window:
    """ Window: A Tuple of Tokens"""
    @staticmethod
    def is_ymdlike(tup):
        """is_ymdlike(tup)

        >>> Window.is_ymdlike(('2004',))
        False

        >>> Window.is_ymdlike(('08', '/', '21', ',', '2016'))
        False

        >>> Window.is_ymdlike(('04', '/', '04', '/', '04', '/', '05',))
        False

        >>> Window.is_ymdlike(('04', '/', '04', '/', '04', ' '))
        True

        >>> Window.is_ymdlike(('04', '/', '04', '/', '04', '/'))
        False


        >>> Window.is_ymdlike(('04', 'd', '04', 'd', '04'))
        False


        >>> Window.is_ymdlike(('04', '/', '04', '/', '04', ':'))
        False

        return ymd_like_bool
        """
        if len(tup) not in [5, 6]:
            return False

        (v1, sep1, v2, sep2, v3) = tup[:5]
        tail = None
        if len(tup) == 6:
            tail = tup[-1]

        if sep1 != sep2:
            return False
        elif tail == sep1:
            # e.g. 04/04/04/05
            return False
        elif sep1 not in ['-', '/']:
            return False
        elif tail is not None and not tail.isspace():
            return False
        return v1.isdigit() and v2.isdigit() and v2.isdigit()

    @staticmethod
    def is_timelike(tup, hour_only=False, validate=True):
        """is_timelike(tup, hour_only=False, validate=True)

        Look at the token at the given index, and the two tokens following it
        (If there are fewer than two tokens following it, return False).
        Can these three tokens together form a HH:MM time, e.g. "4:31"?
        
        The third token may also have a decimal component, in which case
        we are looking at a MM:SS.fff portion of a time, e.g. "31:56.345".

        These will often come in pairs, like "4:31:56.345"

        If the optional argument hour_only is set to True, then the
        checks are tightened to require that this be HH:MM, disallowing
        leading integers above 23, and disallowing non-integer trailing
        components

        If the optional argument validate (which defaults to True) is set to
        False, then the function will not check that the hour/minute/second
        values are valid, and will allow through e.g. "22:64".

        return timelike
        

        >>> tup = ('02', ':', '61.45',)
        >>> Window.is_timelike(tup, validate=False)
        True

        >>> tup = ('d2', ':', '47',)
        >>> Window.is_timelike(tup, validate=True)
        False

        >>> tup = ('2', '-', '47',)
        >>> Window.is_timelike(tup, validate=True)
        False

        >>> tup = ('0.2', ':', '47.0',)
        >>> Window.is_timelike(tup, validate=True)
        False

        >>> tup = ('25', ':', '47',)
        >>> Window.is_timelike(tup, hour_only=True, validate=True)
        False

        >>> tup = ('25', ':', '47',)
        >>> Window.is_timelike(tup, hour_only=False, validate=True)
        True

        >>> tup = ('25', ':', '4',)
        >>> Window.is_timelike(tup, hour_only=False, validate=True)
        False

        >>> tup = ('25', ':', '488',)
        >>> Window.is_timelike(tup, hour_only=False, validate=True)
        False

        >>> tup = ('25', ':', '48t8',)
        >>> Window.is_timelike(tup, hour_only=False, validate=True)
        False

        >>> tup = ('25', ':', '48.d',)
        >>> Window.is_timelike(tup, hour_only=False, validate=True)
        False

        >>> tup = ('23', ':', '48.0',)
        >>> Window.is_timelike(tup, hour_only=False, validate=True)
        True

        """
        if len(tup) != 3:
            return False
            
        (HM, colon, MS) = tup
        # HM --> Hour or Minute
        # MS --> Minute or Second
        # colon --> : between HH:MM or MM:SS
        
        joined = ''.join(tup)
        if not validate and re.search('^\d{1,2}:\d{2}([,\.]\d+)?$', joined):
            return True

        if colon != ':':
            return False
        elif not (HM.isdigit() and int(HM) <= 59):
            return False
        elif hour_only and not (int(HM) <= 23 and len(MS) == 2):
            return False

        integral = MS[:2]
        fractional = MS[3:]

        if not (integral.isdigit() and
                len(integral) == 2 and int(integral) <= 59):
            return False

        elif len(MS) == 2:
            # No fractional part, so this checks out.
            return True
            
        elif MS[2] not in ['.', ',']:
            # We allow for commas for internationalization and for
            # python's logging format.  Anything else indicates a
            # non-minute-or-second
            return False

        elif not fractional.isdigit():
            # Note that ''.isdigit() returns False, so this handles
            # the case of a trailing "." or ","
            return False

        return True


_inf = float('INF')
_minf = float('-INF')
def check_float_like(item):
    """check_float_like(item)

    >>> check_float_like(2)
    True

    >>> check_float_like(2.2)
    True

    >>> check_float_like('-2')
    True

    >>> check_float_like('orange')
    False

    >>> float('Inf')
    inf
    >>> check_float_like('INF')
    False

    >>> float('nan')
    nan
    >>> check_float_like('NaN')
    False

    >>> float('1e4')
    10000.0
    >>> check_float_like('1e4')
    False


    return is_float_like
    """
    try:
        value = float(item)
    except (ValueError, TypeError):
        isfloat = False
    else:
        isfloat = True

        if value != value:
            # Testing for silent == NaN.  A shame there isn't an explicit
            # built-in for this.
            isfloat = False

        elif value == _inf or value == _minf:
            # Note this is well-behaved in that float('INF') == float('INF')
            isfloat = False

        elif isinstance(item, (bytes, unicode)) and 'e' in item:
            # exclude e.g. "1e4"
            isfloat = False

    return isfloat
