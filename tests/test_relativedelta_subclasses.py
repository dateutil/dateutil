from datetime import date, datetime, timedelta, timezone

import pytest

from dateutil.relativedelta import relativedelta

HELPERS = ("_add_relativedelta", "_get_replacement", "_apply_relative")
FORMS = (
    "direct-method",
    "direct-property",
    "before-method",
    "before-property",
    "after-method",
    "after-property",
    "instance-string",
    "instance-callable",
)


def application_method(self):
    return "application value"


def application_callable():
    return "application value"


def make_delta(helper, form, **kwargs):
    reads = []

    def application_property(self):
        reads.append(helper)
        return "application value"

    attribute = (
        property(application_property)
        if form.endswith("property")
        else application_method
    )
    mixin = type("ApplicationMixin", (), {helper: attribute})
    bases = {
        "direct": (relativedelta,),
        "before": (mixin, relativedelta),
        "after": (relativedelta, mixin),
        "instance": (relativedelta,),
    }[form.split("-")[0]]
    namespace = {helper: attribute} if form.startswith("direct") else {}
    delta = type("ApplicationDelta", bases, namespace)(**kwargs)
    if form.startswith("instance"):
        value = (
            application_callable
            if form.endswith("callable")
            else "application value"
        )
        setattr(delta, helper, value)
    return delta, reads


@pytest.mark.parametrize("helper", HELPERS)
@pytest.mark.parametrize("form", FORMS)
def test_application_lookup(helper, form):
    delta, reads = make_delta(helper, form, days=1)
    before = vars(delta).copy()
    value = getattr(delta, helper)
    if form.endswith(("method", "callable")):
        assert callable(value)
        value = value()
    assert type(value) is str
    assert value == "application value"
    assert reads == ([helper] if form.endswith("property") else [])
    assert vars(delta) == before


def add_date(delta):
    return date(2024, 6, 15) + delta


def add_datetime(delta):
    return delta + datetime(2024, 6, 15, 12, 34, 56, 789)


ZONE = timezone(timedelta(hours=4))
AWARE = datetime(2024, 6, 15, 12, 34, 56, 789, tzinfo=ZONE, fold=1)


def subtract_aware(delta):
    return AWARE - delta


@pytest.mark.parametrize("helper", HELPERS[1:])
@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize(
    "operation, expected",
    (
        (add_date, date(2024, 6, 16)),
        (add_datetime, datetime(2024, 6, 16, 12, 34, 56, 789)),
        (
            subtract_aware,
            datetime(2024, 6, 14, 12, 34, 56, 789, tzinfo=ZONE, fold=0),
        ),
    ),
    ids=("date-add", "datetime-add", "aware-subtract"),
)
def test_date_arithmetic(helper, form, operation, expected):
    delta, reads = make_delta(helper, form, days=1)
    before = vars(delta).copy()
    result = operation(delta)
    assert result == expected
    assert type(result) is type(expected)
    assert vars(delta) == before
    assert reads == []
    assert AWARE.fold == 1
    assert AWARE.tzinfo is ZONE
    if operation is subtract_aware:
        assert result.tzinfo is ZONE
        assert result.fold == 0


def assert_delta(result, expected, expected_type):
    assert type(result) is expected_type
    assert vars(result) == vars(expected)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize(
    "same_subclass", (False, True), ids=("ordinary", "same")
)
def test_composition(form, same_subclass):
    left, reads = make_delta(
        "_add_relativedelta", form, months=1, days=2, year=2020, month=3
    )
    right_type = type(left) if same_subclass else relativedelta
    right = right_type(months=2, days=3, year=2021, day=7)
    before = vars(left).copy(), vars(right).copy()
    result = left + right
    assert_delta(
        result,
        relativedelta(months=3, days=5, year=2021, month=3, day=7),
        type(left),
    )
    assert (vars(left), vars(right)) == before
    assert reads == []


@pytest.mark.parametrize("helper", HELPERS)
@pytest.mark.parametrize("form", FORMS)
def test_base_left_composition(helper, form):
    right, reads = make_delta(helper, form, months=2, days=3, year=2021, day=7)
    left = relativedelta(months=1, days=2, year=2020, month=3)
    before = vars(left).copy(), vars(right).copy()
    assert_delta(
        left + right,
        relativedelta(months=3, days=5, year=2021, month=3, day=7),
        relativedelta,
    )
    assert (vars(left), vars(right)) == before
    assert reads == []


