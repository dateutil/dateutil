#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools

from datetime import datetime

from six import assertRaisesRegex, PY3
from six.moves import StringIO

from dateutil.tz import tzoffset
from dateutil.parser import parse, parserinfo

import pytest

tzinfos = {"BRST": -10800}
brsttz = tzoffset("BRST", -10800)
default = datetime(2003, 9, 25)


# If we have a 4-digit year, a non-numeric month (abbreviated or not),
# and a day (1 or 2 digits), then there is no ambiguity as to which
# token is a year/month/day.  This holds regardless of what order the
# terms are in and for each of the separators below.
seps = ['-', ' ', '/', '.']
token_opts = [['%Y'], ['%b', '%B'], ['%d', '%-d']]

prods = itertools.product(*token_opts)
perms = [y for x in prods for y in itertools.permutations(x)]
unambig_fmts = [sep.join(perm) for sep in seps for perm in perms]

@pytest.mark.parametrize("fmt", unambig_fmts)
@pytest.mark.parametrize("year", [2003])
@pytest.mark.parametrize("month", [9])
@pytest.mark.parametrize("day", [25])
def test_iso(fmt, year, month, day):
	try:
		actual = datetime(year, month, day)
	except ValueError:
		# e.g. Feb 30
		return

	dstr = actual.strftime(fmt)
	res = parse(dstr, default=default)
	assert res == actual



