"""Tests for `tz.tzfile`."""

import contextlib
import functools
import os
import shutil
import struct
import sys
import threading
from datetime import date, datetime, time, timedelta

import attr
import pytest
import six

from dateutil import tz

TZPATH_LOCK = threading.Lock()
####
# Backports
functools_cache = getattr(functools, "cache", None)
if functools_cache is None:

    def functools_cache(f):
        _cache = {}

        @functools.wraps(f)
        def inner_func():
            if "value" not in _cache:
                _cache["value"] = f()
            return _cache["value"]

        return inner_func


if sys.version_info < (3, 4):

    def contextdecorator(wrapped):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            class ContextDecorator:
                def __init__(self):
                    self.cm = contextlib.contextmanager(wrapped)(
                        *args, **kwargs
                    )

                def __enter__(self):
                    return self.cm.__enter__()

                def __exit__(self, *args, **kwargs):
                    return self.cm.__exit__(*args, **kwargs)

                def __call__(self, f):
                    @functools.wraps(f)
                    def inner(*iargs, **ikwargs):
                        with self:
                            return f(*iargs, **ikwargs)

                    return inner

            return ContextDecorator()

        return wrapper

else:
    contextdecorator = contextlib.contextmanager

if six.PY2:

    def timestamp(dt):
        if dt.tzinfo is None:
            dt_utc = dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.UTC)
        else:
            dt_utc = dt.astimezone(tz.UTC)

        return (dt_utc - datetime(1970, 1, 1, tzinfo=tz.UTC)).total_seconds()

else:
    timestamp = datetime.timestamp


