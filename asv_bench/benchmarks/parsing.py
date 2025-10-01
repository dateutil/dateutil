# -*- coding: utf-8 -*-

from dateutil.parser._parser import parse, parser, _timelex

iterations = 10 ** 5
# Note: `iterations` is _not_ a keyword internal to asv config


class Parsing(object):

    def time_parse_iso(self):
        for n in range(iterations):
            parse('2017-12-08')

    def time_parse_iso_ymd_hms(self):
        for n in range(iterations):
            parse('2017-12-08 20:38:15')

    def time_parse_YBD(self):
        for n in range(iterations):
            parse('2014 January 19')

    def time_parse_date_format(self):
        for n in range(iterations):
            parse('Thu, 25 Sep 2003 10:49:41 -0300')

    def time_parse_no_separator(self):
        for n in range(iterations):
            parse('19970902090807')


class Fuzzy(object):
    def time_parse_fuzzy(self):
        for n in range(iterations):
            parse("Today is 25 of September of 2003, exactly "
                  "at 10:49:41 with timezone -03:00.", fuzzy=True)

    def time_parse_fuzzy_long(self):
        for n in range(iterations):
            parse("2012 MARTIN CHILDREN'S IRREVOCABLE TRUST "
                  "u/a/d NOVEMBER 7, 2012",
                  fuzzy=True)
