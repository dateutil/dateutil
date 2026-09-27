"""Properties that must hold for any valid IANA time zone data.

Unlike the tests in ``test_tzfile.py``, which pin the data they use so that
they can check specific historical transitions, these run against every key
in whatever data is installed: the data on TZPATH (with tzdata blocked) and
the tzdata package, via the ``tz_source`` fixture. In the ``tz`` CI jobs
that is the master branch of the tz database, so these are the tests that
catch the parser mishandling something new in the data.
"""

import calendar
import os
import sys
from datetime import datetime, timedelta

import pytest

from dateutil import tz
from dateutil.tz._tzfile import _TZStr

try:
    import zoneinfo
except ImportError:
    zoneinfo = None

pytestmark = pytest.mark.tzdata_properties

UTC = tz.UTC
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)

# The standard library's C implementation of zoneinfo is an independent
# implementation of the same thing, so on Python 3.9+ it's the reference.
HAS_ZONEINFO = zoneinfo is not None and sys.version_info >= (3, 9)

PAST_YEARS = (1850, 1900, 1945, 1970, 1990, 2000, 2020)
FUTURE_YEARS = (2037, 2038, 2050, 2100, 2400, 9000)
FIXED_INSTANTS = [
    datetime(year, month, 1, tzinfo=UTC)
    for year in PAST_YEARS + FUTURE_YEARS
    for month in (1, 7)
]


def _from_timestamp(ts):
    try:
        return EPOCH + timedelta(seconds=ts)
    except OverflowError:
        # e.g. the "big bang" transitions at -2**59 in fat files
        return None


def _probe_instants(zone):
    """Instants (in UTC) around the interesting parts of a zone."""
    instants = list(FIXED_INSTANTS)

    # Explicit transitions: the first few, and the last ones, which are
    # followed by the TZ string.
    transitions = list(zone._trans_utc)
    for ts in transitions[:3] + transitions[-10:]:
        for delta in (-1, 0, 1):
            instants.append(_from_timestamp(ts + delta))

    # Transitions generated from the TZ string in the footer.
    if isinstance(zone._tz_after, _TZStr):
        std_offset = zone._tz_after.std.utcoff
        std_offset = std_offset.days * 86400 + std_offset.seconds
        for year in (2040, 2100):
            for local_ts in zone._tz_after.transitions(year):
                utc_ts = local_ts - std_offset
                for delta in (-7201, -3601, -1, 0, 1, 3599, 7199):
                    instants.append(_from_timestamp(utc_ts + delta))

    return [instant for instant in instants if instant is not None]


def _keys():
    keys = sorted(tz.available_iana_timezones())
    assert keys
    return keys


def _fold(dt):
    return getattr(dt, "fold", 0)


def test_every_key_loads(tz_source):
    """Every available key loads, from the source it was found in."""
    tzpath = [os.path.join(path, "") for path in tz.TZPATH]
    for key in _keys():
        zone = tz.gettz(key)
        assert isinstance(zone, tz.tzfile), key
        assert zone.key == key

        if tz_source == "tzpath":
            assert any(zone._filename.startswith(p) for p in tzpath), key


def test_utc_round_trip(tz_source):
    """Converting from UTC to local time and back gives the same instant."""
    for key in _keys():
        zone = tz.gettz(key)
        for dt_utc in _probe_instants(zone):
            dt = dt_utc.astimezone(zone)
            assert dt.astimezone(UTC) == dt_utc, (key, dt_utc, dt)


def test_ambiguous_and_imaginary(tz_source):
    """datetime_ambiguous and datetime_exists agree with the fold offsets."""
    for key in _keys():
        zone = tz.gettz(key)
        for dt_utc in _probe_instants(zone):
            local = dt_utc.astimezone(zone).replace(tzinfo=None)
            # Local times an hour either side are more likely to land in a
            # gap or a fold near a transition.
            for wall in (
                local - timedelta(hours=1),
                local,
                local + timedelta(hours=1),
            ):
                dt = wall.replace(tzinfo=zone)
                offset_0 = tz.enfold(dt, fold=0).utcoffset()
                offset_1 = tz.enfold(dt, fold=1).utcoffset()

                case = (key, wall)
                assert tz.datetime_ambiguous(dt) == (offset_0 > offset_1), case
                assert tz.datetime_exists(dt) == (offset_0 >= offset_1), case


