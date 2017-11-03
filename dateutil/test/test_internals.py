# -*- coding: utf-8 -*-
"""
Tests for implementation details, not necessarily part of the user-facing
API.

The motivating case for these tests is #483, where we want to smoke-test
code that may be difficult to reach through the standard API calls.
"""

from dateutil.parser import _ymd


class TestYMD(unittest.TestCase):

	# @pytest.mark.smoke
	def test_could_be_day(self):
		ymd = _ymd('foo bar 124 baz')

		ymd.append(2, 'M')
		assert ymd.has_month
		assert not ymd.has_year
		assert ymd.could_be_day(4)
		assert not ymd.could_be_day(-6)
		assert not ymd.could_be_day(32)

		# Assumes leapyear
		assert ymd.could_be_day(29)

		ymd.append(1999)
		assert ymd.has_year
		assert not ymd.could_be_day(29)

		ymd.append(16, 'D')
		assert ymd.has_day
		assert not ymd.could_be_day(1)

		ymd = _ymd('foo bar 124 baz')
		ymd.append(1999)
		assert ymd.could_be_day(31)
