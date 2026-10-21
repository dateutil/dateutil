# -*- coding: utf-8 -*-
"""
Optimisations to the parser must not change behaviour. These tests compare
the parser against ``_reference_parser``, a frozen copy of the upstream
implementation, on generated inputs.
"""
from __future__ import unicode_literals

import warnings
from datetime import datetime
from io import StringIO

from hypothesis import given, settings, strategies as st

from dateutil import tz
from dateutil.parser import _parser

from . import _reference_parser as _reference


# -- tokenizer ---------------------------------------------------------------

# Characters the tokenizer's state machine branches on, plus Unicode
# characters where str.isalpha / str.isdigit disagree with regex classes.
_lex_alphabet = st.sampled_from(
    list("0123456789") * 3 + list("abcxyzTZ") * 2 +
    list(".,:;-/+ \t\n") * 2 +
    ["\x00", "é", "ß", "²", "½", "٣", "_", "'", " "])

_lex_inputs = st.text(_lex_alphabet, max_size=40)


@given(_lex_inputs)
@settings(max_examples=5000, deadline=None)
def test_tokenizer_matches_reference(s):
    assert _parser._timelex.split(s) == _reference._timelex.split(s)


@given(_lex_inputs)
@settings(max_examples=500, deadline=None)
def test_tokenizer_matches_reference_for_bytes_and_streams(s):
    expected = _reference._timelex.split(s)
    assert _parser._timelex.split(s.encode("utf-8")) == expected
    assert _parser._timelex.split(StringIO(s)) == expected


# -- parse() -----------------------------------------------------------------

_number = st.one_of(
    st.integers(0, 3000).map(str),
    st.integers(0, 99).map(lambda n: "%02d" % n),
    st.sampled_from(["21.447", "4,5", "1.5", "20180101", "143000", "1e3"]),
)
_word = st.sampled_from([
    "Jan", "March", "sept", "Sep.", "December", "Mon", "Friday", "thu",
    "AM", "pm", "a.m.", "h", "m", "s", "at", "of", "on", "the", "and",
    "st", "nd", "rd", "th", "UTC", "GMT", "EST", "Z", "BRST", "T",
    "+0300", "-03:00", "+05", "today", "Meeting",
])
_sep = st.sampled_from([" ", "-", "/", ".", ",", ":", "", ", ", "T"])

_parse_inputs = st.lists(
    st.tuples(st.one_of(_number, _number, _word), _sep).map("".join),
    min_size=1, max_size=8,
).map("".join)

# Real-world formats, so that successful parses are well represented.
_FORMATS = [
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y%m%dT%H%M%S", "%Y%m%d",
    "%m/%d/%Y", "%d/%m/%y", "%d.%m.%Y %H:%M", "%m-%d-%Y %I:%M %p",
    "%a, %d %b %Y %H:%M:%S", "%A %B %d, %Y", "%b %d %Y %I:%M%p",
    "%d %B %Y", "%B %d", "%H:%M", "%I:%M:%S %p", "%Y-%m", "%d-%b-%Y",
    "%d/%b/%Y:%H:%M:%S", "%a %b %d %H:%M:%S %Y", "%Y.%m.%d", "%y%m%d",
]
_formatted = st.tuples(
    st.datetimes(min_value=datetime(1000, 1, 1),
                 max_value=datetime(9999, 12, 31)),
    st.sampled_from(_FORMATS),
    st.sampled_from(["", " UTC", " EST", " BRST", "Z", " +0300", "-03:00",
                     " GMT+3", " (PST)"]),
).map(lambda t: t[0].strftime(t[1]) + t[2])

_INFO = {
    None: (None, None),
    "dayfirst": (_parser.parserinfo(dayfirst=True),
                 _reference.parserinfo(dayfirst=True)),
}

_kwargs = st.fixed_dictionaries({}, optional={
    "dayfirst": st.sampled_from([None, True, False]),
    "yearfirst": st.sampled_from([None, True, False]),
    "ignoretz": st.booleans(),
    "fuzzy": st.booleans(),
    "fuzzy_with_tokens": st.booleans(),
    "default": st.datetimes(min_value=datetime(1, 1, 1),
                            max_value=datetime(9999, 1, 1)),
    "tzinfos": st.just({"UTC": tz.gettz("Europe/London"), "EST": -18000,
                        "BRST": tz.tzoffset("BRST", -7200)}),
    "parserinfo": st.sampled_from(sorted(_INFO, key=str)),
})


def _outcome(module, timestr, kwargs):
    kwargs = dict(kwargs)
    if "parserinfo" in kwargs:
        kwargs["parserinfo"] = _INFO[kwargs["parserinfo"]][module is _reference]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            result = module.parse(timestr, **kwargs)
            dt, tokens = result if isinstance(result, tuple) else (result, None)
            return ("ok", repr(dt), dt.utcoffset(), tokens)
        except Exception as e:
            # The two modules define distinct (but identical) ParserErrors.
            return ("raises", type(e).__name__, str(e))


@given(timestr=st.one_of(_formatted, _parse_inputs, _lex_inputs),
       kwargs=_kwargs)
@settings(max_examples=5000, deadline=None)
def test_parse_matches_reference(timestr, kwargs):
    assert (_outcome(_parser, timestr, kwargs) ==
            _outcome(_reference, timestr, kwargs))
