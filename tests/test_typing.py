"""Checks annotated public contracts against their runtime behavior."""

from __future__ import annotations

import datetime
import importlib.resources
import io
from collections.abc import Sequence
from typing import Generic, TypeVar, assert_type

from dateutil import parser, relativedelta, rrule, tz, utils

_T = TypeVar("_T")


class ReadOnly(Generic[_T]):
    def __init__(self, data: _T) -> None:
        self.data = data

    def read(self) -> _T:
        return self.data


class CharacterStream:
    def __init__(self, data: str) -> None:
        self.stream = io.StringIO(data)

    def read(self, size: int, /) -> str:
        return self.stream.read(size)


class BinaryStream:
    def __init__(self, data: bytes) -> None:
        self.stream = io.BytesIO(data)

    def read(self, size: int = -1, /) -> bytes:
        return self.stream.read(size)


class Monday:
    weekday = 0
    n = None


class Offset:
    def total_seconds(self) -> float:
        return 5400


class TimezoneLookup:
    def get(self, key: str, /) -> datetime.tzinfo | None:
        return tz.UTC if key == "CSTM" else None

    def __contains__(self, key: object, /) -> bool:
        return key == "CSTM"


def test_parser_stream_and_fuzzy_overloads() -> None:
    expected = datetime.datetime(2024, 1, 1)
    parsed = parser.parse(CharacterStream("2024-01-01"))
    assert_type(parsed, datetime.datetime)
    assert parsed == expected

    fuzzy = parser.parse("on 2024-01-01", fuzzy_with_tokens=True)
    assert_type(fuzzy, tuple[datetime.datetime, tuple[str, ...]])
    assert fuzzy == (expected, ("on ",))

    flag: bool = bool(parsed)
    conditional = parser.parser().parse("2024-01-01", fuzzy_with_tokens=flag)
    assert_type(
        conditional,
        datetime.datetime | tuple[datetime.datetime, tuple[str, ...]],
    )
    assert conditional == (expected, ())


def test_parser_timezone_lookup_without_mapping_base() -> None:
    parsed = parser.parse("2024-01-01 00:00 CSTM", tzinfos=TimezoneLookup())
    assert parsed == datetime.datetime(2024, 1, 1, tzinfo=tz.UTC)


def test_iso_parser_minimal_streams_and_bytearray() -> None:
    expected = datetime.datetime(2024, 1, 1)
    assert_type(parser.isoparse(ReadOnly("2024-01-01")), datetime.datetime)
    assert parser.isoparse(ReadOnly(b"2024-01-01")) == expected
    assert parser.isoparse(bytearray(b"2024-01-01")) == expected
    assert parser.isoparse(ReadOnly(bytearray(b"2024-01-01"))) == expected
    assert_type(parser.isoparser().parse_isodate(b"2024-01-01"), datetime.date)
    assert_type(parser.isoparser().parse_isotime("12:00"), datetime.time)


def test_utilities_preserve_structural_operand_types() -> None:
    wall_time = datetime.time(12)
    aware_time = utils.default_tzinfo(wall_time, tz.UTC)
    assert_type(aware_time, datetime.time)
    assert aware_time == datetime.time(12, tzinfo=tz.UTC)
    assert utils.default_tzinfo(aware_time, None) is aware_time
    assert utils.within_delta(3, 4, 1)
    assert not utils.within_delta(3.0, 4.5, 1.0)
    assert utils.within_delta(
        datetime.date(2024, 1, 1),
        datetime.date(2024, 1, 2),
        datetime.timedelta(days=1),
    )


def test_relative_delta_fractional_units_and_structural_weekday() -> None:
    delta = relativedelta.relativedelta(days=1.5, weekday=Monday())
    scaled = delta * "2"
    assert_type(scaled, relativedelta.relativedelta)
    assert scaled.days == 3
    result = datetime.datetime(2024, 1, 1) + delta
    assert_type(result, datetime.datetime)
    assert result == datetime.datetime(2024, 1, 8, 12)
    promoted = datetime.date(2024, 1, 1) + relativedelta.relativedelta(hours=1)
    assert_type(promoted, datetime.date)
    assert promoted == datetime.datetime(2024, 1, 1, 1)


def test_recurrence_index_slice_and_iterable_inputs() -> None:
    start = datetime.datetime(2024, 1, 1)
    rule = rrule.rrule(
        rrule.WEEKLY,
        dtstart=start,
        byweekday=(day for day in (Monday(), 2)),
        count=3,
        cache=None,
    )
    assert_type(rule[0], datetime.datetime)
    occurrences = rule[:2]
    assert_type(occurrences, Sequence[datetime.datetime])
    assert occurrences == [start, datetime.datetime(2024, 1, 3)]
    assert_type(rule.count(), int)
    assert rule.count() == 3

    rules = rrule.rruleset()
    rules.rrule(iter(occurrences))
    rules.exrule((start,))
    assert list(rules) == [datetime.datetime(2024, 1, 3)]


def test_rrulestr_force_set_overloads() -> None:
    forced = rrule.rrulestr("FREQ=DAILY;COUNT=1", forceset=True)
    compatible = rrule.rrulestr("FREQ=DAILY;COUNT=1", compatible=True)
    assert_type(forced, rrule.rruleset)
    assert_type(compatible, rrule.rruleset)
    assert forced.count() == compatible.count() == 1


def test_timezone_structural_offsets_and_read_only_streams() -> None:
    fixed = tz.tzoffset("custom", Offset())
    assert_type(fixed, tz.tzoffset)
    assert_type(fixed.utcoffset(None), datetime.timedelta)
    assert fixed.utcoffset(None) == datetime.timedelta(seconds=5400)
    assert_type(tz.tzutc(), tz.tzutc)
    assert_type(tz.tzstr("EST5"), tz.tzstr)

    data = (
        importlib.resources.files("tzdata.zoneinfo")
        .joinpath("UTC")
        .read_bytes()
    )
    zone = tz.tzfile(BinaryStream(data), key="UTC")
    assert_type(zone, tz.tzfile)
    assert zone.key == "UTC"
    assert zone.utcoffset(datetime.datetime(2024, 1, 1)) == datetime.timedelta(
        0
    )
