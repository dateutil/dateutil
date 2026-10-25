"""This is an implementation of functions that interact with the tzdata module.

It will only live as long as :mod:`dateutil.zoneinfo` lives; when the
``dateutil.zoneinfo`` module is removed, this can all move under :mod:`tz`.
"""

from __future__ import annotations

import importlib.resources

TYPE_CHECKING = False

if TYPE_CHECKING:
    from collections.abc import Sequence

    from . import _typing


_TZDATA_LOAD_EXCEPTIONS = (
    ImportError,
    FileNotFoundError,
    UnicodeEncodeError,
    IsADirectoryError,
    ValueError,
)


def _open_text(package: str, resource: str) -> _typing._ResourceReader[str]:
    return (
        importlib.resources.files(package)
        .joinpath(resource)
        .open("r", encoding="utf-8")
    )


def _open_binary(package: str, resource: str) -> _typing._ResourceReader[bytes]:
    return importlib.resources.files(package).joinpath(resource).open("rb")


def _is_package_directory(package: str, resource: str) -> bool:
    """Checks for directories before opening resources on Windows."""
    try:
        return importlib.resources.files(package).joinpath(resource).is_dir()
    except ImportError:
        return False


def _load_tzdata(key: str) -> _typing._ResourceReader[bytes]:
    components = key.split("/")
    package_name = ".".join(["tzdata.zoneinfo"] + components[:-1])
    resource_name = components[-1]

    # Empty or relative path components cannot name a zone, and they produce
    # module names that the import machinery handles inconsistently across
    # versions, so treat them as not found up front. A key naming a directory
    # (a subpackage) is not a zone either, and opening it raises a
    # platform-dependent error, see CPython gh-85702.
    if any(c in ("", ".", "..") for c in components) or _is_package_directory(
        package_name, resource_name
    ):
        raise TZFileNotFound("Time zone not found: %s", zone_key=key)

    try:
        return _open_binary(package_name, resource_name)
    except _TZDATA_LOAD_EXCEPTIONS:
        # ImportError: package does not exist (or tzdata is not installed)
        # FileNotFoundError: the key is not a file in the package
        # UnicodeEncodeError: the key is not encodable as a filename
        # IsADirectoryError: the key names a package rather than a resource
        # ValueError: the key is not a valid path (e.g. contains a NUL byte)
        raise TZFileNotFound("Time zone not found: %s", zone_key=key) from None


def _load_tzdata_keys() -> Sequence[str]:
    with _open_text("tzdata", "zones") as f:
        return list(filter(None, (l.strip() for l in f)))


class TZFileNotFound(ValueError):
    """Indicates that a time zone file isn't present in tzdata."""

    def __init__(self, msg: str, *args: object, zone_key: str) -> None:
        super().__init__(msg % zone_key, *args)
        self.zone_key = zone_key