@pytest.mark.skipif(not HAS_ZONEINFO, reason="Requires zoneinfo (Python 3.9+)")
def test_matches_zoneinfo(tz_source):
    """utcoffset, dst, tzname and fromutc agree with the stdlib zoneinfo."""
    # On Python 3.9+, dateutil and zoneinfo share TZPATH, and the tz_source
    # fixture blocks (or allows) tzdata for both of them.
    for key in _keys():
        zone = tz.gettz(key)
        reference = zoneinfo.ZoneInfo.no_cache(key)

        for dt_utc in _probe_instants(zone):
            dt = dt_utc.astimezone(zone)
            dt_ref = dt_utc.astimezone(reference)
            if (dt.replace(tzinfo=None), _fold(dt)) != (
                dt_ref.replace(tzinfo=None),
                dt_ref.fold,
            ):
                # zoneinfo gets some TZ strings wrong near the new year (e.g.
                # "0/0,J365/23" rules); only accept a difference where its
                # answer doesn't round trip and ours does.
                assert dt_ref.astimezone(UTC) != dt_utc, (key, dt_utc)
                assert dt.astimezone(UTC) == dt_utc, (key, dt_utc)

            wall = dt_utc.replace(tzinfo=None)
            for fold in (0, 1):
                dt = tz.enfold(wall.replace(tzinfo=zone), fold=fold)
                dt_ref = wall.replace(tzinfo=reference, fold=fold)
                if (dt.utcoffset(), dt.dst(), dt.tzname()) != (
                    dt_ref.utcoffset(),
                    dt_ref.dst(),
                    dt_ref.tzname(),
                ):
                    # As above: zoneinfo's offset has to be one that its own
                    # fromutc contradicts, and ours has to be one ours agrees
                    # with, so a difference in a real gap still fails.
                    case = (key, wall, fold)
                    ref_rt = dt_ref.astimezone(UTC).astimezone(reference)
                    our_rt = dt.astimezone(UTC).astimezone(zone)
                    assert ref_rt.replace(tzinfo=None) != wall, case
                    assert our_rt.replace(tzinfo=None) == wall, case


####
# dst() against the source data
#
# TZif files record the total UTC offset of each local time type and whether
# it is DST, but not how much of the offset is DST, so dst() is inferred from
# the neighboring transitions (see tzfile._utcoff_to_dstoff). The tzdata.zi
# file installed alongside the TZif files (by the tz Makefile, and in the
# tzdata package) has the standard offset for every period of every zone, so
# away from the boundaries between periods, utcoffset() - dst() has to be the
# standard offset from tzdata.zi.
#
# The inference gets it wrong for these zones, e.g. for British Double Summer
# Time in Europe/London (DST of 2 hours, not 1), for the half-hour DST in
# Pacific/Rarotonga, or when the standard offset changes at the same time as
# DST starts, as in America/Bahia_Banderas in 2010. The list covers the 2024a
# and 2025b releases and the master branch, in the main, vanguard and
# rearguard forms and as fat and slim files. Only new failures fail the test.
KNOWN_DST_INFERENCE_FAILURES = frozenset(
    [
        "Africa/Casablanca",
        "Africa/El_Aaiun",
        "America/Bahia_Banderas",
        "America/Coyhaique",
        "America/Indiana/Tell_City",
        "America/Inuvik",
        "America/Montevideo",
        "America/Punta_Arenas",
        "America/Santiago",
        "America/Scoresbysund",
        "Asia/Choibalsan",
        "Asia/Hong_Kong",
        "Asia/Ust-Nera",
        "Atlantic/Azores",
        "Atlantic/Madeira",
        "Europe/Berlin",
        "Europe/Gibraltar",
        "Europe/Kyiv",
        "Europe/Lisbon",
        "Europe/London",
        "Europe/Madrid",
        "Europe/Minsk",
        "Europe/Moscow",
        "Europe/Paris",
        "Europe/Riga",
        "Europe/Simferopol",
        "Europe/Tallinn",
        "Europe/Vilnius",
        "Pacific/Rarotonga",
    ]
)

_ZI_MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)
_ZI_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

# How far from a boundary between two periods of a zone (whose exact time
# depends on rules that aren't evaluated here) a sample has to be.
_ZI_BOUNDARY_MARGIN = 2 * 86400


def _zi_lookup(abbr, names):
    # tzdata.zi uses the shortest unambiguous abbreviations, e.g. "Ja", "Au"
    matches = [i for i, name in enumerate(names) if name.startswith(abbr)]
    assert len(matches) == 1, abbr
    return matches[0]


