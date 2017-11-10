# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta, date, time
import itertools as it

from dateutil.tz import tz
from dateutil.parser import Isoparser, isoparse

import pytest
import six

UTC = tz.tzutc()

def _generate_tzoffsets(limited):
    def _mkoffset(hmtuple, fmt):
        h, m = hmtuple
        m_td = (-1 if h < 0 else 1) * m

        tzo = tz.tzoffset(None, timedelta(hours=h, minutes=m_td))
        return tzo, fmt.format(h, m)

    out = []
    if not limited:
        # The subset that's just hours
        hm_out_h = [(h, 0) for h in (-23, -5, 0, 5, 23)]
        out.extend([_mkoffset(hm, '{:+03d}') for hm in hm_out_h])

        # Ones that have hours and minutes
        hm_out = [] + hm_out_h
        hm_out += [(-12, 15), (11, 30), (10, 2), (5, 15), (-5, 30)]
    else:
        hm_out = [(-5, -0)]

    fmts = ['{:+03d}:{:02d}', '{:+03d}{:02d}']
    out += [_mkoffset(hm, fmt) for hm in hm_out for fmt in fmts]

    # Also add in UTC and naive
    out.append((tz.tzutc(), 'Z'))
    out.append((None, ''))

    return out

FULL_TZOFFSETS = _generate_tzoffsets(False)
FULL_TZOFFSETS_AWARE = [x for x in FULL_TZOFFSETS if x[1]]
TZOFFSETS = _generate_tzoffsets(True)

DATES = [datetime(1996, 1, 1), datetime(2017, 1, 1)]
@pytest.mark.parametrize('dt', tuple(DATES))
def test_year_only(dt):
    dtstr = dt.strftime('%Y')

    assert isoparse(dtstr) == dt

DATES += [datetime(2000, 2, 1), datetime(2017, 4, 1)]
@pytest.mark.parametrize('dt', tuple(DATES))
@pytest.mark.parametrize('fmt',
    ['%Y%m', '%Y-%m'])
def test_year_month(dt, fmt):
    dtstr = dt.strftime(fmt)

    assert isoparse(dtstr) == dt

DATES += [datetime(2016, 2, 29), datetime(2018, 3, 15)]
YMD_FMTS = ('%Y%m%d', '%Y-%m-%d')
@pytest.mark.parametrize('dt', tuple(DATES))
@pytest.mark.parametrize('fmt', YMD_FMTS)
def test_year_month_day(dt, fmt):
    dtstr = dt.strftime(fmt)

    assert isoparse(dtstr) == dt

def _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset,
                            microsecond_precision=None):
    tzi, offset_str = tzoffset
    fmt = date_fmt + 'T' + time_fmt
    dt = dt.replace(tzinfo=tzi)
    dtstr = dt.strftime(fmt)

    if microsecond_precision is not None:
        if not fmt.endswith('%f'):
            raise ValueError('Time format has no microseconds!')

        if microsecond_precision != 6:
            dtstr = dtstr[:-(6 - microsecond_precision)]
        elif microsecond_precision > 6:
            raise ValueError('Precision must be 1-6')

    dtstr += offset_str

    assert isoparse(dtstr) == dt

DATETIMES = [datetime(1998, 4, 16, 12),
             datetime(2019, 11, 18, 23),
             datetime(2014, 12, 16, 4)]
@pytest.mark.parametrize('dt', tuple(DATETIMES))
@pytest.mark.parametrize('date_fmt', YMD_FMTS)
@pytest.mark.parametrize('tzoffset', TZOFFSETS)
def test_ymd_h(dt, date_fmt, tzoffset):
    _isoparse_date_and_time(dt, date_fmt, '%H', tzoffset)

DATETIMES = [datetime(2012, 1, 6, 9, 37)]
@pytest.mark.parametrize('dt', tuple(DATETIMES))
@pytest.mark.parametrize('date_fmt', YMD_FMTS)
@pytest.mark.parametrize('time_fmt', ('%H%M', '%H:%M'))
@pytest.mark.parametrize('tzoffset', TZOFFSETS)
def test_ymd_hm(dt, date_fmt, time_fmt, tzoffset):
    _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset)

