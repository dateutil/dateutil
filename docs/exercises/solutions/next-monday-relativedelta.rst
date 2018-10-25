
Next Monday meeting: Solution
================================

Presented here is a solution to the :ref:`Martin Luther King Day exercises`.


.. code-block:: python3

    # ------- YOUR CODE -------------#
	from dateutil import relativedelta
	import datetime
	from datetime import datetime
	from dateutil import tz

	def next_monday(now):
		next_meet = now + relativedelta.relativedelta(weekday = 0, hour = 10, minute = 0, second = 0, microsecond = 0) 
		if next_meet < now:
			next_meet = next_meet + relativedelta.relativedelta(weeks = 1)
		return next_meet
    # -------------------------------#

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
