"""This is an implementation of functions that interact with the tzdata module.

It will only live as long as :mod:`dateutil.zoneinfo` lives; when the
``dateutil.zoneinfo`` module is removed, this can all move under :mod:`tz`.
"""

import contextlib
import importlib
import io
import os
import pkgutil
import sys

import six

if six.PY2:
    _TZDATA_LOAD_EXCEPTIONS = (
        ImportError,
        IOError,
        UnicodeEncodeError,
        ValueError,
    )
else:
    _TZDATA_LOAD_EXCEPTIONS = (
        ImportError,
        FileNotFoundError,
        UnicodeEncodeError,
        IsADirectoryError,
        ValueError,
    )

if sys.version_info < (3, 8):
    _nullcontext = getattr(contextlib, "nullcontext", None)
    if _nullcontext is None:

        @contextlib.contextmanager
        def _nullcontext(v):
            yield v

    def _get_data(package, resource):
        # pkgutil.get_data returns None rather than raising when the package
        # cannot be found, so turn that into the ImportError the callers
        # expect from the importlib.resources versions of these functions.
        pkg_data = pkgutil.get_data(package, resource)
        if pkg_data is None:
            raise ImportError("No package named %r" % package)

        return pkg_data

    def _open_text(package, resource):
        str_package_data = _get_data(package, resource).decode("utf-8")

        return _nullcontext(io.StringIO(str_package_data))

    def _open_binary(package, resource):
        return io.BytesIO(_get_data(package, resource))

else:
    import importlib.resources

    if sys.version_info >= (3, 9):

        def _open_text(package, resource):
            return (
                importlib.resources.files(package)
                .joinpath(resource)
                .open("r", encoding="utf-8")
            )

        def _open_binary(package, resource):
            return (
                importlib.resources.files(package).joinpath(resource).open("rb")
            )

    else:
        _open_text = importlib.resources.open_text
        _open_binary = importlib.resources.open_binary


def _is_package_directory(package, resource):
    """Whether ``resource`` names a directory inside ``package``.

    Opening a directory raises IsADirectoryError on POSIX but PermissionError
    on Windows, and on Python < 3.9 there is no portable way to ask the
    resource API, so check the package's search path directly (the tzdata
    package is a regular directory-backed package).
    """
    try:
        pkg = importlib.import_module(package)
    except ImportError:
        return False

    for base in getattr(pkg, "__path__", ()):
        if os.path.isdir(os.path.join(base, resource)):
            return True

    return False


def _load_tzdata(key):
    components = key.split("/")
    package_name = ".".join(["tzdata.zoneinfo"] + components[:-1])
    resource_name = components[-1]

    # A key naming a directory (or ending in "/") is not a zone; opening it
    # would raise a platform-dependent error, see CPython gh-85702.
    if not resource_name or _is_package_directory(package_name, resource_name):
        raise TZFileNotFound("Time zone not found: %s", zone_key=key)

    try:
        return _open_binary(package_name, resource_name)
    except _TZDATA_LOAD_EXCEPTIONS:
        # ImportError: package does not exist (or tzdata is not installed)
        # FileNotFoundError: the key is not a file in the package
        # UnicodeEncodeError: the key is not encodable as a filename
        # IsADirectoryError: the key names a package rather than a resource
        # ValueError: the key is not a valid path (e.g. contains a NUL byte)
        six.raise_from(
            TZFileNotFound("Time zone not found: %s", zone_key=key), None
        )


def _load_tzdata_keys():
    with _open_text("tzdata", "zones") as f:
        return list(filter(None, (l.strip() for l in f)))


class TZFileNotFound(ValueError):
    """Indicates that a time zone file isn't present in tzdata."""

    def __init__(self, msg, *args, **kwargs):
        # TODO: Use keyword-only argument when this is Python 3-only
        zone_key = kwargs.pop("zone_key", None)
        if zone_key is None:  # pragma: nocover
            raise TypeError("Required keyword argument missing: zone_key")

        super(TZFileNotFound, self).__init__(msg % zone_key, *args)
        self.zone_key = zone_key
