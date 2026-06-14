# -*- coding: utf-8 -*-
"""
This module offers a generic Easter computing method for any given year, using
Western, Orthodox or Julian algorithms.
"""

import datetime

__all__ = ["easter", "EASTER_JULIAN", "EASTER_ORTHODOX", "EASTER_WESTERN"]

EASTER_JULIAN = 1
EASTER_ORTHODOX = 2
EASTER_WESTERN = 3


def _compute_julian_easter_paschal_moon(year):
    """Compute Paschal Full Moon parameters using the Julian (old) method.

    Returns (i, j, e) where:
      i = days from March 21 to Paschal Full Moon
      j = weekday for PFM (0=Sunday)
      e = extra days for Julian→Gregorian conversion (0 for pure Julian)
    """
    golden_year = year % 19
    i = (19 * golden_year + 15) % 30
    j = (year + year // 4 + i) % 7
    return i, j, 0


def _compute_orthodox_easter_paschal_moon(year):
    """Compute Paschal Full Moon parameters using the Orthodox method.

    Same as Julian but with extra days to convert Julian date to Gregorian.
    """
    i, j, _ = _compute_julian_easter_paschal_moon(year)
    extra_days = 10
    if year > 1600:
        extra_days = extra_days + year // 100 - 16 - (year // 100 - 16) // 4
    return i, j, extra_days


def _compute_western_easter_paschal_moon(year):
    """Compute Paschal Full Moon parameters using the Western (revised) method.

    Returns (i, j, e) where e is always 0 for the Western method.
    """
    golden_year = year % 19
    century = year // 100
    h = (century - century // 4 - (8 * century + 13) // 25 + 19 * golden_year + 15) % 30
    i = h - (h // 28) * (1 - (h // 28) * (29 // (h + 1)) * ((21 - golden_year) // 11))
    j = (year + year // 4 + i + 2 - century + century // 4) % 7
    return i, j, 0


def _paschal_moon_to_easter_date(year, i, j, extra_days):
    """Convert Paschal Full Moon parameters to an Easter date.

    Args:
        year: The year to compute Easter for
        i: Days from March 21 to Paschal Full Moon
        j: Weekday for PFM (0=Sunday)
        extra_days: Extra days for Julian→Gregorian conversion

    Returns:
        datetime.date for Easter in the given year
    """
    # p can be from -6 to 56 corresponding to dates 22 March to 23 May
    p = i - j + extra_days
    day = 1 + (p + 27 + (p + 6) // 40) % 31
    month = 3 + (p + 26) // 30
    return datetime.date(int(year), int(month), int(day))


_METHOD_DISPATCH = {
    EASTER_JULIAN: _compute_julian_easter_paschal_moon,
    EASTER_ORTHODOX: _compute_orthodox_easter_paschal_moon,
    EASTER_WESTERN: _compute_western_easter_paschal_moon,
}


def easter(year, method=EASTER_WESTERN):
    """
    This method was ported from the work done by GM Arts,
    on top of the algorithm by Claus Tondering, which was
    based in part on the algorithm of Ouding (1940), as
    quoted in "Explanatory Supplement to the Astronomical
    Almanac", P.  Kenneth Seidelmann, editor.

    This algorithm implements three different Easter
    calculation methods:

    1. Original calculation in Julian calendar, valid in
       dates after 326 AD
    2. Original method, with date converted to Gregorian
       calendar, valid in years 1583 to 4099
    3. Revised method, in Gregorian calendar, valid in
       years 1583 to 4099 as well

    These methods are represented by the constants:

    * ``EASTER_JULIAN   = 1``
    * ``EASTER_ORTHODOX = 2``
    * ``EASTER_WESTERN  = 3``

    The default method is method 3.

    More about the algorithm may be found at:

    `GM Arts: Easter Algorithms <http://www.gmarts.org/index.php?go=415>`_

    and

    `The Calendar FAQ: Easter <https://www.tondering.dk/claus/cal/easter.php>`_

    """
    if method not in _METHOD_DISPATCH:
        raise ValueError("invalid method")

    i, j, extra_days = _METHOD_DISPATCH[method](year)
    return _paschal_moon_to_easter_date(year, i, j, extra_days)
