# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ._common import unittest

from datetime import datetime, timedelta

# dateutil imports
from dateutil.absolutedelta import absolutedelta
from dateutil import tz

from nose_parameterized import parameterized

NYC = tz.gettz('America/New_York')
CHI = tz.gettz('America/Chicago')

class AbsoluteDeltaTest(unittest.TestCase):
    @parameterized.expand([
        ('naive',
            datetime(2012, 1, 2, 13),
            datetime(2012, 1, 2, 12),
            absolutedelta(hours=1)),
        ('aware_same',
            datetime(2014, 1, 2, 15, tzinfo=NYC),
            datetime(2014, 1, 2, 12, tzinfo=NYC),
            absolutedelta(hours=3)),
        ('aware_different',
            datetime(2011, 1, 3, 17, tzinfo=CHI),   # 23:00 UTC
            datetime(2011, 1, 3, 14, tzinfo=NYC),   # 19:00 UTC
            absolutedelta(hours=4)),
        ('aware_dst_start',
            datetime(2004, 4, 4, 3, 30, tzinfo=NYC),    # DST, 07:30 UTC
            datetime(2004, 4, 4, 1, 30, tzinfo=NYC),    # EST, 06:30 UTC
            absolutedelta(hours=1)),
        ('aware_dst_end',
            datetime(2004, 10, 31, 0, 30, tzinfo=NYC),  # EST
            datetime(2004, 10, 31, 3, 30, tzinfo=NYC),  # DST,
            absolutedelta(hours=-4))
    ])
    def test_sub(self, name, dt1, dt2, ad_e):
        ad_a = absolutedelta.sub(dt1, dt2)

        # Assert that it's constructed correctly
        self.assertIsInstance(ad_a, absolutedelta)
        self.assertEqual(ad_a, ad_e)

        # Now check that the reverse works
        ad_r = absolutedelta.sub(dt2, dt1)

        self.assertIsInstance(ad_r, absolutedelta)
        self.assertEqual(ad_r, -ad_e)

    def test_sub_mixed_naivete(self):
        NYC = tz.gettz('America/New_York')

        dt1 = datetime(2012, 1, 3, 15, tzinfo=NYC)
        dt2 = datetime(2012, 1, 3, 15)

        with self.assertRaises(ValueError):
            absolutedelta.sub(dt2, dt1)

    def test_from_timedelta(self):
        td = timedelta(weeks=1, days=2, hours=4)

        ad_a = absolutedelta.from_timedelta(td)
        ad_e = absolutedelta(weeks=1, days=2, hours=4)

        self.assertEqual(ad_a, ad_e)
        self.assertIsInstance(ad_a, absolutedelta)

    @parameterized.expand([
        ('naive',
            datetime(2002, 9, 12, 17, 15, 15),
            datetime(2003, 7, 14, 12,  8),
            absolutedelta(days=304, hours=18, minutes=52, seconds=45)),
        ('aware',
            datetime(1972, 3, 4, 21, 0, tzinfo=CHI),
            datetime(1972, 3, 5, 22, 5, tzinfo=CHI),
            absolutedelta(days=1, hours=1, minutes=5)),
        ('aware_dst_start',
            datetime(2007, 3, 11, 1, 30, tzinfo=NYC),
            datetime(2007, 3, 11, 3, 15, tzinfo=NYC),
            absolutedelta(minutes=45)),
        ('aware_dst_end',
            datetime(2007, 11, 4,  0, 30, tzinfo=NYC),
            datetime(2007, 11, 4,  3, 30, tzinfo=NYC),
            absolutedelta(hours=4))
    ])
    def test_addition(self, name, dt_in, dt_exp, ad):
        # Test __add__
        self.assertEqual(ad + dt_in, dt_exp)

        # Test __radd__
        self.assertEqual(dt_in + ad, dt_exp)

        # Test __sub__
        self.assertEqual(dt_exp - ad, dt_in)

    @parameterized.expand([
        ('ad_ad_0',
            absolutedelta(days=3, minutes=4),
            absolutedelta(days=3, minutes=-4),
            absolutedelta(days=6)),
        ('ad_ad_1',
            absolutedelta(days=7, hours=1),
            absolutedelta(days=-7, hours=-1),
            absolutedelta(0)),
        ('ad_ad_2',
            absolutedelta(weeks=1, microseconds=4),
            absolutedelta(days=-2, seconds=15, microseconds=2),
            absolutedelta(days=5, seconds=15, microseconds=6)),
        ('ad_td',
            absolutedelta(hours=9),
            timedelta(hours=3),
            absolutedelta(hours=12))
        ])
    def test_add_deltas(self, name, d1, d2, d_out):
        d_act = d1 + d2
        self.assertEqual(d_act, d_out)

        self.assertIsInstance(d_act, type(d_out))

    @parameterized.expand([
        ('ad_ad_0',
            absolutedelta(days=3, minutes=4),
            absolutedelta(days=3, minutes=-4),
            absolutedelta(minutes=8)),
        ('ad_ad_1',
            absolutedelta(days=7, hours=1),
            absolutedelta(days=-7, hours=-1),
            absolutedelta(weeks=2, hours=2)),
        ('ad_ad_2',
            absolutedelta(weeks=1, microseconds=4),
            absolutedelta(days=-2, seconds=15, microseconds=2),
            absolutedelta(days=9, seconds=-15, microseconds=2)),
        ('ad_td',
            absolutedelta(hours=9),
            timedelta(hours=3),
            absolutedelta(hours=6))
        ])
    def test_sub_deltas(self, name, d1, d2, d_out):
        # Test __sub__
        d_act = d1 - d2

        self.assertEqual(d_act, d_out)
        self.assertIsInstance(d_act, type(d_out))

        # Test __rsub__
        d_act_r = -(d2 - d1)

        self.assertEqual(d_act_r, d_out)
        self.assertIsInstance(d_act_r, type(d_out))

    @parameterized.expand([
        ('p00',
            absolutedelta(days=4),
            absolutedelta(days=4)),
        ('0p0',
            absolutedelta(seconds=7),
            absolutedelta(seconds=7)),
        ('00p',
            absolutedelta(microseconds=18),
            absolutedelta(microseconds=18)),
        ('n00',
            absolutedelta(days=-21),
            absolutedelta(days=21)),
        ('0n0',
            absolutedelta(seconds=-14),
            absolutedelta(seconds=14)),
        ('00n',
            absolutedelta(microseconds=-17449),
            absolutedelta(microseconds=17449)),
        ('pn0_p',
            absolutedelta(days=1, seconds=-22),
            absolutedelta(days=1, seconds=-22)),
        ('np0_n',
            absolutedelta(days=-1, seconds=3600),
            absolutedelta(hours=23)),
        ('nnn_n',
            absolutedelta(days=-4, seconds=-3600, microseconds=-24),
            absolutedelta(days=4, seconds=3600, microseconds=24))
    ])
    def test_abs(self, name, ad_in, ad_out):
        ad_a = abs(ad_in)

        self.assertEqual(ad_a, ad_out)
        self.assertIsInstance(ad_a, type(ad_out))

    def test_pos(self):
        ad = absolutedelta(hours=7)

        self.assertIs(ad, +ad)

    @parameterized.expand([
        ('ints_p00',
            absolutedelta(days=1),
            'absolutedelta(1)'),
        ('ints_n00',
            absolutedelta(days=-1),
            'absolutedelta(-1)'),
        ('ints_0p0',
            absolutedelta(seconds=20),
            'absolutedelta(0, 20)'),
        ('ints_0n0',
            absolutedelta(seconds=-15),
            'absolutedelta(-1, 86385)'),
        ('ints_00p',
            absolutedelta(microseconds=5),
            'absolutedelta(0, 0, 5)'),
        ('ints_00n',
            absolutedelta(microseconds=-5),
            'absolutedelta(-1, 86399, 999995)'),
        ('ints_p0n',
            absolutedelta(days=2, microseconds=-1427),
            'absolutedelta(1, 86399, 998573)'),
        ('ints_np0',
            absolutedelta(days=-2, seconds=1800),
            'absolutedelta(-2, 1800)'),
        ('floats',
            absolutedelta(days=2.25, seconds=-3600.1),
            'absolutedelta(2, 17999, 900000)')
    ])
    def test_repr(self, name, ad, ad_repr):
        self.assertEqual(repr(ad), ad_repr)

    @parameterized.expand([
        ('int_pos',
            absolutedelta(days=1),
            3,
            absolutedelta(days=3)),
        ('int_neg',
            absolutedelta(days=1),
            -4,
            absolutedelta(days=-4)),
        ('int_zero',
            absolutedelta(days=1),
            0,
            absolutedelta(0)),
        ('float_pos',
            absolutedelta(days=1),
            1.5,
            absolutedelta(days=1, hours=12)),
        ('float_neg',
            absolutedelta(days=1),
            -2.25,
            absolutedelta(days=-2, hours=-6)),
        ('float_zero',
            absolutedelta(days=1),
            0.0,
            absolutedelta(0))
    ])
    def test_mul(self, name, ad_in, fac, ad_out):
        # Test __mul__
        ad_a = ad_in * fac

        self.assertEqual(ad_a, ad_out)
        self.assertIsInstance(ad_a, type(ad_out))

        # Test __rmul__
        ad_ar = fac * ad_in

        self.assertEqual(ad_ar, ad_out)
        self.assertIsInstance(ad_ar, type(ad_out))

    @parameterized.expand([
        ('int_even',
            absolutedelta(4),
            2,
            absolutedelta(2)),
        ('int_not_divisible',
            absolutedelta(microseconds=17),
            3,
            absolutedelta(microseconds=6)),
        ('absolutedelta_int',
            absolutedelta(days=4, hours=18),
            absolutedelta(hours=2),
            57.0),
        ('absolutedelta_float',
            absolutedelta(days=4, hours=17),
            absolutedelta(hours=2),
            56.5),
        ('timedelta_int',
            absolutedelta(days=4, hours=18),
            timedelta(hours=2),
            57.0),
        ('timedelta_float',
            absolutedelta(days=4, hours=17),
            timedelta(hours=2),
            56.5),
    ])
    def test_div(self, name, ad_in, fac, ad_out):
        ad_a = ad_in / fac

        self.assertEqual(ad_a, ad_out)
        self.assertIsInstance(ad_a, type(ad_out))

    @parameterized.expand([
        ('int',
            absolutedelta(microseconds=17),
            3,
            absolutedelta(microseconds=5)),
        ('absolutedelta',
            absolutedelta(microseconds=42),
            absolutedelta(microseconds=15),
            2),
        ('absolutedelta',
            absolutedelta(microseconds=42),
            timedelta(microseconds=15),
            2)
    ])
    def test_floor_div(self, name, ad_in, fac, ad_out):
        ad_a = ad_in // fac

        self.assertEqual(ad_a, ad_out)
        self.assertIsInstance(ad_a, type(ad_out))

