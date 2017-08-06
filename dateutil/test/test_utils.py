# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta, datetime
from dateutil.utils import within_delta
import unittest

class UtilsTest(unittest.TestCase):

    def testWithinDelta(self):
        d1 = datetime(2016, 1, 1, 12, 14, 1, 9)
        d2 = d1.replace(microsecond=15)

        self.assertTrue(within_delta(d1, d2, timedelta(seconds=1)))
        self.assertFalse(within_delta(d1, d2, timedelta(microseconds=1)))

    def testWithinDeltaWithNegativeDelta(self):
        d1 = datetime(2016, 1, 1)
        d2 = datetime(2015, 12, 31)

        self.assertTrue(within_delta(d2, d1, timedelta(days=-1)))
