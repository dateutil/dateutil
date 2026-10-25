import calendar
from datetime import date, datetime, timedelta, timezone

import pytest

from dateutil.relativedelta import MO, relativedelta

ORDERS = ("before", "after")
PATHS = ("date", "naive", "aware")
ZONE = timezone(timedelta(hours=4))
AWARE = datetime(2024, 6, 15, 12, 34, 56, 789, tzinfo=ZONE, fold=1)
EXPECTED = {
    "year": (
        date(2020, 6, 15),
        datetime(2020, 6, 15, 12, 34, 56, 789),
        datetime(2020, 6, 15, 12, 34, 56, 789, tzinfo=ZONE),
    ),
    "month": (
        date(2024, 2, 15),
        datetime(2024, 2, 15, 12, 34, 56, 789),
        datetime(2024, 2, 15, 12, 34, 56, 789, tzinfo=ZONE),
    ),
    "day": (
        date(2024, 6, 7),
        datetime(2024, 6, 7, 12, 34, 56, 789),
        datetime(2024, 6, 7, 12, 34, 56, 789, tzinfo=ZONE),
    ),
    None: (
        date(2024, 6, 15),
        datetime(2024, 6, 15, 12, 34, 56, 789),
        datetime(2024, 6, 15, 12, 34, 56, 789, tzinfo=ZONE),
    ),
}
FIELDS = (("year", 2020), ("month", 2), ("day", 7))


def mixin_delta(mixin, order, **kwargs):
    bases = {
        "before": (mixin, relativedelta),
        "after": (relativedelta, mixin),
    }[order]
    return type("DescriptorDelta", bases, {})(**kwargs)


def scripted_delta(field, order, first, second, fail_second=False, **kwargs):
    state = {"armed": False, "reads": 0, "stored": None}

    def get_field(self):
        if not state["armed"]:
            return state["stored"]
        state["reads"] += 1
        if state["reads"] == 2 and fail_second:
            raise RuntimeError("second descriptor read")
        return (first, second)[min(state["reads"] - 1, 1)]

    def set_field(self, value):
        state["stored"] = value

    mixin = type("FieldMixin", (), {field: property(get_field, set_field)})
    delta = mixin_delta(mixin, order, **kwargs)
    state.update(armed=True, reads=0)
    return delta, state


def apply_delta(delta, path):
    if path == "date":
        return date(2024, 6, 15) + delta
    if path == "naive":
        return delta + datetime(2024, 6, 15, 12, 34, 56, 789)
    return AWARE + delta


def assert_result(result, expected, path):
    assert result == expected
    assert type(result) is type(expected)
    if path == "aware":
        assert result.tzinfo is ZONE
        assert result.fold == 0
        assert AWARE.tzinfo is ZONE
        assert AWARE.fold == 1
        assert AWARE == datetime(
            2024, 6, 15, 12, 34, 56, 789, tzinfo=ZONE, fold=1
        )


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("field, first", FIELDS)
def test_changing_descriptor(order, path, field, first):
    delta, state = scripted_delta(field, order, first, first + 1)
    result = apply_delta(delta, path)
    reads = state["reads"]
    assert_result(result, EXPECTED[field][PATHS.index(path)], path)
    assert reads == 1


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("field, second", FIELDS)
def test_none_descriptor(order, path, field, second):
    delta, state = scripted_delta(field, order, None, second)
    result = apply_delta(delta, path)
    reads = state["reads"]
    assert_result(result, EXPECTED[None][PATHS.index(path)], path)
    assert reads == 1


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("field, first", FIELDS)
def test_second_read_error(order, field, first):
    delta, state = scripted_delta(field, order, first, first, fail_second=True)
    result = date(2024, 6, 15) + delta
    reads = state["reads"]
    assert_result(result, EXPECTED[field][0], "date")
    assert reads == 1


@pytest.mark.parametrize("order", ORDERS)
def test_invalid_month_precedes_day(order):
    delta, state = scripted_delta("day", order, 7, 8, month=13)
    with pytest.raises(calendar.IllegalMonthError):
        date(2024, 6, 15) + delta
    reads = state["reads"]
    assert reads == 0


@pytest.mark.parametrize("order", ORDERS)
def test_public_field_order(order):
    fields = (
        "year",
        "years",
        "month",
        "months",
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
        "days",
        "leapdays",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "weekday",
    )
    state = {"armed": False, "reads": []}

    class TraceMixin:
        def __getattribute__(self, name):
            if state["armed"] and name in fields:
                state["reads"].append(name)
            return super().__getattribute__(name)

    delta = mixin_delta(TraceMixin, order, months=1, leapdays=1, weekday=MO(1))
    state.update(armed=True, reads=[])
    result = date(2024, 2, 29) + delta
    reads = tuple(state["reads"])
    assert result == date(2024, 4, 1)
    assert type(result) is date
    assert reads == (
        "year",
        "years",
        "month",
        "months",
        "months",
        "months",
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
        "days",
        "leapdays",
        "leapdays",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "weekday",
        "weekday",
        "weekday",
    )


@pytest.mark.parametrize("order", ORDERS)
def test_composition_retains_two_reads(order):
    class LeftDelta(relativedelta):
        pass

    left = LeftDelta(months=1)
    right, state = scripted_delta("year", order, 2020, 2021)
    result = left + right
    reads = state["reads"]
    assert reads == 2
    assert type(result) is LeftDelta
    assert result.year == 2021
    assert result.months == 1
