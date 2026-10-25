from __future__ import annotations

from . import _tzpath
from ._tzpath import reset_tzpath
from .tz import *
from .tz import __doc__

TYPE_CHECKING = False

if TYPE_CHECKING:
    from collections.abc import Sequence

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


def __getattr__(name: str) -> Sequence[str]:
    if name == "TZPATH":
        return _tzpath.TZPATH
    else:
        raise AttributeError(
            "Module %s has no attribute %s" % (repr(__name__), repr(name))
        )


def __dir__() -> Sequence[str]:
    return sorted(list(globals()) + ["TZPATH"])


class DeprecatedTzFormatWarning(Warning):
    """Warning raised when time zones are parsed from deprecated formats."""