DATETIMES = [datetime(2003, 9, 2, 22, 14, 2),
             datetime(2003, 8, 8, 14, 9, 14),
             datetime(2003, 4, 7, 6, 14, 59)]
HMS_FMTS = ('%H%M%S', '%H:%M:%S')
@pytest.mark.parametrize('dt', tuple(DATETIMES))
@pytest.mark.parametrize('date_fmt', YMD_FMTS)
@pytest.mark.parametrize('time_fmt', HMS_FMTS)
@pytest.mark.parametrize('tzoffset', TZOFFSETS)
def test_ymd_hms(dt, date_fmt, time_fmt, tzoffset):
    _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset)

DATETIMES = [datetime(2017, 11, 27, 6, 14, 30, 123456)]
@pytest.mark.parametrize('dt', tuple(DATETIMES))
@pytest.mark.parametrize('date_fmt', YMD_FMTS)
@pytest.mark.parametrize('time_fmt', (x + '.%f' for x in HMS_FMTS))
@pytest.mark.parametrize('tzoffset', TZOFFSETS)
@pytest.mark.parametrize('precision', list(range(3, 7)))
def test_ymd_hms_micro(dt, date_fmt, time_fmt, tzoffset, precision):
    # Truncate the microseconds to the desired precision for the representation
    dt = dt.replace(microsecond=int(round(dt.microsecond, precision-6)))

    _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset, precision)

@pytest.mark.parametrize('tzoffset', FULL_TZOFFSETS)
def test_full_tzoffsets(tzoffset):
    dt = datetime(2017, 11, 27, 6, 14, 30, 123456)
    date_fmt = '%Y-%m-%d'
    time_fmt = '%H:%M:%S.%f'

    _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset)

@pytest.mark.parametrize('dt_str', [
    '2014-04-11T00',
    '2014-04-11T24',
    '2014-04-11T00:00',
    '2014-04-11T24:00',
    '2014-04-11T00:00:00',
    '2014-04-11T24:00:00',
    '2014-04-11T00:00:00.000',
    '2014-04-11T24:00:00.000',
    '2014-04-11T00:00:00.000000',
    '2014-04-11T24:00:00.000000']
)
def test_datetime_midnight(dt_str):
    assert isoparse(dt_str) == datetime(2014, 4, 11, 0, 0, 0, 0)

##
# Uncommon date formats
TIME_ARGS = ('time_args',
    ((None, time(0), None), ) + tuple(('%H:%M:%S.%f', _t, _tz)
        for _t, _tz in it.product([time(0), time(9, 30), time(14, 47)],
                                  TZOFFSETS)))

@pytest.mark.parametrize('date_val', [date(2016, 12, 31),
                                      date(2016, 4, 1),
                                      date(2016, 2, 28)])
@pytest.mark.parametrize('date_fmt', ('--%m%d', '--%m-%d'))
@pytest.mark.parametrize(*TIME_ARGS)
def test_noyear(date_val, date_fmt, time_args):
    time_fmt, time_val, tzoffset = time_args

    fmt = date_fmt
    dt = datetime.combine(date_val, time_val)

    if time_fmt is not None:
        tzi, offset_str = tzoffset
        fmt += 'T' + time_fmt
        dt = dt.replace(tzinfo=tzi)
    else:
        offset_str = ''

    dtstr = dt.strftime(fmt) + offset_str

    dt_act = Isoparser(default_year=2016).isoparse(dtstr)
    assert dt_act == dt

@pytest.mark.parametrize('year,expected', [
    (2017, 2016),
    (2016, 2016),
    (2003, 2000),
    (2000, 2000),
    (1903, 1896),
    (1900, 1896)])
def test_noyear_leap(year, expected):
    dtstr = '--02-29'
    dt_expected = datetime(expected, 2, 29)
    isoparser = Isoparser(default_year=year)

    dt_actual = isoparser.isoparse(dtstr)
    assert dt_actual == dt_expected

