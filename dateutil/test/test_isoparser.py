from datetime import datetime, timedelta, date, time
import itertools as it

from dateutil.tz import tz
from dateutil.parser import isoparse

import pytest

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
    dt = dt.replace(microsecond=round(dt.microsecond, precision-6))

    _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset, precision)

@pytest.mark.parametrize('tzoffset', FULL_TZOFFSETS)
def test_full_tzoffsets(tzoffset):
    dt = datetime(2017, 11, 27, 6, 14, 30, 123456)
    date_fmt = '%Y-%m-%d'
    time_fmt = '%H:%M:%S.%f'

    _isoparse_date_and_time(dt, date_fmt, time_fmt, tzoffset)


##
# Uncommon date formats
TIME_ARGS = ('time_args',
    ((None, time(0), None), ) + tuple(('%H:%M:%S.%f', _t, _tz)
        for _t, _tz in it.product([time(0), time(9, 30), time(14, 47)],
                                  TZOFFSETS)))

@pytest.mark.parametrize('date_val', [date(1900, 12, 31),
                                      date(1900, 4, 1),
                                      date(1900, 2, 28)])
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

    assert isoparse(dtstr) == dt