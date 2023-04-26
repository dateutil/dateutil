import contextlib
import sys
import threading

import pytest
import six

from dateutil import tz

TZPATH_LOCK = threading.Lock()


def pop_tzdata_modules():
    tzdata_modules = {}
    for modname in list(sys.modules):
        if modname.split(".", 1)[0] != "tzdata":  # pragma: nocover
            continue

        tzdata_modules[modname] = sys.modules.pop(modname)

    return tzdata_modules


@contextlib.contextmanager
def set_tzpath(tzpath, block_tzdata=False):
    with TZPATH_LOCK:
        if block_tzdata:
            tzdata_modules = pop_tzdata_modules()
            sys.modules["tzdata"] = None

        old_tzpath = tuple(tz.TZPATH)
        try:
            tz._tzpath.reset_tzpath(to=tzpath)
            yield
        finally:
            sys.modules.pop("tzdata")
            for modname, module in tzdata_modules.items():
                sys.modules[modname] = module

            tz._tzpath.reset_tzpath(to=old_tzpath)


@set_tzpath((), block_tzdata=False)
def no_tz_data():
    tz.gettz.clear_cache()
    NYC = tz.gettz("America/New_York")
    assert NYC is None
