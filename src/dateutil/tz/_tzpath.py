from __future__ import annotations

import zoneinfo

TYPE_CHECKING = False

if TYPE_CHECKING:
    from collections.abc import Sequence

reset_tzpath = zoneinfo.reset_tzpath
InvalidTZPathWarning = zoneinfo.InvalidTZPathWarning


def __getattr__(name: str) -> Sequence[str]:
    if name == "TZPATH":
        return zoneinfo.TZPATH
    else:
        raise AttributeError(
            "Module %s has no attribute %s" % (repr(__name__), repr(name))
        )
