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


def _compute_julian_pfm_offset(year):
    """Compute Paschal Full Moon offset for Julian calendar method.

    Uses the original calculation valid for dates after 326 AD.

    Args:
        year: The year to compute for.

    Returns:
        Tuple of (i, j) where:
        - i: Number of days from March 21 to Paschal Full Moon
        - j: Weekday for PFM (0=Sunday, etc)
    """
    g = year % 19
    i = (19 * g + 15) % 30
    j = (year + year // 4 + i) % 7
    return i, j


def _compute_gregorian_correction(year):
    """Compute the Julian-to-Gregorian date correction for Orthodox Easter.

    Orthodox Easter uses the Julian calendar date, then converts to the
    Gregorian calendar by adding extra days.

    Args:
        year: The year to compute for.

    Returns:
        Integer number of extra days to add.
    """
    e = 10
    if year > 1600:
        e = e + year // 100 - 16 - (year // 100 - 16) // 4
    return e


def _compute_western_pfm_offset(year):
    """Compute Paschal Full Moon offset for Western (revised) method.

    Uses the revised method in Gregorian calendar, valid for years 1583-4099.

    Args:
        year: The year to compute for.

    Returns:
        Tuple of (i, j) where:
        - i: Number of days from March 21 to Paschal Full Moon
        - j: Weekday for PFM (0=Sunday, etc)
    """
    g = year % 19
    c = year // 100
    h = (c - c // 4 - (8 * c + 13) // 25 + 19 * g + 15) % 30
    i = h - (h // 28) * (1 - (h // 28) * (29 // (h + 1)) * ((21 - g) // 11))
    j = (year + year // 4 + i + 2 - c + c // 4) % 7
    return i, j


def _pfm_offset_to_date(year, pfm_days, weekday_offset, gregorian_correction=0):
    """Convert Paschal Full Moon offset to an Easter date.

    Args:
        year: The year.
        pfm_days: Number of days from March 21 to Paschal Full Moon (i).
        weekday_offset: Weekday for PFM (j).
        gregorian_correction: Extra days for Julian-to-Gregorian conversion.

    Returns:
        datetime.date for Easter Sunday.
    """
    p = pfm_days - weekday_offset + gregorian_correction
    d = 1 + (p + 27 + (p + 6) // 40) % 31
    m = 3 + (p + 26) // 30
    return datetime.date(int(year), int(m), int(d))


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

    if not (1 <= method <= 3):
        raise ValueError("invalid method")

    if method < 3:
        # Old method (Julian or Orthodox)
        i, j = _compute_julian_pfm_offset(year)
        gregorian_correction = _compute_gregorian_correction(year) if method == 2 else 0
    else:
        # New method (Western/Revised)
        i, j = _compute_western_pfm_offset(year)
        gregorian_correction = 0

    return _pfm_offset_to_date(year, i, j, gregorian_correction)