####
# Test utilities
def _copy_resource_to(resource, path):
    """Copies a test resource to a path on disk."""
    from dateutil._tzdata_impl import _open_binary

    # Python 2.7 compat
    parent_dir = os.path.dirname(path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    with _open_binary("tests.resources", resource) as f:
        with open(path, "wb") as out_f:
            out_f.write(f.read())


def pop_tzdata_modules():
    tzdata_modules = {}
    for modname in list(sys.modules):
        if modname.split(".", 1)[0] != "tzdata":  # pragma: nocover
            continue

        tzdata_modules[modname] = sys.modules.pop(modname)

    return tzdata_modules


def construct_zone(transitions, after=None, version=3):
    # These are not used for anything, so we're not going to include
    # them for now.
    isutc = []
    isstd = []
    leap_seconds = []

    offset_lists = [[], []]
    trans_times_lists = [[], []]
    trans_idx_lists = [[], []]

    v1_range = (-(2**31), 2**31)
    v2_range = (-(2**63), 2**63)
    ranges = [v1_range, v2_range]

    def zt_as_tuple(zt):
        # zt may be a tuple (timestamp, offset_before, offset_after) or
        # a ZoneTransition object -- this is to allow the timestamp to be
        # values that are outside the valid range for datetimes but still
        # valid 64-bit timestamps.
        if isinstance(zt, tuple):
            return zt

        if zt.transition:
            trans_time = int(timestamp(zt.transition_utc))
        else:
            trans_time = None

        return (trans_time, zt.offset_before, zt.offset_after)

    transitions = sorted(map(zt_as_tuple, transitions), key=lambda x: x[0])

    for zt in transitions:
        trans_time, offset_before, offset_after = zt

        for v, (dt_min, dt_max) in enumerate(ranges):
            offsets = offset_lists[v]
            trans_times = trans_times_lists[v]
            trans_idx = trans_idx_lists[v]

            if trans_time is not None and not (dt_min <= trans_time <= dt_max):
                continue

            if offset_before not in offsets:
                offsets.append(offset_before)

            if offset_after not in offsets:
                offsets.append(offset_after)

            if trans_time is not None:
                trans_times.append(trans_time)
                trans_idx.append(offsets.index(offset_after))

    isutcnt = len(isutc)
    isstdcnt = len(isstd)
    leapcnt = len(leap_seconds)

    zonefile = six.BytesIO()

    time_types = ("l", "q")
    for v in range(min((version, 2))):
        offsets = offset_lists[v]
        trans_times = trans_times_lists[v]
        trans_idx = trans_idx_lists[v]
        time_type = time_types[v]

        # Translate the offsets into something closer to the C values
        abbrstr = bytearray()
        ttinfos = []

        for offset in offsets:
            utcoff = int(offset.utcoffset.total_seconds())
            isdst = bool(offset.dst)
            abbrind = len(abbrstr)

            ttinfos.append((utcoff, isdst, abbrind))
            abbrstr += offset.tzname.encode("ascii") + b"\x00"
        abbrstr = bytes(abbrstr)

        typecnt = len(offsets)
        timecnt = len(trans_times)
        charcnt = len(abbrstr)

        # Write the header
        zonefile.write(b"TZif")
        zonefile.write(b"%d" % version)
        zonefile.write(b" " * 15)
        zonefile.write(
            struct.pack(
                ">6l", isutcnt, isstdcnt, leapcnt, timecnt, typecnt, charcnt
            )
        )

        # Now the transition data
        zonefile.write(
            struct.pack(
                ">{timecnt}{time_type}".format(
                    timecnt=timecnt, time_type=time_type
                ),
                *trans_times
            )
        )
        zonefile.write(
            struct.pack(">{timecnt}B".format(timecnt=timecnt), *trans_idx)
        )

        for ttinfo in ttinfos:
            zonefile.write(struct.pack(">lbb", *ttinfo))

        zonefile.write(bytes(abbrstr))

        # Now the metadata and leap seconds
        zonefile.write(
            struct.pack("{isutcnt}b".format(isutcnt=isutcnt), *isutc)
        )
        zonefile.write(
            struct.pack("{isstdcnt}b".format(isstdcnt=isstdcnt), *isstd)
        )
        zonefile.write(
            struct.pack(">{leapcnt}l".format(leapcnt=leapcnt), *leap_seconds)
        )

        # Finally we write the TZ string if we're writing a Version 2+ file
        if v > 0:
            zonefile.write(b"\x0A")
            zonefile.write(after.encode("ascii"))
            zonefile.write(b"\x0A")

    zonefile.seek(0)
    return zonefile


@contextdecorator
def set_tzpath(tzpath, block_tzdata=False):
    tzdata_modules = {}
    with TZPATH_LOCK:
        if block_tzdata:
            tzdata_modules = pop_tzdata_modules()
            sys.modules["tzdata"] = None

        old_tzpath = tuple(tz.TZPATH)
        try:
            tz._tzpath.reset_tzpath(to=tzpath)
            yield
        finally:
            sys.modules.pop("tzdata")
            for modname, module in tzdata_modules.items():
                sys.modules[modname] = module

            tz._tzpath.reset_tzpath(to=old_tzpath)


@functools_cache
def rearguard():
    # If we know that we're using the rearguard tzdata file, skip tests
    # that rely on rearguard features.
    for path in tz.TZPATH:
        # Technically you could have more than one set of tzdata, some which
        # are reaguard and some vanguard or whatever, but we'll just assume
        # that the first tzdata file we find is authoritative in terms of
        # version.
        tzdata_zi = os.path.join(path, "tzdata.zi")
        if os.path.exists(tzdata_zi):
            with open(tzdata_zi, "rt") as f:
                if "-rearguard" in next(iter(f)):
                    return True
                else:
                    break
        return False


def as_list(f):
    @functools.wraps(f)
    def inner_func(*args, **kwargs):
        return list(f(*args, **kwargs))

    return inner_func


SUPPORTS_SUB_MINUTE_OFFSETS = not sys.version_info < (3, 6)


####
# Classes representing test data
ZERO = timedelta(0)
ONE_H = timedelta(hours=1)
SECOND = timedelta(seconds=1)

if SUPPORTS_SUB_MINUTE_OFFSETS:

    def offset_converter(td):
        return td

else:

    def offset_converter(td):
        minutes = round(td.total_seconds() / 60.0)
        return timedelta(minutes=minutes)


@attr.s
class ZoneOffset(object):
    tzname = attr.ib()
    utcoffset = attr.ib()
    dst = attr.ib(default=ZERO, converter=offset_converter)

    def __attrs_post_init__(self):
        self.raw_utcoffset = self.utcoffset
        self.utcoffset = offset_converter(self.utcoffset)


@attr.s
class ZoneTransition(object):
    transition = attr.ib()
    offset_before = attr.ib()
    offset_after = attr.ib()
    marks = attr.ib(default=None)

    @property
    def transition_utc(self):
        return (self.transition - self.offset_before.raw_utcoffset).replace(
            tzinfo=tz.UTC
        )

    @property
    def fold(self):
        """Whether this introduces a fold"""
        return self.offset_before.utcoffset > self.offset_after.utcoffset

    @property
    def gap(self):
        """Whether this introduces a gap"""
        return (
            self.offset_before.raw_utcoffset < self.offset_after.raw_utcoffset
        )

    @property
    def delta(self):
        return (
            self.offset_after.raw_utcoffset - self.offset_before.raw_utcoffset
        )

    @property
    def anomaly_start(self):
        if self.fold:
            return self.transition + self.delta
        else:
            return self.transition

    @property
    def anomaly_end(self):
        if not self.fold:
            return self.transition + self.delta
        else:
            return self.transition


####
# Test data
@functools_cache
def get_zonedump_data():
    def _zone_dump_data():
        def _Africa_Abidjan():
            LMT = ZoneOffset("LMT", timedelta(seconds=-968))
            GMT = ZoneOffset("GMT", ZERO)

            return [
                ZoneTransition(datetime(1912, 1, 1), LMT, GMT),
            ]

        def _Africa_Casablanca():
            P00_s = ZoneOffset("+00", ZERO, ZERO)
            P01_d = ZoneOffset("+01", ONE_H, ONE_H)
            P00_d = ZoneOffset("+00", ZERO, -ONE_H)
            P01_s = ZoneOffset("+01", ONE_H, ZERO)

            return [
                # Morocco sometimes pauses DST during Ramadan
                ZoneTransition(datetime(2018, 3, 25, 2), P00_s, P01_d),
                ZoneTransition(datetime(2018, 5, 13, 3), P01_d, P00_s),
                ZoneTransition(datetime(2018, 6, 17, 2), P00_s, P01_d),
                # On October 28th Morocco set standard time to +01,
                # with negative DST only during Ramadan
                ZoneTransition(datetime(2018, 10, 28, 3), P01_d, P01_s),
                ZoneTransition(datetime(2019, 5, 5, 3), P01_s, P00_d),
                ZoneTransition(datetime(2019, 6, 9, 2), P00_d, P01_s),
            ]

        def _America_Los_Angeles():
            LMT = ZoneOffset("LMT", timedelta(seconds=-28378), ZERO)
            PST = ZoneOffset("PST", timedelta(hours=-8), ZERO)
            PDT = ZoneOffset("PDT", timedelta(hours=-7), ONE_H)
            PWT = ZoneOffset("PWT", timedelta(hours=-7), ONE_H)
            PPT = ZoneOffset("PPT", timedelta(hours=-7), ONE_H)

            return [
                ZoneTransition(datetime(1883, 11, 18, 12, 7, 2), LMT, PST),
                ZoneTransition(datetime(1918, 3, 31, 2), PST, PDT),
                ZoneTransition(datetime(1918, 3, 31, 2), PST, PDT),
                ZoneTransition(datetime(1918, 10, 27, 2), PDT, PST),
                # Transition to Pacific War Time
                ZoneTransition(datetime(1942, 2, 9, 2), PST, PWT),
                # Transition from Pacific War Time to Pacific Peace Time
                ZoneTransition(datetime(1945, 8, 14, 16), PWT, PPT),
                ZoneTransition(datetime(1945, 9, 30, 2), PPT, PST),
                ZoneTransition(datetime(2015, 3, 8, 2), PST, PDT),
                ZoneTransition(datetime(2015, 11, 1, 2), PDT, PST),
                # After 2038: Rules continue indefinitely
                ZoneTransition(datetime(2450, 3, 13, 2), PST, PDT),
                ZoneTransition(datetime(2450, 11, 6, 2), PDT, PST),
            ]

        def _America_Santiago():
            LMT = ZoneOffset("LMT", timedelta(seconds=-16965), ZERO)
            SMT = ZoneOffset("SMT", timedelta(seconds=-16965), ZERO)
            N05 = ZoneOffset("-05", timedelta(seconds=-18000), ZERO)
            N04 = ZoneOffset("-04", timedelta(seconds=-14400), ZERO)
            N03 = ZoneOffset("-03", timedelta(seconds=-10800), ONE_H)

            return [
                ZoneTransition(datetime(1890, 1, 1), LMT, SMT),
                ZoneTransition(datetime(1910, 1, 10), SMT, N05),
                ZoneTransition(datetime(1916, 7, 1), N05, SMT),
                ZoneTransition(datetime(2008, 3, 30), N03, N04),
                ZoneTransition(datetime(2008, 10, 12), N04, N03),
                ZoneTransition(datetime(2040, 4, 8), N03, N04),
                ZoneTransition(datetime(2040, 9, 2), N04, N03),
            ]

        def _Asia_Tokyo():
            JST = ZoneOffset("JST", timedelta(seconds=32400), ZERO)
            JDT = ZoneOffset("JDT", timedelta(seconds=36000), ONE_H)

            # Japan had DST from 1948 to 1951, and it was unusual in that
            # the transition from DST to STD occurred at 25:00, and is
            # denominated as such in the time zone database
            return [
                ZoneTransition(datetime(1948, 5, 2), JST, JDT),
                ZoneTransition(datetime(1948, 9, 12, 1), JDT, JST),
                ZoneTransition(datetime(1951, 9, 9, 1), JDT, JST),
            ]

        def _Australia_Sydney():
            LMT = ZoneOffset("LMT", timedelta(seconds=36292), ZERO)
            AEST = ZoneOffset("AEST", timedelta(seconds=36000), ZERO)
            AEDT = ZoneOffset("AEDT", timedelta(seconds=39600), ONE_H)

            return [
                ZoneTransition(datetime(1895, 2, 1), LMT, AEST),
                ZoneTransition(datetime(1917, 1, 1, 2), AEST, AEDT),
                ZoneTransition(datetime(1917, 3, 25, 3), AEDT, AEST),
                ZoneTransition(datetime(2012, 4, 1, 3), AEDT, AEST),
                ZoneTransition(datetime(2012, 10, 7, 2), AEST, AEDT),
                ZoneTransition(datetime(2040, 4, 1, 3), AEDT, AEST),
                ZoneTransition(datetime(2040, 10, 7, 2), AEST, AEDT),
            ]

        def _Europe_Dublin():
            LMT = ZoneOffset("LMT", timedelta(seconds=-1521), ZERO)
            DMT = ZoneOffset("DMT", timedelta(seconds=-1521), ZERO)
            IST_0 = ZoneOffset("IST", timedelta(seconds=2079), ONE_H)
            GMT_0 = ZoneOffset("GMT", ZERO, ZERO)
            BST = ZoneOffset("BST", ONE_H, ONE_H)
            GMT_1 = ZoneOffset("GMT", ZERO, -ONE_H)
            IST_1 = ZoneOffset("IST", ONE_H, ZERO)

            return [
                ZoneTransition(datetime(1880, 8, 2, 0), LMT, DMT),
                ZoneTransition(datetime(1916, 5, 21, 2), DMT, IST_0),
                ZoneTransition(datetime(1916, 10, 1, 3), IST_0, GMT_0),
                ZoneTransition(datetime(1917, 4, 8, 2), GMT_0, BST),
                ZoneTransition(datetime(2016, 3, 27, 1), GMT_1, IST_1),
                ZoneTransition(datetime(2016, 10, 30, 2), IST_1, GMT_1),
                ZoneTransition(datetime(2487, 3, 30, 1), GMT_1, IST_1),
                ZoneTransition(datetime(2487, 10, 26, 2), IST_1, GMT_1),
            ]

        def _Europe_Lisbon():
            WET = ZoneOffset("WET", ZERO, ZERO)
            WEST = ZoneOffset("WEST", ONE_H, ONE_H)
            CET = ZoneOffset("CET", ONE_H, ZERO)
            CEST = ZoneOffset("CEST", timedelta(seconds=7200), ONE_H)

            return [
                ZoneTransition(datetime(1992, 3, 29, 1), WET, WEST),
                ZoneTransition(datetime(1992, 9, 27, 2), WEST, CET),
                ZoneTransition(datetime(1993, 3, 28, 2), CET, CEST),
                ZoneTransition(datetime(1993, 9, 26, 3), CEST, CET),
                ZoneTransition(datetime(1996, 3, 31, 2), CET, WEST),
                ZoneTransition(datetime(1996, 10, 27, 2), WEST, WET),
            ]

        def _Europe_London():
            LMT = ZoneOffset("LMT", timedelta(seconds=-75), ZERO)
            GMT = ZoneOffset("GMT", ZERO, ZERO)
            BST = ZoneOffset("BST", ONE_H, ONE_H)

            return [
                ZoneTransition(datetime(1847, 12, 1), LMT, GMT),
                ZoneTransition(datetime(2005, 3, 27, 1), GMT, BST),
                ZoneTransition(datetime(2005, 10, 30, 2), BST, GMT),
                ZoneTransition(datetime(2043, 3, 29, 1), GMT, BST),
                ZoneTransition(datetime(2043, 10, 25, 2), BST, GMT),
            ]

        def _Pacific_Kiritimati():
            LMT = ZoneOffset("LMT", timedelta(seconds=-37760), ZERO)
            N1040 = ZoneOffset("-1040", timedelta(seconds=-38400), ZERO)
            N10 = ZoneOffset("-10", timedelta(seconds=-36000), ZERO)
            P14 = ZoneOffset("+14", timedelta(seconds=50400), ZERO)

            # This is literally every transition in Christmas Island history
            return [
                ZoneTransition(datetime(1901, 1, 1), LMT, N1040),
                ZoneTransition(datetime(1979, 10, 1), N1040, N10),
                # They skipped December 31, 1994
                ZoneTransition(datetime(1994, 12, 31), N10, P14),
            ]

        return {
            "Africa/Abidjan": _Africa_Abidjan(),
            "Africa/Casablanca": _Africa_Casablanca(),
            "America/Los_Angeles": _America_Los_Angeles(),
            "America/Santiago": _America_Santiago(),
            "Australia/Sydney": _Australia_Sydney(),
            "Asia/Tokyo": _Asia_Tokyo(),
            "Europe/Dublin": _Europe_Dublin(),
            "Europe/Lisbon": _Europe_Lisbon(),
            "Europe/London": _Europe_London(),
            "Pacific/Kiritimati": _Pacific_Kiritimati(),
        }

    return _zone_dump_data()


@functools_cache
def transition_examples():
    zonedump_data = get_zonedump_data()
    return tuple(zonedump_data.items())


@functools_cache
def fixed_offset_zones():
    return {}


####
# Tests


@set_tzpath((), block_tzdata=True)
def test_no_tz_data():
    """Test what happens when no TZ data is available."""
    tz.gettz.cache_clear()
    NYC = tz.gettz("America/New_York")
    assert NYC is None


def test_tzpath_setting(tmp_path):
    """Ensure that setting tz.TZPATH changes where `tz.gettz` searches."""
    if six.PY2:
        tmp_path = str(tmp_path)

    with set_tzpath([tmp_path]):
        _copy_resource_to(
            "liliput_tzif", os.path.join(str(tmp_path), "Fictional", "Liliput")
        )
        tz.gettz.cache_clear()

        fiction_land = tz.gettz("Fictional/Liliput")

        assert fiction_land is not None


@pytest.mark.parametrize(
    "dt, errtype",
    [
        # Should fail if tzinfo is not `self`
        (datetime(2019, 1, 1, tzinfo=tz.UTC), ValueError),
        (datetime(2019, 1, 1), ValueError),
        # Only works with `datetime`
        (date(2019, 1, 1), TypeError),
        (time(0), TypeError),
        (0, TypeError),
        ("2019-01-01", TypeError),
    ],
)
def test_fromutc_errors(dt, errtype):
    """tzinfo.fromutc invocations that raise an error."""
    zone = tz.gettz("Europe/London")  # Any zone should work
    with pytest.raises(errtype):
        zone.fromutc(dt)


@as_list
def _get_unambiguous_transitions():
    for key, zone_transitions in transition_examples():
        for zone_transition in zone_transitions:
            yield (
                key,
                zone_transition.transition - timedelta(days=2),
                zone_transition.offset_before,
            )
            yield (
                key,
                zone_transition.transition + timedelta(days=2),
                zone_transition.offset_after,
            )


@pytest.mark.skipif(
    rearguard(), reason="Skipping TZ tests with rearguard files"
)
@pytest.mark.parametrize("key, dt, offset", _get_unambiguous_transitions())
def test_unambiguous(key, dt, offset):
    """Test times that are *not* ambiguous."""
    tzi = tz.gettz(key)
    dt = dt.replace(tzinfo=tzi)

    assert dt.tzname() == offset.tzname
    assert dt.utcoffset() == offset.utcoffset
    assert dt.dst() == offset.dst


@as_list
def _get_folds_and_gaps():
    for key, zone_transitions in transition_examples():
        for zt in zone_transitions:
            if not zt.fold and not zt.gap:
                continue
            test_group = "fold" if zt.fold else "gap"

            # Cases are of the form key, dt, fold, offset
            dt = zt.anomaly_start - timedelta(seconds=1)
            yield (key, dt, 0, zt.offset_before)
            yield (key, dt, 1, zt.offset_before)

            dt = zt.anomaly_start
            yield (key, dt, 0, zt.offset_before)
            yield (key, dt, 1, zt.offset_after)

            dt = zt.anomaly_start + timedelta(seconds=1)
            yield (key, dt, 0, zt.offset_before)
            yield (key, dt, 1, zt.offset_after)

            dt = zt.anomaly_end - timedelta(seconds=1)
            yield (key, dt, 0, zt.offset_before)
            yield (key, dt, 1, zt.offset_after)

            dt = zt.anomaly_end
            yield (key, dt, 0, zt.offset_after)
            yield (key, dt, 1, zt.offset_after)

            dt = zt.anomaly_end + timedelta(seconds=1)
            yield (key, dt, 0, zt.offset_after)
            yield (key, dt, 1, zt.offset_after)


@pytest.mark.skipif(
    rearguard(), reason="Skipping TZ tests with rearguard files"
)
@pytest.mark.parametrize("key, dt, fold, offset", _get_folds_and_gaps())
def test_gaps_and_folds(key, dt, fold, offset):
    """Test times that are ambiguous."""
    tzi = tz.gettz(key)
    dt = tz.enfold(dt.replace(tzinfo=tzi), fold)

    assert dt.tzname() == offset.tzname
    assert dt.utcoffset() == offset.utcoffset
    assert dt.dst() == offset.dst


@as_list
def _get_folds_from_utc():
    for key, zone_transitions in transition_examples():
        for zt in zone_transitions:
            if not zt.fold:
                continue
            dt_utc = zt.transition_utc
            yield (key, dt_utc - SECOND, 0)
            yield (key, dt_utc + SECOND, 1)


@pytest.mark.parametrize("key, dt_utc, expected_fold", _get_folds_from_utc())
def test_folds_from_utc(key, dt_utc, expected_fold):
    tzi = tz.gettz(key)
    dt = dt_utc.astimezone(tzi)

    assert getattr(dt, "fold", 0) == expected_fold


def test_time_fixed_offset():
    utc = tz.gettz("UTC")
    assert isinstance(utc, tz.tzfile)

    t = time(11, 1, tzinfo=utc)
    assert t.utcoffset() == ZERO


def test_time_varying_offset():
    tzi = tz.gettz("America/New_York")
    t = time(11, 1, tzinfo=tzi)

    assert t.utcoffset() is None
    assert t.tzname() is None
    assert t.dst() is None


def test_one_transition():
    LMT = ZoneOffset("LMT", -timedelta(hours=6, minutes=31, seconds=2))
    STD = ZoneOffset("STD", -timedelta(hours=6))

    transitions = [
        ZoneTransition(datetime(1883, 6, 9, 14), LMT, STD),
    ]

    after = "STD6"

    zf = construct_zone(transitions, after)
    zi = tz.tzfile(zf, key="One Transition")

    dt0 = datetime(1883, 6, 9, 1, tzinfo=zi)
    dt1 = datetime(1883, 6, 10, 1, tzinfo=zi)

    for dt, offset in [(dt0, LMT), (dt1, STD)]:
        # TODO: Use subtests
        assert dt.tzname() == offset.tzname
        assert dt.utcoffset() == offset.utcoffset
        assert dt.dst() == offset.dst

    dts = [
        (
            datetime(1883, 6, 9, 1, tzinfo=zi),
            (
                datetime(1883, 6, 9, 7, 31, 2, tzinfo=tz.UTC)
                if SUPPORTS_SUB_MINUTE_OFFSETS
                else datetime(1883, 6, 9, 7, 31, tzinfo=tz.UTC)
            ),
        ),
        (
            datetime(2010, 4, 1, 12, tzinfo=zi),
            datetime(2010, 4, 1, 18, tzinfo=tz.UTC),
        ),
    ]

    for dt_local, dt_utc in dts:
        # TODO: Use subtests
        dt_actual = dt_utc.astimezone(zi)
        assert dt_actual == dt_local

        dt_utc_actual = dt_local.astimezone(tz.UTC)
        assert dt_utc_actual == dt_utc


@functools_cache
def one_transition_zone_dst():
    DST = ZoneOffset("DST", ONE_H, ONE_H)
    transitions = [
        ZoneTransition(datetime(1970, 1, 1), DST, DST),
    ]

    after = "STD0DST-1,0/0,J365/25"

    zf = construct_zone(transitions, after)
    zi = tz.tzfile(zf, key="One Zone DST")
    return zi


@pytest.mark.parametrize(
    "dt",
    [
        datetime(1900, 3, 1),
        datetime(1965, 9, 12),
        datetime(1970, 1, 1),
        datetime(2010, 11, 3),
        datetime(2040, 1, 1),
    ],
)
def test_one_zone_dst(dt):
    """Tests for a zone with one transition, DST -> DST"""
    DST = ZoneOffset("DST", ONE_H, ONE_H)
    dt = dt.replace(tzinfo=one_transition_zone_dst())
    assert dt.tzname() == DST.tzname
    assert dt.utcoffset() == DST.utcoffset
    assert dt.dst() == DST.dst


@functools_cache
def _no_tzstr_zone():
    STD = ZoneOffset("STD", ONE_H, ZERO)
    DST = ZoneOffset("DST", 2 * ONE_H, ONE_H)

    transitions = []
    for year in range(1996, 2000):
        transitions.append(ZoneTransition(datetime(year, 3, 1, 2), STD, DST))
        transitions.append(ZoneTransition(datetime(year, 11, 1, 2), DST, STD))

    after = ""

    zf = construct_zone(transitions, after)

    zi = tz.tzfile(zf)
    return zi


@pytest.mark.parametrize(
    "dt, isdst",
    [
        (datetime(1995, 1, 1), False),
        (datetime(1996, 4, 1), True),
        (datetime(1996, 11, 2), False),
        (datetime(2001, 1, 1), False),
    ],
)
def test_no_tzstr(dt, isdst):
    """Test a V2+ zone with no TZStr set."""
    if isdst:
        offset = ZoneOffset("DST", 2 * ONE_H, ONE_H)
    else:
        offset = ZoneOffset("STD", ONE_H, ZERO)
    dt = dt.replace(tzinfo=_no_tzstr_zone())

    assert dt.tzname() == offset.tzname
    assert dt.utcoffset() == offset.utcoffset
    assert dt.dst() == offset.dst


def test_no_tzstr_time():
    """Test that a zone with no tzstr returns None for time objects."""
    t = time(0, tzinfo=_no_tzstr_zone())
    assert t.tzname() is None
    assert t.utcoffset() is None
    assert t.dst() is None


@as_list
def _tz_no_transitions_before_only():
    # From RFC 8536 Section 3.2:
    #
    #   If there are no transitions, local time for all timestamps is
    #   specified by the TZ string in the footer if present and nonempty;
    #   otherwise, it is specified by time type 0.

    offsets = [
        ZoneOffset("STD", ZERO, ZERO),
        ZoneOffset("DST", ONE_H, ONE_H),
    ]

    for offset in offsets:
        # Phantom transition to set time type 0.
        transitions = [
            ZoneTransition(None, offset, offset),
        ]

        after = ""

        zf = construct_zone(transitions, after)
        zi = tz.tzfile(zf, key="Etc/No_Transitions_%s" % offset.tzname)

        dts = [
            datetime(1900, 1, 1),
            datetime(1970, 1, 1),
            datetime(2000, 1, 1),
        ]

        for dt in dts:
            yield dt.replace(tzinfo=zi), offset


@pytest.mark.parametrize("dt, offset", _tz_no_transitions_before_only())
def test_tz_no_transitions_before_only(dt, offset):
    assert dt.utcoffset() == offset.utcoffset
    assert dt.tzname() == offset.tzname
    assert dt.dst() == offset.dst
