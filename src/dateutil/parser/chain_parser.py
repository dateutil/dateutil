import datetime as dt


class _FixedStrptime(object):
    """Parses datetime from strings by using a format that will be fed to strptime"""
    def __init__(self, format_):
        self._format = format_

    def __call__(self, dt_str):
        return dt.datetime.strptime(dt_str, self._format)

    def __repr__(self):
        return "StrptimeParser(%r)" % (self._format)


class ChainParser(object):
    """Parser that is built from combining multiple parsers

    All provided parsers should have a call method that takes a string as input
    and raise `ValueError` if they cannot parse the datetime.

    If the parser provided is a string, a parser will be constructed which
    uses :func:`datetime.datetime.strptime` with the provided format.

    This is useful for situations where you know that your dates are in one of a
    small number of formats, or where you want to specifically prioritize some
    formats over others. For example, if you want to interpret a 6-digit number as
    ``YYMMDD``, then ``DDMMYY``, then fall back to `dateutil.parser.parse` for any
    strings that don't match either of those, you could construct the following
    ``ChainParser``:

    .. doctest:: chainparser

        >>> parser = ChainParser("%y%m%d",  "%d%m%y", dateutil.parser.parse)
        >>> print(parser("120101"))
        2012-01-01 00:00:00
        >>> print(parser("010199"))
        1999-01-01 00:00:00


    """
    def __init__(self, *parsers):
        self._parsers = [
            _FixedStrptime(parser) if isinstance(parser, str) else parser
            for parser in parsers
        ]
        for parser in self._parsers:
            if not callable(parser):
                raise ValueError(
                    "Invalid parser {0!r}, the parser is not callable."
                    .format(parser)
                )

    def __call__(self, dt_str):
        for parser in self._parsers:
            try:
                return parser(dt_str)
            except ValueError:
                pass
        raise ValueError(
            "Unable to parse string {0!r} with the available parsers"
            .format(dt_str)
        )

    def __repr__(self):
        chain_parser_args = [
            repr(p._format) if isinstance(p, _FixedStrptime) else repr(p)
            for p in self._parsers
        ]
        return "ChainParser(%s)" % ", ".join(chain_parser_args)
