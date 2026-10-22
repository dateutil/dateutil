from . import _tzpath
from ._tzpath import reset_tzpath
from .tz import *
from .tz import __doc__

__all__ = [
    "tzutc",
    "tzoffset",
    "tzlocal",
    "tzfile",
    "tzrange",
    "tzstr",
    "tzical",
    "tzwin",
    "tzwinlocal",
    "gettz",
    "enfold",
    "datetime_ambiguous",
    "datetime_exists",
    "resolve_imaginary",
    "available_iana_timezones",
    "UTC",
    "TZPATH",
    "reset_tzpath",
    "DeprecatedTzFormatWarning",
    "DeprecatedTzKeyWarning",
]


def __getattr__(name):
    if name == "TZPATH":
        return _tzpath.TZPATH
    else:
        raise AttributeError(
            "Module %s has no attribute %s" % (repr(__name__), repr(name))
        )


def __dir__():
    return sorted(list(globals()) + ["TZPATH"])


class DeprecatedTzFormatWarning(Warning):
    """Warning raised when time zones are parsed from deprecated formats."""
