import operator
from datetime import date, datetime, timedelta, timezone

import pytest

from dateutil.relativedelta import MO, relativedelta


def _reverse_add(base, delta):
    return delta + base


OPERATIONS = [operator.add, _reverse_add, operator.sub]
BASES = [
    date(2024, 6, 15),
    datetime(2024, 6, 15, 12, 34, 56, 789),
    datetime(2024, 6, 15, 12, 34, 56, 789, tzinfo=timezone.utc),
]


@pytest.mark.parametrize("base", BASES)
@pytest.mark.parametrize("apply", OPERATIONS)
@pytest.mark.parametrize("field", ["year", "month", "day"])
def test_zero_absolute_date_field(base, apply, field):
    delta = relativedelta(**{field: 0})
    with pytest.raises(ValueError):
        apply(base, delta)


@pytest.mark.parametrize("apply", [operator.add, _reverse_add])
@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"year": 0, "years": 1}, date(1, 6, 15)),
        ({"month": 0, "months": 1}, date(2024, 1, 15)),
        ({"month": 0, "months": -1}, date(2023, 11, 15)),
        ({"year": -1, "years": 2}, date(1, 6, 15)),
        ({"month": -1, "months": 2}, date(2024, 1, 15)),
    ],
)
def test_absolute_selection_precedes_relative_arithmetic(
    apply, kwargs, expected
):
    assert apply(date(2024, 6, 15), relativedelta(**kwargs)) == expected


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"year": 0, "years": -1}, date(1, 6, 15)),
        ({"month": 0, "months": -1}, date(2024, 1, 15)),
        ({"month": 0, "months": 1}, date(2023, 11, 15)),
    ],
)
def test_subtraction_preserves_absolute_selection(kwargs, expected):
    assert date(2024, 6, 15) - relativedelta(**kwargs) == expected


@pytest.mark.parametrize("apply", OPERATIONS)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"day": 0, "days": 1},
        {"day": 0, "days": 1, "weekday": MO},
        {"day": -1, "days": 2},
    ],
)
def test_invalid_day_precedes_relative_days_and_weekday(apply, kwargs):
    delta = relativedelta(**kwargs)
    with pytest.raises(ValueError):
        apply(date(2024, 6, 15), delta)


@pytest.mark.parametrize("base", BASES)
@pytest.mark.parametrize("apply", OPERATIONS)
@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"year": None, "month": None, "day": None},
        {"years": 0, "months": 0, "days": 0},
    ],
)
def test_unspecified_and_zero_relative_fields(base, apply, kwargs):
    assert apply(base, relativedelta(**kwargs)) == base


@pytest.mark.parametrize(
    "field, expected",
    [
        ("hour", datetime(2024, 6, 15, 0, 34, 56, 789)),
        ("minute", datetime(2024, 6, 15, 12, 0, 56, 789)),
        ("second", datetime(2024, 6, 15, 12, 34, 0, 789)),
        ("microsecond", datetime(2024, 6, 15, 12, 34, 56)),
    ],
)
def test_zero_absolute_time_field(field, expected):
    assert BASES[1] + relativedelta(**{field: 0}) == expected


@pytest.mark.parametrize("field", ["hour", "minute", "second", "microsecond"])
def test_zero_absolute_time_promotes_date(field):
    actual = BASES[0] + relativedelta(**{field: 0})
    assert type(actual) is datetime
    assert actual == datetime(2024, 6, 15)


@pytest.mark.parametrize(
    "weekday, expected",
    [
        (0, date(2024, 6, 17)),
        (MO(2), date(2024, 6, 24)),
        (MO(-1), date(2024, 6, 10)),
        (MO(0), date(2024, 6, 17)),
    ],
)
def test_weekday_adjustment(weekday, expected):
    assert BASES[0] + relativedelta(weekday=weekday) == expected


@pytest.mark.parametrize(
    "base, kwargs, expected",
    [
        (date(2024, 1, 31), {"months": 1}, date(2024, 2, 29)),
        (date(2023, 1, 31), {"months": 1}, date(2023, 2, 28)),
        (date(2024, 3, 31), {"months": -1}, date(2024, 2, 29)),
        (date(2024, 1, 31), {"months": -1}, date(2023, 12, 31)),
        (date(2024, 12, 31), {"months": 1}, date(2025, 1, 31)),
        (date(2024, 6, 15), {"month": 2, "day": 31}, date(2024, 2, 29)),
        (date(2023, 6, 15), {"month": 2, "day": 31}, date(2023, 2, 28)),
        (date(2024, 2, 29), {"years": 1}, date(2025, 2, 28)),
        (date(2024, 3, 1), {"leapdays": 1}, date(2024, 3, 2)),
        (date(2023, 3, 1), {"leapdays": 1}, date(2023, 3, 1)),
        (date(2024, 2, 29), {"leapdays": 1}, date(2024, 2, 29)),
        (
            date(2024, 6, 15),
            {"year": 2020, "month": 2, "day": 29},
            date(2020, 2, 29),
        ),
    ],
)
def test_calendar_compatibility(base, kwargs, expected):
    assert base + relativedelta(**kwargs) == expected


