import calendar
from datetime import date, datetime, timedelta, timezone

import pytest

from dateutil.relativedelta import relativedelta

ORDERS = ("before", "after")
FIELDS = (("year", 2020, 2021), ("month", 2, 3), ("day", 7, 8))
PATHS = ("date", "naive", "aware")
ZONE = timezone(timedelta(hours=4))
INPUTS = {
    "date": date(2024, 6, 15),
    "naive": datetime(2024, 6, 15, 12, 34, 56, 789),
    "aware": datetime(2024, 6, 15, 12, 34, 56, 789, tzinfo=ZONE, fold=1),
}
UNCHANGED = {
    "date": date(2024, 6, 15),
    "naive": datetime(2024, 6, 15, 12, 34, 56, 789),
    "aware": datetime(2024, 6, 15, 12, 34, 56, 789, tzinfo=ZONE),
}
SELECTED = {
    "year": date(2020, 6, 15),
    "month": date(2024, 2, 15),
    "day": date(2024, 6, 7),
}
PUBLIC_FIELDS = (
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
APPLICATION_TRACES = {
    "year": (
        "year",
        ("bool", "year"),
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
    ),
    "month": (
        "year",
        "years",
        "month",
        ("bool", "month"),
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
    ),
    "day": (
        "year",
        "years",
        "month",
        "months",
        "day",
        ("bool", "day"),
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
    ),
}
RAISING_TRACES = {
    "year": ("year", ("bool", "year")),
    "month": ("year", "years", "month", ("bool", "month")),
    "day": ("year", "years", "month", "months", "day", ("bool", "day")),
}
TRUTHY_MONTH_TRACE = (
    "year",
    "years",
    "month",
    ("bool", "month"),
    "months",
    ("eq", "month", 2),
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
COMPOSITION_TRACES = {
    "year": (
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "year",
        "month",
        "day",
        "weekday",
        "hour",
        "minute",
        "second",
        "microsecond",
    ),
    "month": (
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "month",
        "month",
        "day",
        "weekday",
        "hour",
        "minute",
        "second",
        "microsecond",
    ),
    "day": (
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "month",
        "day",
        "day",
        "weekday",
        "hour",
        "minute",
        "second",
        "microsecond",
    ),
}
EQUALITY_TRACES = {
    "year": (
        "weekday",
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        ("eq", "year", 2020),
        "month",
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
    ),
    "month": (
        "weekday",
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "month",
        ("eq", "month", 2),
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
    ),
    "day": (
        "weekday",
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "month",
        "day",
        ("eq", "day", 7),
        "hour",
        "minute",
        "second",
        "microsecond",
    ),
}
DELTA_BOOL_TRACES = {
    "year": (
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
    ),
    "month": (
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "month",
    ),
    "day": (
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "month",
        "day",
    ),
}


class ObservedInt(int):
    def __new__(cls, value, state, label, behavior):
        instance = super().__new__(cls, value)
        instance.state = state
        instance.label = label
        instance.behavior = behavior
        return instance

    def __bool__(self):
        if not self.state["armed"]:
            return True
        self.state["events"].append(("bool", self.label))
        if self.behavior == "raising":
            raise self.state["error"]
        return self.behavior == "truthy"

    def __eq__(self, other):
        if self.state["armed"]:
            self.state["events"].append(("eq", self.label, other))
        return int.__eq__(self, other)


class LeftDelta(relativedelta):
    pass


def new_state():
    return {
        "armed": False,
        "events": [],
        "reads": {},
        "stored": {},
        "error": RuntimeError("scalar truthiness"),
    }


def field_property(field, values, state, fail_getter=False):
    def get_field(self):
        if not state["armed"]:
            return state["stored"][field]
        state["reads"][field] = state["reads"].get(field, 0) + 1
        if fail_getter:
            raise state["error"]
        return values[min(state["reads"][field] - 1, 1)]

    def set_field(self, value):
        state["stored"][field] = value

    return property(get_field, set_field)


def make_delta(order, state, properties, **kwargs):
    class TraceMixin:
        def __getattribute__(self, name):
            if state["armed"] and name in PUBLIC_FIELDS:
                state["events"].append(name)
            return super().__getattribute__(name)

    mixin = type("PropertyMixin", (TraceMixin,), properties)
    bases = {"before": (mixin, relativedelta), "after": (relativedelta, mixin)}[
        order
    ]
    return type("TruthinessDelta", bases, {})(**kwargs)


def observed_delta(order, field, value, behavior, second=None, **kwargs):
    state = new_state()
    first = ObservedInt(value, state, field, behavior)
    last = (
        first if second is None else ObservedInt(second, state, field, behavior)
    )
    prop = field_property(field, (first, last), state)
    delta = make_delta(order, state, {field: prop}, **{field: first, **kwargs})
    return delta, state, first, last


def arm(state):
    state.update(armed=True, events=[], reads={})


def capture(state):
    events, reads = tuple(state["events"]), dict(state["reads"])
    state["armed"] = False
    return events, reads


def apply_delta(delta, path):
    if path == "naive":
        return delta + INPUTS[path]
    return INPUTS[path] + delta


def assert_input(path):
    assert INPUTS[path] == UNCHANGED[path]
    assert type(INPUTS[path]) is type(UNCHANGED[path])
    if path == "aware":
        assert INPUTS[path].tzinfo is ZONE
        assert INPUTS[path].fold == 1


def assert_result(result, expected, path):
    assert result == expected
    assert type(result) is type(expected)
    if path != "date":
        assert result.fold == 0
    if path == "aware":
        assert result.tzinfo is ZONE
    assert_input(path)


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("field, value, second", FIELDS)
def test_false_nonzero_application(order, path, field, value, second):
    delta, state, first, _ = observed_delta(order, field, value, "false")
    before = vars(delta).copy()
    arm(state)
    result = apply_delta(delta, path)
    events, reads = capture(state)
    assert_result(result, UNCHANGED[path], path)
    assert events == APPLICATION_TRACES[field]
    assert reads == {field: 1}
    assert vars(delta) == before
    assert getattr(delta, field) is first


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("field, value, second", FIELDS)
def test_raising_truthiness(order, path, field, value, second):
    delta, state, first, _ = observed_delta(order, field, value, "raising")
    before = vars(delta).copy()
    arm(state)
    with pytest.raises(RuntimeError) as caught:
        apply_delta(delta, path)
    events, reads = capture(state)
    assert caught.value is state["error"]
    assert events == RAISING_TRACES[field]
    assert reads == {field: 1}
    assert vars(delta) == before
    assert getattr(delta, field) is first
    assert_input(path)


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("field, value, second", FIELDS)
def test_observable_truthy_application(order, field, value, second):
    delta, state, first, _ = observed_delta(order, field, value, "truthy")
    before = vars(delta).copy()
    arm(state)
    result = date(2024, 6, 15) + delta
    events, reads = capture(state)
    expected = {
        "year": APPLICATION_TRACES["year"],
        "month": TRUTHY_MONTH_TRACE,
        "day": APPLICATION_TRACES["day"],
    }
    assert_result(result, SELECTED[field], "date")
    assert events == expected[field]
    assert reads == {field: 1}
    assert vars(delta) == before
    assert getattr(delta, field) is first


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("behavior", ("false", "raising"))
@pytest.mark.parametrize("field, value, second", FIELDS)
def test_composition_preserves_second_value(
    order, behavior, field, value, second
):
    right, state, first, last = observed_delta(
        order, field, value, behavior, second
    )
    left = LeftDelta(months=1)
    left_before, right_before = vars(left).copy(), vars(right).copy()
    arm(state)
    result = left + right
    events, reads = capture(state)
    assert events == COMPOSITION_TRACES[field]
    assert reads == {field: 2}
    assert type(result) is LeftDelta
    assert getattr(result, field) is last
    assert result.months == 1
    assert vars(left) == left_before
    assert vars(right) == right_before
    assert getattr(right, field) is first


@pytest.mark.parametrize("order", ORDERS)
def test_mixed_zero_composition(order):
    state = new_state()
    day = ObservedInt(0, state, "day", "raising")
    values = {"year": False, "month": 0.0, "day": day}
    properties = {
        field: field_property(field, (value, value), state)
        for field, value in values.items()
    }
    right = make_delta(order, state, properties, **values)
    left = LeftDelta(year=2020, month=2, day=7)
    left_before, right_before = vars(left).copy(), vars(right).copy()
    arm(state)
    result = left + right
    events, reads = capture(state)
    assert events == (
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "leapdays",
        "year",
        "year",
        "month",
        "month",
        "day",
        "day",
        "weekday",
        "hour",
        "minute",
        "second",
        "microsecond",
    )
    assert reads == {"year": 2, "month": 2, "day": 2}
    assert type(result) is LeftDelta
    assert result.year is False
    assert result.month is values["month"]
    assert result.day is day
    assert vars(left) == left_before
    assert vars(right) == right_before


@pytest.mark.parametrize("order", ORDERS)
def test_invalid_month_precedes_raising_day(order):
    state = new_state()
    day = ObservedInt(7, state, "day", "raising")
    prop = field_property("day", (day, day), state, fail_getter=True)
    delta = make_delta(order, state, {"day": prop}, month=13, day=day)
    arm(state)
    with pytest.raises(calendar.IllegalMonthError) as caught:
        date(2024, 6, 15) + delta
    events, reads = capture(state)
    assert caught.value.month == 13
    assert events == ("year", "years", "month", "months")
    assert reads == {}
    assert delta.day is day


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("behavior", ("false", "raising"))
def test_absolute_hour_does_not_test_scalar_truthiness(order, behavior):
    delta, state, first, _ = observed_delta(order, "hour", 7, behavior)
    arm(state)
    result = date(2024, 6, 15) + delta
    events, reads = capture(state)
    assert_result(result, datetime(2024, 6, 15, 7), "naive")
    assert events == PUBLIC_FIELDS
    assert reads == {"hour": 1}
    assert delta.hour is first


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("behavior", ("false", "raising"))
def test_relative_leapdays_truthiness(order, behavior):
    delta, state, first, _ = observed_delta(order, "leapdays", 1, behavior)
    arm(state)
    if behavior == "raising":
        with pytest.raises(RuntimeError) as caught:
            date(2024, 6, 15) + delta
        events, reads = capture(state)
        assert caught.value is state["error"]
        assert events == (
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
            ("bool", "leapdays"),
        )
    else:
        result = date(2024, 6, 15) + delta
        events, reads = capture(state)
        assert_result(result, date(2024, 6, 15), "date")
        assert events == (
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
            ("bool", "leapdays"),
            "hours",
            "minutes",
            "seconds",
            "microseconds",
            "weekday",
        )
    assert reads == {"leapdays": 1}
    assert delta.leapdays is first


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize("field, value, second", FIELDS)
def test_delta_equality_and_truth_testing(order, field, value, second):
    delta, state, first, _ = observed_delta(order, field, value, "raising")
    other = relativedelta(**{field: value})
    arm(state)
    equal = delta == other
    equality_events, equality_reads = capture(state)
    arm(state)
    truth = bool(delta)
    bool_events, bool_reads = capture(state)
    assert equal is True
    assert equality_events == EQUALITY_TRACES[field]
    assert equality_reads == {field: 1}
    assert truth is True
    assert bool_events == DELTA_BOOL_TRACES[field]
    assert bool_reads == {field: 1}
    assert getattr(delta, field) is first


@pytest.mark.parametrize("order", ORDERS)
def test_application_owned_helper_name(order):
    state = new_state()

    def application_helper(self):
        state["events"].append("application helper")
        return 2020

    def get_year(self):
        return self._use_absolute_value()

    def set_year(self, value):
        state["stored"]["year"] = value

    properties = {
        "year": property(get_year, set_year),
        "_use_absolute_value": application_helper,
    }
    delta = make_delta(order, state, properties)
    arm(state)
    result = date(2024, 6, 15) + delta
    events, reads = capture(state)
    assert_result(result, date(2020, 6, 15), "date")
    assert events == (
        "year",
        "application helper",
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
    assert reads == {}
