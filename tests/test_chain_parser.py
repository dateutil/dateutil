from dateutil.parser import ChainParser
import dateutil.parser
import pytest

import datetime as dt


def custom_parser(dt_str):
    return dt.datetime(1989, 4, 24)


@pytest.mark.smoke
def test_parser_repr():
    parse = ChainParser(
        "%Y%m%d",
        "%Y-%m-%d",
    )
    assert repr(parse) == "ChainParser('%Y%m%d', '%Y-%m-%d')"


@pytest.mark.parametrize(
    "dtstr, expected",
    [
        ("2019-12-04T00:00:00", dt.datetime(2019, 12, 4)),
        ("2019/12/04T00:00:00", dt.datetime(2019, 12, 4)),
    ],
)
def test_dateutil_parsers(dtstr, expected):
    parse = ChainParser(
        dateutil.parser.isoparse,
        dateutil.parser.parse,
    )
    assert parse(dtstr) == expected


@pytest.mark.parametrize(
    "dtstr, expected",
    [
        ("20191204", dt.datetime(2019, 12, 4)),
        ("WORKS", dt.datetime(1989, 4, 24)),
    ],
)
def test_custom_parser(dtstr, expected):
    parse = ChainParser(
        "%Y%m%d",
        custom_parser,
    )
    assert parse(dtstr) == expected


def test_build_invalid_parser():
    with pytest.raises(ValueError):
        ChainParser(None)


def test_impossible_to_parse_dtstr():
    with pytest.raises(ValueError, match="Unable to parse"):
        ChainParser("%Y%m%d")("NOTWORK")


@pytest.mark.parametrize(
    "dtstr, expected",
    [
        ("120101", dt.datetime(2012, 1, 1)),
        ("010199", dt.datetime(1999, 1, 1)),
        ("990101", dt.datetime(1999, 1, 1)),
    ],
)
def test_ymd_fallback(dtstr, expected):
    parser = ChainParser("%y%m%d", "%d%m%y")
    assert parser(dtstr) == expected


@pytest.mark.parametrize(
    "parsers, expected",
    [
        (["%y%m%d", "%d%m%y"], dt.datetime(2001, 2, 3)),
        (["%d%m%y", "%y%m%d"], dt.datetime(2003, 2, 1)),
    ],
)
def test_parser_order(parsers, expected):
    parse = ChainParser(*parsers)
    assert parse("010203") == expected
