from __future__ import annotations

import sys

try:
    from ._version import version as __version__
except ImportError:
    __version__ = 'unknown'


TYPE_CHECKING = False

if TYPE_CHECKING:
    import types

__all__ = ["easter", "parser", "relativedelta", "rrule", "tz", "utils"]


def __getattr__(name: str) -> types.ModuleType:
    import importlib

    if name in __all__ or name == "zoneinfo":
        return importlib.import_module("." + name, __name__)
    raise AttributeError(
        "module {!r} has no attribute {!r}".format(__name__, name)
    )


def __dir__() -> list[str]:
    # __dir__ should include all the lazy-importable modules as well.
    return (
        [x for x in globals() if x not in sys.modules] + __all__ + ["zoneinfo"]
    )