def _zi_seconds(value):
    sign = -1 if value.startswith("-") else 1
    parts = [int(part) for part in value.lstrip("-").split(":")] + [0, 0]
    return sign * (parts[0] * 3600 + parts[1] * 60 + parts[2])


def _zi_until(fields):
    """The approximate UTC timestamp of an UNTIL column."""
    year = int(fields[0])
    month = _zi_lookup(fields[1], _ZI_MONTHS) + 1 if len(fields) > 1 else 1
    day = 1
    if len(fields) > 2:
        day_spec = fields[2]
        days_in_month = calendar.monthrange(year, month)[1]
        if day_spec.startswith("last"):
            weekday = _zi_lookup(day_spec[4:], _ZI_WEEKDAYS)
            day = max(
                d
                for d in range(1, days_in_month + 1)
                if calendar.weekday(year, month, d) == weekday
            )
        elif ">=" in day_spec or "<=" in day_spec:
            op = ">=" if ">=" in day_spec else "<="
            name, first = day_spec.split(op)
            weekday = _zi_lookup(name, _ZI_WEEKDAYS)
            step = 1 if op == ">=" else -1
            day = int(first)
            while calendar.weekday(year, month, day) != weekday:
                day += step
        else:
            day = int(day_spec)

    seconds = _zi_seconds(fields[3].rstrip("wsugz")) if len(fields) > 3 else 0
    days = (datetime(year, month, 1) - datetime(1970, 1, 1)).days + day - 1
    return days * 86400 + seconds


def _parse_tzdata_zi(path):
    """Returns ({zone: [(stdoff, until), ...]}, {link: target})."""
    zones = {}
    links = {}
    periods = None
    with open(path) as f:
        for line in f:
            fields = line.split("#", 1)[0].split()
            if not fields:
                continue

            if fields[0] == "Z":
                periods = zones.setdefault(fields[1], [])
                fields = fields[2:]
            elif fields[0] in ("R", "L"):
                if fields[0] == "L":
                    links[fields[2]] = fields[1]
                periods = None
                continue

            # A zone line (without "Z <name>") or a continuation line:
            # STDOFF RULES FORMAT [UNTIL]
            until = _zi_until(fields[3:]) if len(fields) > 3 else None
            periods.append((_zi_seconds(fields[0]), until))

    return zones, links


def _find_tzdata_zi(tz_source):
    if tz_source == "tzdata":
        import tzdata

        candidates = [
            os.path.join(os.path.dirname(tzdata.__file__), "zoneinfo")
        ]
    else:
        candidates = tz.TZPATH

    for directory in candidates:
        path = os.path.join(directory, "tzdata.zi")
        if os.path.exists(path):
            return path

    return None


@pytest.mark.skipif(
    sys.version_info < (3, 6),
    reason="Sub-minute offsets are rounded before Python 3.6",
)
def test_dst_matches_tzdata_zi(tz_source):
    """utcoffset() - dst() is the standard offset given in tzdata.zi."""
    path = _find_tzdata_zi(tz_source)
    if path is None:
        pytest.skip("No tzdata.zi alongside the TZif files")

    zones, links = _parse_tzdata_zi(path)

    failures = {}
    for key in _keys():
        name = key
        while name in links:
            name = links[name]

        periods = zones.get(name)
        if periods is None:
            continue

        boundaries = [until for _, until in periods if until is not None]
        zone = tz.gettz(key)

        # Samples in the middle of the stretches between transitions, which
        # are where the answer is least ambiguous.
        transitions = list(zone._trans_utc)
        samples = [(a + b) // 2 for a, b in zip(transitions, transitions[1:])]
        samples += [
            int((instant - EPOCH).total_seconds()) for instant in FIXED_INSTANTS
        ]

        for ts in samples:
            if any(abs(ts - b) < _ZI_BOUNDARY_MARGIN for b in boundaries):
                continue

            dt_utc = _from_timestamp(ts)
            if dt_utc is None:
                continue

            stdoff = next(
                stdoff
                for stdoff, until in periods
                if until is None or ts < until
            )

            dt = dt_utc.astimezone(zone)
            std = dt.utcoffset() - dt.dst()
            if std.days * 86400 + std.seconds != stdoff:
                failures.setdefault(name, []).append(dt)

    unexpected = {
        name: dts[:3]
        for name, dts in failures.items()
        if name not in KNOWN_DST_INFERENCE_FAILURES
    }
    assert not unexpected