@pytest.mark.parametrize('isocal,dt_expected',[
    ((2017, 10), datetime(2017, 3, 6)),
    ((2020, 1), datetime(2019, 12, 30)),    # ISO year != Cal year
    ((2004, 53), datetime(2004, 12, 27)),   # Only half the week is in 2014
])
def test_isoweek(isocal, dt_expected):
    # TODO: Figure out how to parametrize this on formats, too
    for fmt in ('{:04d}-W{:02d}', '{:04d}W{:02d}'):
        dtstr = fmt.format(*isocal)
        assert isoparse(dtstr) == dt_expected

@pytest.mark.parametrize('isocal,dt_expected',[
    ((2016, 13, 7), datetime(2016, 4, 3)),
    ((2004, 53, 7), datetime(2005, 1, 2)),      # ISO year != Cal year
    ((2009, 1, 2), datetime(2008, 12, 30)),     # ISO year < Cal year
    ((2009, 53, 6), datetime(2010, 1, 2))       # ISO year > Cal year
])
def test_isoweek_day(isocal, dt_expected):
    # TODO: Figure out how to parametrize this on formats, too
    for fmt in ('{:04d}-W{:02d}-{:d}', '{:04d}W{:02d}{:d}'):
        dtstr = fmt.format(*isocal)
        assert isoparse(dtstr) == dt_expected

@pytest.mark.parametrize('isoord,dt_expected', [
    ((2004, 1), datetime(2004, 1, 1)),
    ((2016, 60), datetime(2016, 2, 29)),
    ((2017, 60), datetime(2017, 3, 1)),
    ((2016, 366), datetime(2016, 12, 31)),
    ((2017, 365), datetime(2017, 12, 31))
])
def test_iso_ordinal(isoord, dt_expected):
    for fmt in ('{:04d}-{:03d}', '{:04d}{:03d}'):
        dtstr = fmt.format(*isoord)

        assert isoparse(dtstr) == dt_expected


###
# Acceptance of bytes
@pytest.mark.parametrize('isostr,dt', [
    (b'2014', datetime(2014, 1, 1)),
    (b'20140204', datetime(2014, 2, 4)),
    (b'2014-02-04', datetime(2014, 2, 4)),
    (b'2014-02-04T12', datetime(2014, 2, 4, 12)),
    (b'2014-02-04T12:30', datetime(2014, 2, 4, 12, 30)),
    (b'2014-02-04T12:30:15', datetime(2014, 2, 4, 12, 30, 15)),
    (b'2014-02-04T12:30:15.224', datetime(2014, 2, 4, 12, 30, 15, 224000)),
    (b'20140204T123015.224', datetime(2014, 2, 4, 12, 30, 15, 224000)),
    (b'2014-02-04T12:30:15.224Z', datetime(2014, 2, 4, 12, 30, 15, 224000,
                                           tz.tzutc())),
    (b'2014-02-04T12:30:15.224+05:00',
        datetime(2014, 2, 4, 12, 30, 15, 224000,
                 tzinfo=tz.tzoffset(None, timedelta(hours=5))))])
def test_bytes(isostr, dt):
    assert isoparse(isostr) == dt


###
# Invalid ISO strings
@pytest.mark.parametrize('isostr,exception', [
    ('201', ValueError),                        # ISO string too short
    ('2012-0425', ValueError),                  # Inconsistent date separators
    ('201204-25', ValueError),                  # Inconsistent date separators
    ('20120425T0120:00', ValueError),           # Inconsistent time separators
    ('20120425T012500-334', ValueError),        # Wrong microsecond separator
    ('20120425C012500', ValueError),            # Wrong time separator
    ('20120411T03:30+', ValueError),            # Time zone too short
    ('20120411T03:30+1234567', ValueError),     # Time zone too long
    ('20120411T03:30-25:40', ValueError),       # Time zone invalid
    ('20120411T03:30+00:60', ValueError),       # Time zone invalid minutes
    ('20120411T03:30+00:61', ValueError),       # Time zone invalid minutes
    ('20120411T033030.123456012:00',            # No sign in time zone
        ValueError),
    ('2012-W00', ValueError),                   # Invalid ISO week
    ('2012-W55', ValueError),                   # Invalid ISO week
    ('2012-W01-0', ValueError),                 # Invalid ISO week day
    ('2012-W01-8', ValueError),                 # Invalid ISO week day
    ('2013-000', ValueError),                   # Invalid ordinal day
    ('2013-366', ValueError),                   # Invalid ordinal day
    ('2013366', ValueError),                    # Invalid ordinal day
    ('2014-03-12Т12:30:14', ValueError)         # Cyrillic T
])
def test_iso_raises(isostr, exception):
    with pytest.raises(exception):
        isoparse(isostr)


