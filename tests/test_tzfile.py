import contextlib
import functools
import shutil
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


def _copy_resource_to(resource, path):
    """Copies a test resource to a path on disk."""
    from dateutil._tzdata_impl import _open_binary

    # Python 2.7 compat
    parent_dir = os.path.dirname(path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    with _open_binary("tests.resources", resource) as f:
        with open(path, "wb") as out_f:
            out_f.write(f.read())


def pop_tzdata_modules():
    tzdata_modules = {}
    for modname in list(sys.modules):
        if modname.split(".", 1)[0] != "tzdata":  # pragma: nocover
            continue

        tzdata_modules[modname] = sys.modules.pop(modname)

    return tzdata_modules


@contextdecorator
def set_tzpath(tzpath, block_tzdata=False):
    tzdata_modules = {}
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
    tz.gettz.cache_clear()
    NYC = tz.gettz("America/New_York")
    assert NYC is None


def test_tzpath_setting(tmp_path):
    with set_tzpath([tmp_path]):
        _copy_resource_to(
            "liliput_tzif", os.path.join(str(tmp_path), "Fictional", "Liliput")
        )
        tz.gettz.cache_clear()

        fiction_land = tz.gettz("Fictional/Liliput")

        assert fiction_land is not None
