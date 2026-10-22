from datetime import datetime

import pytest

from dateutil.parser import ParserError, parse
from dateutil.tz import tzoffset, tzutc


@pytest.mark.parametrize("dayfirst", [False, True])
@pytest.mark.parametrize("yearfirst", [False, True])
@pytest.mark.parametrize(
    "text, expected",
    [
        ("2009:03:29 12:30:23", datetime(2009, 3, 29, 12, 30, 23)),
        ("2009:03:04 12:30:23", datetime(2009, 3, 4, 12, 30, 23)),
        ("2020:02:29 00:00:00", datetime(2020, 2, 29)),
        ("0024:03:29 12:30:23", datetime(24, 3, 29, 12, 30, 23)),
        (
            "2009:03:29 12:30:23.123456",
            datetime(2009, 3, 29, 12, 30, 23, 123456),
        ),
        (
            "2009:03:29 12:30:23Z",
            datetime(2009, 3, 29, 12, 30, 23, tzinfo=tzutc()),
        ),
        (
            "2009:03:29 12:30:23+05:30",
            datetime(2009, 3, 29, 12, 30, 23, tzinfo=tzoffset(None, 19800)),
        ),
        ("2009:03:29", datetime(2009, 3, 29, 8, 9, 10)),
    ],
)
def test_exif_date(text, expected, dayfirst, yearfirst):
    assert (
        parse(
            text,
            default=datetime(2022, 5, 5, 8, 9, 10),
            dayfirst=dayfirst,
            yearfirst=yearfirst,
        )
        == expected
    )


@pytest.mark.parametrize(
    "text",
    [
        "2009:02:29 12:30:23",
        "2009:13:04 12:30:23",
        "2009:00:04 12:30:23",
        "2009:03:00 12:30:23",
        "2009:03:32 12:30:23",
    ],
)
def test_invalid_exif_date(text):
    with pytest.raises(ParserError):
        parse(text)


def test_exif_fuzzy_tokens():
    result, tokens = parse(
        "Taken on 2009:03:29 at 12:30:23", fuzzy_with_tokens=True
    )
    assert result == datetime(2009, 3, 29, 12, 30, 23)
    assert tokens == ("Taken on ", " at ")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("9:03:29", datetime(2022, 5, 5, 9, 3, 29)),
        ("09:03:29", datetime(2022, 5, 5, 9, 3, 29)),
        ("0009:03:29", datetime(2022, 5, 5, 9, 3, 29)),
        ("0000:03:29", datetime(2022, 5, 5, 0, 3, 29)),
        ("0023:03:29", datetime(2022, 5, 5, 23, 3, 29)),
        ("12:30.5", datetime(2022, 5, 5, 12, 30, 30)),
        ("2009-03-29 12:30:23", datetime(2009, 3, 29, 12, 30, 23)),
    ],
)
def test_other_colon_and_date_formats(text, expected):
    assert parse(text, default=datetime(2022, 5, 5)) == expected
