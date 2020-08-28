Exercises
=========

It is often useful to work through some examples in order to understand how a module works; on this page, there are several exercises of varying difficulty that you can use to learn how to use ``dateutil``.

If you are interested in helping improve the documentation of ``dateutil``, it is recommended that you attempt to complete these exercises with no resources *other than dateutil's documentation*. If you find that the documentation is not clear enough to allow you to complete these exercises, open an issue on the `dateutil issue tracker <https://github.com/dateutil/dateutil/issues>`_ to let the developers know what part of the documentation needs improvement.


.. contents:: Table of Contents
    :backlinks: top
    :local:


.. _mlk-day-exercise:

Martin Luther King Day
--------------------------------


    `Martin Luther King, Jr Day <https://en.wikipedia.org/wiki/Martin_Luther_King_Jr._Day>`_ is a US holiday that occurs every year on the third Monday in January?

    How would you generate a :doc:`recurrence rule <../rrule>` that generates Martin Luther King Day, starting from its first observance in 1986?


**Test Script**

To solve this exercise, copy-paste this script into a document, change anything between the ``--- YOUR CODE ---`` comment blocks.

.. raw:: html

    <details>

.. code-block:: python3

    # ------- YOUR CODE -------------#
    from dateutil import rrule

    MLK_DAY = <<YOUR CODE HERE>>

    # -------------------------------#

    from datetime import datetime
    MLK_TEST_CASES = [
        ((datetime(1970, 1, 1), datetime(1980, 1, 1)),
         []),
        ((datetime(1980, 1, 1), datetime(1989, 1, 1)),
         [datetime(1986, 1, 20),
          datetime(1987, 1, 19),
          datetime(1988, 1, 18)]),
        ((datetime(2017, 2, 1), datetime(2022, 2, 1)),
         [datetime(2018, 1, 15, 0, 0),
          datetime(2019, 1, 21, 0, 0),
          datetime(2020, 1, 20, 0, 0),
          datetime(2021, 1, 18, 0, 0),
          datetime(2022, 1, 17, 0, 0)]
         ),
    ]

    def test_mlk_day():
        for (between_args, expected) in MLK_TEST_CASES:
            assert MLK_DAY.between(*between_args) == expected

    if __name__ == "__main__":
        test_mlk_day()
        print('Success!')

.. raw:: html

    </details>

A solution to this problem is provided :doc:`here <solutions/mlk-day-rrule>`.


Next Monday meeting
-------------------

    A team has a meeting at 10 AM every Monday and wants a function that tells them, given a ``datetime.datetime`` object, what is the date and time of the *next* Monday meeting? This is probably best accomplished using a :doc:`relativedelta <../relativedelta>`.

**Test Script**

To solve this exercise, copy-paste this script into a document, change anything between the ``--- YOUR CODE ---`` comment blocks.

.. raw:: html

    <details>


.. code-block:: python3

    # --------- YOUR CODE -------------- #
    from dateutil import relativedelta

    def next_monday(dt):
        <<YOUR CODE HERE>>

    # ---------------------------------- #

    from datetime import datetime
    from dateutil import tz

    NEXT_MONDAY_CASES = [
        (datetime(2018, 4, 11, 14, 30, 15, 123456),
         datetime(2018, 4, 16, 10, 0)),
        (datetime(2018, 4, 16, 10, 0),
         datetime(2018, 4, 16, 10, 0)),
        (datetime(2018, 4, 16, 10, 30),
         datetime(2018, 4, 23, 10, 0)),
        (datetime(2018, 4, 14, 9, 30, tzinfo=tz.gettz('America/New_York')),
         datetime(2018, 4, 16, 10, 0, tzinfo=tz.gettz('America/New_York'))),
    ]

    def test_next_monday_1():
        for dt_in, dt_out in NEXT_MONDAY_CASES:
            assert next_monday(dt_in) == dt_out

    if __name__ == "__main__":
        test_next_monday_1()
        print('Success!')

.. raw:: html

    </details>


