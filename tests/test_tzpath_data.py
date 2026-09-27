"""Properties that must hold for any valid IANA time zone data.

Unlike the tests in ``test_tzfile.py``, which pin the data they use so that
they can check specific historical transitions, these run against every key
in whatever data is installed: the data on TZPATH (with tzdata blocked) and
the tzdata package, via the ``tz_source`` fixture. In the ``tz`` CI jobs
that is the master branch of the tz database, so these are the tests that
catch the parser mishandling something new in the data.
"""

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


# In slim builds, America/Nuuk's last explicit transition (2023-10-29 01:00
# UTC, from -02 DST to -02 standard) is followed by a TZ string whose own DST
# period for 2023 runs until 00:00 local time on 2023-10-29. For wall times in
# the hour between those two, utcoffset() uses the TZ string (-01) while
# fromutc() uses the explicit transition (-02), so datetime_exists() says
# they don't exist. CPython's zoneinfo behaves the same way.
KNOWN_FOOTER_SEAMS = {
    "America/Godthab": (datetime(2023, 10, 28, 23), datetime(2023, 10, 29)),
    "America/Nuuk": (datetime(2023, 10, 28, 23), datetime(2023, 10, 29)),
}


def _in_known_seam(key, wall):
    start, end = KNOWN_FOOTER_SEAMS.get(key, (None, None))
    return start is not None and start <= wall < end


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
                if _in_known_seam(key, wall):
                    continue

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
            assert (dt.replace(tzinfo=None), _fold(dt)) == (
                dt_ref.replace(tzinfo=None),
                dt_ref.fold,
            ), (key, dt_utc)

            wall = dt_utc.replace(tzinfo=None)
            for fold in (0, 1):
                dt = tz.enfold(wall.replace(tzinfo=zone), fold=fold)
                dt_ref = wall.replace(tzinfo=reference, fold=fold)
                assert (dt.utcoffset(), dt.dst(), dt.tzname()) == (
                    dt_ref.utcoffset(),
                    dt_ref.dst(),
                    dt_ref.tzname(),
                ), (key, wall, fold)
