from datetime import datetime

import pytest

from dateutil import tz
from dateutil.parser import parse, parser


@pytest.mark.parametrize(
    "parse_func", [parse, parser().parse], ids=["function", "instance"]
)
@pytest.mark.parametrize(
    "default_tz",
    [None, tz.tzoffset("default", -18000)],
    ids=["naive-default", "aware-default"],
)
@pytest.mark.parametrize(
    "dstr,expected",
    [
        ("2018-12-20 14:30:00 +0400", datetime(2018, 12, 20, 14, 30)),
        ("2018-12-20 14:30:00", datetime(2018, 12, 20, 14, 30)),
        ("14:30", datetime(2003, 9, 25, 14, 30, 17, 123456)),
    ],
)
@pytest.mark.parametrize("ignoretz", [True, False])
@pytest.mark.parametrize("fuzzy_with_tokens", [False, True])
def test_parse_ignoretz_default(
    parse_func, default_tz, dstr, expected, ignoretz, fuzzy_with_tokens
):
    default = datetime(2003, 9, 25, 8, 9, 17, 123456, tzinfo=default_tz)
    original = default.replace()
    kwargs = dict(
        default=default, ignoretz=ignoretz, fuzzy_with_tokens=fuzzy_with_tokens
    )
    expected_tz = None if ignoretz else default_tz
    if not ignoretz and dstr.endswith("+0400"):
        expected_tz = tz.tzoffset(None, 14400)
    expected = expected.replace(tzinfo=expected_tz)
    text = "Today is " + dstr if fuzzy_with_tokens else dstr
    result = parse_func(text, **kwargs)
    if fuzzy_with_tokens:
        result, tokens = result
        expected_tokens = ("Today is ",) + (
            (" ", " ")
            if dstr.endswith("+0400")
            else (" ",) if dstr != "14:30" else ()
        )
        assert tokens == expected_tokens
    assert result == expected
    if expected_tz is None:
        assert result.tzinfo is None
    elif not dstr.endswith("+0400"):
        assert result.tzinfo is default_tz
    assert default == original
    assert default.tzinfo is original.tzinfo


@pytest.mark.parametrize(
    "parse_func", [parse, parser().parse], ids=["function", "instance"]
)
@pytest.mark.parametrize(
    "dstr", ["2018-12-20 14:30:00 +0400", "2018-12-20 14:30:00"]
)
def test_parse_ignoretz_default_ignores_tzinfos(parse_func, dstr):
    def tzinfos(*args):
        pytest.fail("tzinfos must not be called when ignoretz=True")

    default = datetime(2000, 1, 1, tzinfo=tz.UTC)
    result = parse_func(dstr, default=default, ignoretz=True, tzinfos=tzinfos)
    assert result == datetime(2018, 12, 20, 14, 30)
    assert result.tzinfo is None
    assert default.tzinfo is tz.UTC
