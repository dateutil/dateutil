"""This is an implementation of functions that interact with the tzdata module.

It will only live as long as :mod:`dateutil.zoneinfo` lives; when the
``dateutil.zoneinfo`` module is removed, this can all move under :mod:`tz`.
"""

import contextlib
import io
import os
import pkgutil
import sys

import six

if six.PY2:
    _TZDATA_LOAD_EXCEPTIONS = (ImportError, IOError, UnicodeEncodeError)
else:
    _TZDATA_LOAD_EXCEPTIONS = (
        ImportError,
        FileNotFoundError,
        UnicodeEncodeError,
    )

if sys.version_info < (3, 8):
    _nullcontext = getattr(contextlib, "nullcontext", None)
    if _nullcontext is None:

        @contextlib.contextmanager
        def _nullcontext(v):
            yield v

    def _open_text(package, resource):
        pkg_data = pkgutil.get_data(package, resource)
        str_package_data = pkg_data.decode("utf-8")

        return _nullcontext(io.StringIO(str_package_data))

    def _open_binary(package, resource):
        return io.BytesIO(pkgutil.get_data(package, resource))

else:
    import importlib.resources

    if sys.version_info > (3, 9):

        def _open_text(package, resource):
            return (
                importlib.resources.files(package).joinpath(resource).open("r")
            )

        def _open_binary(package, resource):
            return (
                importlib.resources.files(package).joinpath(resource).open("rb")
            )

    else:
        _open_text = importlib.resources.open_text
        _open_binary = importlib.resources.open_binary


def _load_tzdata(key):
    components = key.split("/")
    package_name = ".".join(["tzdata.zoneinfo"] + components[:-1])
    resource_name = components[-1]

    try:
        return _open_binary(package_name, resource_name)
    except _TZDATA_LOAD_EXCEPTIONS:
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