@pytest.mark.xfail()
@pytest.mark.parametrize('isostr,exception', [
    ('20120425T01:2000', ValueError),           # Inconsistent time separators
])
def test_iso_raises_failing(isostr, exception):
    # These are test cases where the current implementation is too lenient
    # and need to be fixed
    with pytest.raises(exception):
        isoparse(isostr)

###
# Test ISOParser constructor
@pytest.mark.parametrize('year', [0, 10000])
def test_isoparser_invalid_years(year):
    with pytest.raises(ValueError):
        Isoparser(default_year=year)

@pytest.mark.parametrize('sep', ['  ', '9', '🍛'])
def test_isoparser_invalid_sep(sep):
    with pytest.raises(ValueError):
        Isoparser(sep=sep)


###
# Test parse_tzstr
@pytest.mark.parametrize('tzoffset', FULL_TZOFFSETS)
def test_parse_tzstr(tzoffset):
    dt = datetime(2017, 11, 27, 6, 14, 30, 123456)
    date_fmt = '%Y-%m-%d'
    time_fmt = '%H:%M:%S.%f'

    _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset)


@pytest.mark.parametrize('tzstr', [
    '-00:00', '+00:00', '+00', '-00', '+0000', '-0000'
])
@pytest.mark.parametrize('zero_as_utc', [True, False])
def test_parse_tzstr_zero_as_utc(tzstr, zero_as_utc):
    tzi = Isoparser.parse_tzstr(tzstr, zero_as_utc=zero_as_utc)
    assert tzi == tz.tzutc()
    assert (type(tzi) == tz.tzutc) == zero_as_utc


###
# Test parse_isodate
@pytest.mark.parametrize('date_val', [date(2016, 12, 31),
                                      date(2016, 4, 1),
                                      date(2016, 2, 28)])
@pytest.mark.parametrize('date_fmt', ('--%m%d', '--%m-%d'))
def test_noyear_date(date_val, date_fmt):
    dtstr = date_val.strftime(date_fmt)

    d_act = Isoparser(default_year=2016).parse_isodate(dtstr)
    assert d_act == date_val


def __make_date_examples():
    dates_no_day = [
        date(1999, 12, 1),
        date(2016, 2, 1),
        date(1000, 11, 1)
    ]

    date_no_day_fmts = ('%Y%m', '%Y-%m')

    o = it.product(dates_no_day, date_no_day_fmts)

    dates_w_day = [
        date(1969, 12, 31),
        date(1900, 1, 1),
        date(2016, 2, 29),
        date(2017, 11, 14)
    ]

    dates_w_day_fmts = ('%Y%m%d', '%Y-%m-%d')
    o = it.chain(o, it.product(dates_w_day, dates_w_day_fmts))

    return list(o)


@pytest.mark.parametrize('d,dt_fmt', __make_date_examples())
@pytest.mark.parametrize('as_bytes', [True, False])
def test_parse_isodate(d, dt_fmt, as_bytes):
    d_str = d.strftime(dt_fmt)

    if isinstance(d_str, six.text_type) and as_bytes:
        d_str = d_str.encode('ascii')
    elif isinstance(d_str, six.binary_type) and not as_bytes:
        d_str = d_str.decode('ascii')

    iparser = Isoparser()
    assert iparser.parse_isodate(d_str) == d


@pytest.mark.parametrize('isostr,exception', [
    ('243', ValueError),                        # ISO string too short
    ('2014-0423', ValueError),                  # Inconsistent date separators
    ('201404-23', ValueError),                  # Inconsistent date separators
    ('2014日03月14', ValueError),                # Not ASCII
    ('2013-02-29', ValueError),                 # Not a leap year
    ('2014/12/03', ValueError),                 # Wrong separators
    ('2014-04-19T', ValueError),                # Unknown components
])
def test_isodate_raises(isostr, exception):
    with pytest.raises(exception):
        Isoparser().parse_isodate(isostr)