def add_timedelta(delta, value):
    return delta + value


def reflected_timedelta(delta, value):
    return value + delta


@pytest.mark.parametrize("helper", HELPERS)
@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("operation", (add_timedelta, reflected_timedelta))
def test_timedelta(helper, form, operation):
    delta, reads = make_delta(helper, form, months=1, days=2, year=2020)
    value = timedelta(days=3, seconds=4, microseconds=5)
    before = vars(delta).copy()
    assert_delta(
        operation(delta, value),
        relativedelta(months=1, days=5, seconds=4, microseconds=5, year=2020),
        type(delta),
    )
    assert vars(delta) == before
    assert value == timedelta(days=3, seconds=4, microseconds=5)
    assert reads == []


@pytest.mark.parametrize("helper", HELPERS)
@pytest.mark.parametrize("form", FORMS)
def test_delta_subtraction(helper, form):
    left, reads = make_delta(helper, form, months=1, days=2, year=2020, month=3)
    right = relativedelta(months=2, days=3, year=2021, day=7)
    before = vars(left).copy(), vars(right).copy()
    assert_delta(
        left - right,
        relativedelta(months=-1, days=-1, year=2020, month=3, day=7),
        type(left),
    )
    assert (vars(left), vars(right)) == before
    assert reads == []


class PlainDelta(relativedelta):
    pass


def test_negation():
    delta = PlainDelta(months=1, days=2, year=2020)
    before = vars(delta).copy()
    assert_delta(
        -delta, relativedelta(months=-1, days=-2, year=2020), PlainDelta
    )
    assert vars(delta) == before


def test_normalization():
    delta = PlainDelta(days=1.5, hours=2, year=2020)
    before = vars(delta).copy()
    assert_delta(
        delta.normalized(),
        relativedelta(days=1, hours=14, year=2020),
        PlainDelta,
    )
    assert vars(delta) == before


class PublicAddDelta(relativedelta):
    def __add__(self, other):
        return "public addition"


@pytest.mark.parametrize("operation", (add_date, subtract_aware))
def test_public_add_override(operation):
    delta = PublicAddDelta(days=1)
    before = vars(delta).copy()
    assert operation(delta) == "public addition"
    assert vars(delta) == before


class PublicReflectedDelta(relativedelta):
    def __radd__(self, other):
        return "public reflected addition"


def test_public_reflected_override():
    left = relativedelta(days=1)
    right = PublicReflectedDelta(days=2)
    before = vars(left).copy(), vars(right).copy()
    assert left + right == "public reflected addition"
    assert (vars(left), vars(right)) == before


class ReflectedOperand:
    def __radd__(self, other):
        return "operand reflected addition"


def test_unsupported_reflected_operand():
    delta = PlainDelta(days=1)
    before = vars(delta).copy()
    assert delta + ReflectedOperand() == "operand reflected addition"
    assert vars(delta) == before


def test_unsupported_operand():
    delta = PlainDelta(days=1)
    before = vars(delta).copy()
    assert delta.__add__(object()) is NotImplemented
    with pytest.raises(TypeError):
        delta + object()
    assert vars(delta) == before


def test_unsupported_subtraction():
    delta = PlainDelta(days=1)
    before = vars(delta).copy()
    assert delta.__sub__(object()) is NotImplemented
    with pytest.raises(TypeError):
        delta - object()
    assert vars(delta) == before


class ApplicationMixin:
    def _get_replacement(self):
        return self._application_year

    @property
    def year(self):
        return self._get_replacement()

    @year.setter
    def year(self, value):
        self._application_year = value


class ApplicationDelta(relativedelta, ApplicationMixin):
    pass


class ReverseApplicationDelta(ApplicationMixin, relativedelta):
    pass


@pytest.mark.parametrize(
    "delta_type", (ApplicationDelta, ReverseApplicationDelta)
)
def test_application_year_property(delta_type):
    delta = delta_type(days=1)
    assert delta.year is None
    before = vars(delta).copy()
    result = date(2024, 6, 15) + delta
    assert result == date(2024, 6, 16)
    assert type(result) is date
    assert vars(delta) == before
    delta.year = 2020
    assert delta.year == 2020
    before = vars(delta).copy()
    result = date(2024, 6, 15) + delta
    assert result == date(2020, 6, 16)
    assert type(result) is date
    assert vars(delta) == before