@pytest.mark.parametrize(
    "kwargs",
    [
        {"year": -1},
        {"day": -1},
        {"month": 13},
        {"year": 10000},
    ],
)
def test_existing_invalid_absolute_fields(kwargs):
    delta = relativedelta(**kwargs)
    with pytest.raises(ValueError):
        BASES[0] + delta


@pytest.mark.parametrize("field", ["year", "month", "day"])
def test_zero_survives_delta_transformations(field):
    delta = relativedelta(**{field: 0})
    before = vars(delta).copy()
    transformed = [
        delta + relativedelta(days=1),
        relativedelta(days=1) + delta,
        delta - relativedelta(days=1),
        delta + timedelta(days=1),
        timedelta(days=1) + delta,
        -delta,
        delta.normalized(),
    ]
    for result in transformed:
        assert getattr(result, field) == 0
        with pytest.raises(ValueError):
            BASES[0] + result
    for base in BASES:
        with pytest.raises(ValueError):
            base + delta
    assert vars(delta) == before


@pytest.mark.parametrize("field", ["year", "month", "day"])
def test_right_absolute_field_wins_without_mutation(field):
    left = relativedelta(**{field: 0})
    right = relativedelta(**{field: 1})
    before_left, before_right = vars(left).copy(), vars(right).copy()
    assert getattr(left + right, field) == 1
    assert getattr(right + left, field) == 0
    assert getattr(left + relativedelta(), field) == 0
    assert vars(left) == before_left
    assert vars(right) == before_right


def test_yearday_overrides_absolute_day():
    assert BASES[0] + relativedelta(day=0, yearday=32) == date(2024, 2, 1)


@pytest.mark.parametrize("normalize", [False, True])
def test_fractional_relative_units(normalize):
    delta = relativedelta(days=1.5, hours=2, minutes=0.5, seconds=0.25)
    if normalize:
        delta = delta.normalized()
    assert BASES[1] + delta == datetime(2024, 6, 17, 2, 35, 26, 250789)


class DeltaSubclass(relativedelta):
    pass


class DateSubclass(date):
    pass


class DatetimeSubclass(datetime):
    pass


def test_delta_subclass_construction():
    delta = DeltaSubclass(months=1)
    assert type(delta + relativedelta(days=1)) is DeltaSubclass
    assert type(delta + timedelta(days=1)) is DeltaSubclass
    assert BASES[0] + delta == date(2024, 7, 15)


@pytest.mark.parametrize(
    "base, expected_type",
    [
        (DateSubclass(2024, 6, 15), DateSubclass),
        (DatetimeSubclass(2024, 6, 15, 12), DatetimeSubclass),
    ],
)
def test_date_subclass_preserved(base, expected_type):
    actual = base + relativedelta(months=1)
    assert type(actual) is expected_type
    assert actual.month == 7


def test_date_subclass_promotion():
    actual = DateSubclass(2024, 6, 15) + relativedelta(hour=0)
    assert type(actual) is datetime
    assert actual == datetime(2024, 6, 15)


def test_timezone_and_fold_compatibility():
    zone = timezone(timedelta(hours=4))
    base = datetime(2024, 6, 15, 12, tzinfo=zone, fold=1)
    actual = base + relativedelta(months=1)
    assert actual == datetime(2024, 7, 15, 12, tzinfo=zone)
    assert actual.tzinfo is zone
    assert actual.fold == 0


class ReflectedOperand:
    def __radd__(self, other):
        return "reflected addition"


def test_unsupported_operand_dispatch():
    delta = relativedelta()
    assert delta.__add__(object()) is NotImplemented
    assert delta + ReflectedOperand() == "reflected addition"
    with pytest.raises(TypeError):
        delta + object()


@pytest.mark.parametrize("field", ["year", "month", "day"])
def test_false_absolute_date_field(field):
    delta = relativedelta(**{field: False})
    assert getattr(delta, field) is False
    with pytest.raises(ValueError):
        BASES[0] + delta


@pytest.mark.parametrize(
    "field, error",
    [
        ("year", TypeError),
        ("month", ValueError),
        ("day", TypeError),
    ],
)
def test_float_zero_uses_existing_calendar_validation(field, error):
    delta = relativedelta(**{field: 0.0})
    assert type(getattr(delta, field)) is float
    with pytest.raises(error):
        BASES[0] + delta


def test_fractional_absolute_warning():
    with pytest.warns(DeprecationWarning):
        delta = relativedelta(day=1.5)
    with pytest.raises(TypeError):
        BASES[0] + delta
