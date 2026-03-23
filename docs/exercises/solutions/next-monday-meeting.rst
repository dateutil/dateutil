Next Monday Meeting — Solution
==============================

This is a solution to the :ref:`Next Monday meeting exercise <next-monday-exercise>`.

The key insight is to use :class:`dateutil.relativedelta.relativedelta` with ``weekday=MO(+1)``
to advance to the next Monday, and replace the time components at the same time. However, if
the input is already exactly Monday at 10:00, it should return that same datetime (not the
following week).

.. code-block:: python3

    from datetime import datetime
    from dateutil.relativedelta import relativedelta, MO
    from dateutil import tz

    def next_monday(dt):
        # Replace time to 10:00 and move to next Monday (or stay if already Monday at 10:00)
        candidate = dt + relativedelta(weekday=MO, hour=10, minute=0, second=0, microsecond=0)
        # If the candidate is in the past relative to dt (same Monday but already past 10:00),
        # advance by one week
        if candidate < dt:
            candidate += relativedelta(weeks=1)
        return candidate

**Walkthrough**

``relativedelta(weekday=MO, hour=10, minute=0, second=0, microsecond=0)`` does two things at once:

1. Advances (or stays) to the nearest Monday using ``weekday=MO``.
2. Sets the time to 10:00:00 by replacing ``hour``, ``minute``, ``second``, and ``microsecond``.

If the result is still *before* ``dt`` — which happens when ``dt`` is a Monday after 10:00 AM —
we add one more week to get the *next* Monday.
