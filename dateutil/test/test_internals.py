# -*- coding: utf-8 -*-
"""
Tests for implementation details, not necessarily part of the user-facing
API.

The motivating case for these tests is #483, where we want to smoke-test
code that may be difficult to reach through the standard API calls.
"""

import unittest
import sys

import pytest

from dateutil.parser._parser import _ymd, parser
import dateutil.tz

IS_PY32 = sys.version_info[0:2] == (3, 2)


class TestParserPrivate(object):
    def test_single_character_tzname(self):
        # See GH#540
        dstr = '5:50 A.M. on June 13, 1990'
        res = parser()._parse(dstr)[0]
        assert res.tzname is None

        dstr = 'Jan 29, 1945 14:45 AM I going to see you there?'
        res = parser()._parse(dstr, fuzzy=True)[0]
        assert res.tzname is None

    def test_alpha_tzname(self):
        # See GH#540
        dstr = '2017-12-07 10:27:15B'
        tzinfos = {'B': dateutil.tz.tzoffset('Beta', 120)}
        res = parser().parse(dstr, tzinfos=tzinfos)
        assert res.tzinfo is tzinfos['B']

    @pytest.mark.xfail
    def test_alpha_tzname_ampm(self):
        # If the Alpha-style timezone is "A" it gets incorrectly
        # identified as part of AM/PM
        dstr = '2017-12-07 10:27:15A'
        tzinfos = {'A': dateutil.tz.tzoffset('Alpha', 60)}
        res = parser().parse(dstr, tzinfos=tzinfos)
        assert res.tzinfo is tzinfos['A']


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


###
# Test that private interfaces in _parser are deprecated properly
@pytest.mark.skipif(IS_PY32, reason='pytest.warns not supported on Python 3.2')
def test_parser_private_warns():
    from dateutil.parser import _timelex, _tzparser
    from dateutil.parser import _parsetz

    with pytest.warns(DeprecationWarning):
        _tzparser()

    with pytest.warns(DeprecationWarning):
        _timelex('2014-03-03')

    with pytest.warns(DeprecationWarning):
        _parsetz('+05:00')


@pytest.mark.skipif(IS_PY32, reason='pytest.warns not supported on Python 3.2')
def test_parser_parser_private_not_warns():
    from dateutil.parser._parser import _timelex, _tzparser
    from dateutil.parser._parser import _parsetz

    with pytest.warns(None) as recorder:
        _tzparser()
        assert len(recorder) == 0

    with pytest.warns(None) as recorder:
        _timelex('2014-03-03')

        assert len(recorder) == 0

    with pytest.warns(None) as recorder:
        _parsetz('+05:00')
        assert len(recorder) == 0
