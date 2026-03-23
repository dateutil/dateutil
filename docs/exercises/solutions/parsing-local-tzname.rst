:orphan:

Parsing a local tzname — Solution
==================================

This is a solution to the :ref:`parsing-local-tzname-exercise`.

Problem 1 — US, India and Japan
---------------------------------

The trick is to pass a ``tzinfos`` dictionary to :func:`dateutil.parser.parse` that maps
each timezone abbreviation to the correct IANA timezone object:

.. code-block:: python3

    from dateutil.parser import parse
    from dateutil import tz

    US_JP_IND_TZINFOS = {
        # US timezones (standard and daylight)
        'EST': tz.gettz('America/New_York'),
        'EDT': tz.gettz('America/New_York'),
        'CST': tz.gettz('America/Chicago'),
        'CDT': tz.gettz('America/Chicago'),
        'MST': tz.gettz('America/Denver'),
        'MDT': tz.gettz('America/Denver'),
        'PST': tz.gettz('America/Los_Angeles'),
        'PDT': tz.gettz('America/Los_Angeles'),
        # India
        'IST': tz.gettz('Asia/Kolkata'),
        # Japan
        'JST': tz.gettz('Asia/Tokyo'),
    }

    def parse_func_us_jp_ind(dtstr):
        return parse(dtstr, tzinfos=US_JP_IND_TZINFOS)

Problem 2 — India and Israel
------------------------------

``IST`` is ambiguous between India Standard Time and Israel Standard Time (``IDT`` is
Israel Daylight Time). We default to India for ambiguous strings:

.. code-block:: python3

    from dateutil.parser import parse
    from dateutil import tz

    IND_ISR_TZINFOS = {
        'IST': tz.gettz('Asia/Kolkata'),   # ambiguous → default to India
        'IDT': tz.gettz('Asia/Jerusalem'),  # unambiguous Israel Daylight Time
    }

    def parse_func_ind_isr(dtstr):
        return parse(dtstr, tzinfos=IND_ISR_TZINFOS)
