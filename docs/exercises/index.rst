Exercises
=========

It is often useful to work through some examples in order to understand how a module works; on this page, there are several exercises of varying difficulty that you can use to learn how to use ``dateutil``.

If you are interested in helping improve the documentation of ``dateutil``, it is recommended that you attempt to complete these exercises with no resources *other than dateutil's documentation*. If you find that the documentation is not clear enough to allow you to complete these exercises, open an issue on the `dateutil issue tracker <https://github.com/dateutil/dateutil/issues>`_ to let the developers know what part of the documentation needs improvement.


.. contents:: Table of Contents
    :backlinks: top
    :local:


Martin Luther King Day
--------------------------------


    `Martin Luther King, Jr Day <https://en.wikipedia.org/wiki/Martin_Luther_King_Jr._Day>`_ is a US holiday that occurs every year on the third Monday in January?

    How would you generate a `recurrence rule <../rrule.html>`_ that generates Martin Luther King Day, starting from its first observance in 1986?


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