Parsing a local tzname
----------------------

    Three-character time zone abbreviations are *not* unique in that they do not explicitly map to a time zone. A list of time zone abbreviations in use can be found `here <https://www.timeanddate.com/time/zones/>`_. This means that parsing a datetime string such as ``'2018-01-01 12:30:30 CST'`` is ambiguous without context. Using :mod:`dateutil.parser` and :mod:`dateutil.tz`, it is possible to provide a context such that these local names are converted to proper time zones.

Problem 1
*********
    Given the context that you will only be parsing dates coming from the continental United States, India and Japan, write a function that parses a datetime string and returns a timezone-aware ``datetime`` with an IANA-style timezone attached.

    Note: For the purposes of the experiment, you may ignore the portions of the United States like Arizona and parts of Indiana that do not observe daylight saving time.

**Test Script**

To solve this exercise, copy-paste this script into a document, change anything between the ``--- YOUR CODE ---`` comment blocks.

.. raw:: html

    <details>


.. code-block:: python3

    # --------- YOUR CODE -------------- #
    from dateutil.parser import parse
    from dateutil import tz

    def parse_func_us_jp_ind():
        <<YOUR CODE HERE>>

    # ---------------------------------- #

    from dateutil import tz
    from datetime import datetime


    PARSE_TZ_TEST_DATETIMES = [
        datetime(2018, 1, 1, 12, 0),
        datetime(2018, 3, 20, 2, 0),
        datetime(2018, 5, 12, 3, 30),
        datetime(2014, 9, 1, 23)
    ]

    PARSE_TZ_TEST_ZONES = [
        tz.gettz('America/New_York'),
        tz.gettz('America/Chicago'),
        tz.gettz('America/Denver'),
        tz.gettz('America/Los_Angeles'),
        tz.gettz('Asia/Kolkata'),
        tz.gettz('Asia/Tokyo'),
    ]

    def test_parse():
        for tzi in PARSE_TZ_TEST_ZONES:
            for dt in PARSE_TZ_TEST_DATETIMES:
                dt_exp = dt.replace(tzinfo=tzi)
                dtstr = dt_exp.strftime('%Y-%m-%d %H:%M:%S %Z')

                dt_act = parse_func_us_jp_ind(dtstr)
                assert dt_act == dt_exp
                assert dt_act.tzinfo is dt_exp.tzinfo

    if __name__ == "__main__":
        test_parse()
        print('Success!')

.. raw:: html

    </details>


Problem 2
*********
    Given the context that you will *only* be passed dates from India or Ireland, write a function that correctly parses all *unambiguous* time zone strings to aware datetimes localized to the correct IANA zone, and for *ambiguous* time zone strings default to India.

**Test Script**

To solve this exercise, copy-paste this script into a document, change anything between the ``--- YOUR CODE ---`` comment blocks.


.. raw:: html

    <details>

.. code-block:: python3

    # --------- YOUR CODE -------------- #
    from dateutil.parser import parse
    from dateutil import tz

    def parse_func_ind_ire():
        <<YOUR CODE HERE>>

    # ---------------------------------- #
    ISRAEL = tz.gettz('Asia/Jerusalem')
    INDIA = tz.gettz('Asia/Kolkata')
    PARSE_IXT_TEST_CASE = [
        ('2018-02-03 12:00 IST+02:00', datetime(2018, 2, 3, 12, tzinfo=ISRAEL)),
        ('2018-06-14 12:00 IDT+03:00', datetime(2018, 6, 14, 12, tzinfo=ISRAEL)),
        ('2018-06-14 12:00 IST', datetime(2018, 6, 14, 12, tzinfo=INDIA)),
        ('2018-06-14 12:00 IST+05:30', datetime(2018, 6, 14, 12, tzinfo=INDIA)),
        ('2018-02-03 12:00 IST', datetime(2018, 2, 3, 12, tzinfo=INDIA)),
    ]


    def test_parse_ixt():
        for dtstr, dt_exp in PARSE_IXT_TEST_CASE:
            dt_act = parse_func_ind_ire(dtstr)
            assert dt_act == dt_exp, (dt_act, dt_exp)
            assert dt_act.tzinfo is dt_exp.tzinfo, (dt_act, dt_exp)

    if __name__ == "__main__":
        test_parse_ixt()
        print('Success!')

.. raw:: html

    </details>

