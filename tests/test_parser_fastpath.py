# -*- coding: utf-8 -*-
"""
The ISO-8601 fast path in ``parser._parse`` must be a pure optimisation:
for every input and every option, ``parse()`` must behave exactly as it does
with the fast path disabled (i.e. the original tokenizing parser).
"""
from __future__ import unicode_literals

import warnings
from datetime import datetime

import pytest
from hypothesis import given, settings, strategies as st

from dateutil import tz
from dateutil.parser import _parser
from dateutil.parser import parse, parser, parserinfo

try:
    from unittest import mock
except ImportError:  # pragma: no cover
    import mock


def _outcome(timestr, kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            result = parse(timestr, **kwargs)
            dt, tokens = result if isinstance(result, tuple) else (result, None)
            # The general path can build tzoffsets that datetime rejects
            # (e.g. "+24:00"), so utcoffset() may raise too.
            return ("ok", repr(dt), dt.utcoffset(), tokens)
        except Exception as e:
            return ("raises", type(e), str(e))


def _slow_outcome(timestr, kwargs):
    with mock.patch.object(parser, "_try_parse_iso", lambda self, s: None):
        return _outcome(timestr, kwargs)


def _num(lo, hi, width):
    return st.integers(lo, hi).map(lambda n: str(n).zfill(width))


_frac = st.tuples(st.sampled_from([".", ","]),
                  st.text("0123456789", min_size=1, max_size=9)).map("".join)

_time = st.tuples(
    st.sampled_from(["T", " ", "t", ""]),
    _num(0, 25, 2), st.sampled_from([":", ""]), _num(0, 60, 2),
    st.one_of(st.just(""),
              st.tuples(st.just(":"), _num(0, 61, 2),
                        st.one_of(st.just(""), _frac)).map("".join)),
).map("".join)

_tz = st.one_of(
    st.sampled_from(["", "Z", "z", " UTC", "UTC", " EST", "+00:00", "-00:00"]),
    st.tuples(st.sampled_from(["+", "-"]), _num(0, 25, 2),
              st.sampled_from([":", ""]),
              st.one_of(st.just(""), _num(0, 61, 2))).map("".join),
)

_iso_like = st.tuples(
    st.sampled_from(["", " "]),
    st.one_of(_num(0, 9999, 4), _num(0, 99, 2), _num(10000, 99999, 5)),
    st.sampled_from(["-", "/", ".", ""]),
    st.one_of(_num(0, 13, 2), _num(1, 9, 1)),
    st.sampled_from(["-", "/", ".", ""]),
    st.one_of(_num(0, 32, 2), _num(1, 9, 1)),
    st.one_of(st.just(""), _time),
    _tz,
    st.sampled_from(["", " ", "\n"]),
).map("".join)

# Exactly the fast path's grammar, with values straddling every range check.
_strict_time = st.tuples(
    st.sampled_from(["T", " "]), _num(0, 25, 2), st.just(":"), _num(0, 60, 2),
    st.one_of(st.just(""), st.tuples(
        st.just(":"), _num(0, 61, 2),
        st.one_of(st.just(""), st.text("0123456789", min_size=1, max_size=7)
                  .map(lambda f: "." + f))).map("".join)),
    st.one_of(st.sampled_from(["", "Z"]), st.tuples(
        st.sampled_from(["+", "-"]), _num(0, 25, 2),
        st.sampled_from(["", ":"]),
        st.one_of(st.just(""), _num(0, 61, 2))).map("".join)),
).map("".join)

_strict_iso = st.tuples(
    _num(0, 9999, 4), st.just("-"), _num(0, 13, 2), st.just("-"),
    _num(0, 32, 2), st.one_of(st.just(""), _strict_time),
).map("".join)

_inputs = st.one_of(
    _strict_iso,
    _iso_like,
    # non-ASCII digits and other junk around otherwise-valid shapes
    _iso_like.map(lambda s: s.replace("1", "١")),
    st.text("0123456789-:T.+Z ", max_size=30),
)

class _NoJumpInfo(parserinfo):
    # Without "T" and " " as jump tokens, the general path rejects ISO
    # datetimes; the fast path must not accept them for such subclasses.
    JUMP = []


_kwargs = st.fixed_dictionaries({}, optional={
    "dayfirst": st.sampled_from([None, True, False]),
    "yearfirst": st.sampled_from([None, True, False]),
    "ignoretz": st.booleans(),
    "fuzzy": st.booleans(),
    "fuzzy_with_tokens": st.booleans(),
    "default": st.datetimes(min_value=datetime(1, 1, 1),
                            max_value=datetime(9999, 1, 1)),
    "tzinfos": st.just({"UTC": tz.gettz("Europe/London"), "EST": -18000}),
    "parserinfo": st.sampled_from([parserinfo(dayfirst=True), _NoJumpInfo()]),
})


@given(timestr=_inputs, kwargs=_kwargs)
@settings(max_examples=3000, deadline=None)
def test_fast_path_matches_slow_path(timestr, kwargs):
    assert _outcome(timestr, kwargs) == _slow_outcome(timestr, kwargs)


@pytest.mark.parametrize("timestr", [
    "2024-03-15",
    "2024-03-15T14:30",
    "2024-03-15 14:30:00",
    "2024-03-15T14:30:00.123456",
    "2024-03-15T14:30:00Z",
    "2024-03-15T14:30:00+02:00",
    "2024-03-15T14:30:00-0530",
    "2024-03-15T14:30:00+05",
])
def test_common_iso_inputs_skip_the_tokenizer(timestr):
    def tokenizer_called(*args, **kwargs):
        raise AssertionError("tokenizer used for %r" % timestr)

    with mock.patch.object(_parser._timelex, "split", tokenizer_called):
        parse(timestr)
