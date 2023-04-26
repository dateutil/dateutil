import contextlib
import functools
import sys
import threading

import pytest
import six

from dateutil import tz

TZPATH_LOCK = threading.Lock()

if sys.version_info < (3, 4):

    def contextdecorator(wrapped):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            class ContextDecorator:
                def __init__(self):
                    self.cm = contextlib.contextmanager(wrapped)(
                        *args, **kwargs
                    )

                def __enter__(self):
                    return self.cm.__enter__()

                def __exit__(self, *args, **kwargs):
                    return self.cm.__exit__(*args, **kwargs)

                def __call__(self, f):
                    @functools.wraps(f)
                    def inner(*iargs, **ikwargs):
                        with self:
                            return f(*iargs, **ikwargs)

                    return inner

            return ContextDecorator()

        return wrapper

else:
    contextdecorator = contextlib.contextmanager


def pop_tzdata_modules():
    tzdata_modules = {}
    for modname in list(sys.modules):
        if modname.split(".", 1)[0] != "tzdata":  # pragma: nocover
            continue

        tzdata_modules[modname] = sys.modules.pop(modname)

    return tzdata_modules


@contextdecorator
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
