from __future__ import unicode_literals

import contextlib
import functools
import os
import pickle
import subprocess
import sys
import tempfile
import threading
import time
import warnings

import pytest

from dateutil import tz

####
# Selecting the source of time zone data
#
# TZPATH, the gettz cache and whether the tzdata package can be imported are
# all process-wide, so tests that change them take this lock. It is reentrant
# so that a test running under a fixture that holds it can still use
# set_tzpath itself.
TZPATH_LOCK = threading.RLock()


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
def set_tzpath(tzpath, block_tzdata=False, clear_cache=True):
    tzdata_modules = {}
    with TZPATH_LOCK:
        if block_tzdata:
            tzdata_modules = pop_tzdata_modules()
            sys.modules["tzdata"] = None

        old_tzpath = tuple(tz.TZPATH)
        try:
            tz._tzpath.reset_tzpath(to=tzpath)
            # Zones already in the cache may have come from somewhere else
            # (another TZPATH, or tzdata when it is now blocked), and zones
            # cached in here must not leak out, so clear it on both ends.
            if clear_cache:
                tz.gettz.cache_clear()
            yield
        finally:
            if block_tzdata:
                sys.modules.pop("tzdata", None)
                sys.modules.update(tzdata_modules)

            tz._tzpath.reset_tzpath(to=old_tzpath)
            if clear_cache:
                tz.gettz.cache_clear()


TZ_SOURCES = ("tzpath", "tzdata")


def tz_source_skip_reason(source):
    """Why tests can't run against ``source`` here, or None if they can.

    ``"tzpath"`` is the time zone data on TZPATH (the system data, or whatever
    PYTHONTZPATH points at) with the tzdata package blocked, so that a key
    that is missing or broken there fails rather than being answered by
    tzdata. ``"tzdata"`` is the tzdata package, with an empty TZPATH.
    """
    if source == "tzpath":
        # Any real installation of the data has one of these (depending on
        # whether the "backward" links were installed); anything else, like
        # an empty directory, is treated as no data at all.
        if not any(
            os.path.isfile(os.path.join(path, *key.split("/")))
            for path in tz.TZPATH
            for key in ("Etc/UTC", "UTC")
        ):
            return "No time zone data on TZPATH"
    elif source == "tzdata":
        try:
            import tzdata  # noqa: F401
        except ImportError:
            return "tzdata is not installed"
    else:  # pragma: nocover
        raise ValueError("Unknown time zone data source: %r" % (source,))

    return None


def tz_source_context(source):
    """A context manager that makes ``source`` the only time zone data."""
    if source == "tzpath":
        return set_tzpath(tuple(tz.TZPATH), block_tzdata=True)
    else:
        return set_tzpath((), block_tzdata=False)


class TzSourceMixin(object):
    """Runs the tests in a TestCase against a single source of time zone data.

    unittest.TestCase subclasses can't use parametrized pytest fixtures, so to
    run a set of tests against more than one source, subclass the test case
    and override ``tz_source``. A ``tz_source`` of None leaves everything as
    it is.
    """

    tz_source = "tzpath"

    def setUp(self):
        super(TzSourceMixin, self).setUp()
        if self.tz_source is None:
            return

        reason = tz_source_skip_reason(self.tz_source)
        if reason is not None:
            self.skipTest(reason)

        context = tz_source_context(self.tz_source)
        context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)


class PicklableMixin(object):
    def _get_nobj_bytes(self, obj, dump_kwargs, load_kwargs):
        """
        Pickle and unpickle an object using ``pickle.dumps`` / ``pickle.loads``
        """
        pkl = pickle.dumps(obj, **dump_kwargs)
        return pickle.loads(pkl, **load_kwargs)

    def _get_nobj_file(self, obj, dump_kwargs, load_kwargs):
        """
        Pickle and unpickle an object using ``pickle.dump`` / ``pickle.load`` on
        a temporary file.
        """
        with tempfile.TemporaryFile('w+b') as pkl:
            pickle.dump(obj, pkl, **dump_kwargs)
            pkl.seek(0)         # Reset the file to the beginning to read it
            nobj = pickle.load(pkl, **load_kwargs)

        return nobj

    def assertPicklable(self, obj, singleton=False, asfile=False,
                        dump_kwargs=None, load_kwargs=None):
        """
        Assert that an object can be pickled and unpickled. This assertion
        assumes that the desired behavior is that the unpickled object compares
        equal to the original object, but is not the same object.
        """
        get_nobj = self._get_nobj_file if asfile else self._get_nobj_bytes
        dump_kwargs = dump_kwargs or {}
        load_kwargs = load_kwargs or {}

        nobj = get_nobj(obj, dump_kwargs, load_kwargs)
        if not singleton:
            self.assertIsNot(obj, nobj)
        self.assertEqual(obj, nobj)


class TZContextBase(object):
    """
    Base class for a context manager which allows changing of time zones.

    Subclasses may define a guard variable to either block or or allow time
    zone changes by redefining ``_guard_var_name`` and ``_guard_allows_change``.
    The default is that the guard variable must be affirmatively set.

    Subclasses must define ``get_current_tz`` and ``set_current_tz``.
    """
    _guard_var_name = "DATEUTIL_MAY_CHANGE_TZ"
    _guard_allows_change = True

    def __init__(self, tzval):
        self.tzval = tzval
        self._old_tz = None

    @classmethod
    def tz_change_allowed(cls):
        """
        Class method used to query whether or not this class allows time zone
        changes.
        """
        guard = bool(os.environ.get(cls._guard_var_name, False))

        # _guard_allows_change gives the "default" behavior - if True, the
        # guard is overcoming a block. If false, the guard is causing a block.
        # Whether tz_change is allowed is therefore the XNOR of the two.
        return guard == cls._guard_allows_change

    @classmethod
    def tz_change_disallowed_message(cls):
        """ Generate instructions on how to allow tz changes """
        msg = ('Changing time zone not allowed. Set {envar} to {gval} '
               'if you would like to allow this behavior')

        return msg.format(envar=cls._guard_var_name,
                          gval=cls._guard_allows_change)

    def __enter__(self):
        if not self.tz_change_allowed():
            msg = self.tz_change_disallowed_message()
            pytest.skip(msg)

            # If this is used outside of a test suite, we still want an error.
            raise ValueError(msg)  # pragma: no cover

        self._old_tz = self.get_current_tz()
        self.set_current_tz(self.tzval)

    def __exit__(self, type, value, traceback):
        if self._old_tz is not None:
            self.set_current_tz(self._old_tz)

        self._old_tz = None

    def get_current_tz(self):
        raise NotImplementedError

    def set_current_tz(self):
        raise NotImplementedError


class TZEnvContext(TZContextBase):
    """
    Context manager that temporarily sets the `TZ` variable (for use on
    *nix-like systems). Because the effect is local to the shell anyway, this
    will apply *unless* a guard is set.

    If you do not want the TZ environment variable set, you may set the
    ``DATEUTIL_MAY_NOT_CHANGE_TZ_VAR`` variable to a truthy value.
    """
    _guard_var_name = "DATEUTIL_MAY_NOT_CHANGE_TZ_VAR"
    _guard_allows_change = False

    def get_current_tz(self):
        return os.environ.get('TZ', UnsetTz)

    def set_current_tz(self, tzval):
        if tzval is UnsetTz and 'TZ' in os.environ:
            del os.environ['TZ']
        else:
            os.environ['TZ'] = tzval

        time.tzset()


class TZWinContext(TZContextBase):
    """
    Context manager for changing local time zone on Windows.

    Because the effect of this is system-wide and global, it may have
    unintended side effect. Set the ``DATEUTIL_MAY_CHANGE_TZ`` environment
    variable to a truthy value before using this context manager.
    """
    def get_current_tz(self):
        p = subprocess.Popen(['tzutil', '/g'], stdout=subprocess.PIPE)

        ctzname, err = p.communicate()
        ctzname = ctzname.decode()     # Popen returns

        if p.returncode:
            raise OSError('Failed to get current time zone: ' + err)

        return ctzname

    def set_current_tz(self, tzname):
        p = subprocess.Popen('tzutil /s "' + tzname + '"')

        out, err = p.communicate()

        if p.returncode:
            raise OSError('Failed to set current time zone: ' +
                          (err or 'Unknown error.'))


###
# Utility classes
class NotAValueClass(object):
    """
    A class analogous to NaN that has operations defined for any type.
    """
    def _op(self, other):
        return self             # Operation with NotAValue returns NotAValue

    def _cmp(self, other):
        return False

    __add__ = __radd__ = _op
    __sub__ = __rsub__ = _op
    __mul__ = __rmul__ = _op
    __div__ = __rdiv__ = _op
    __truediv__ = __rtruediv__ = _op
    __floordiv__ = __rfloordiv__ = _op

    __lt__ = __rlt__ = _op
    __gt__ = __rgt__ = _op
    __eq__ = __req__ = _op
    __le__ = __rle__ = _op
    __ge__ = __rge__ = _op


NotAValue = NotAValueClass()


class ComparesEqualClass(object):
    """
    A class that is always equal to whatever you compare it to.
    """

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __le__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False

    __req__ = __eq__
    __rne__ = __ne__
    __rle__ = __le__
    __rge__ = __ge__
    __rlt__ = __lt__
    __rgt__ = __gt__


ComparesEqual = ComparesEqualClass()


class UnsetTzClass(object):
    """ Sentinel class for unset time zone variable """
    pass


UnsetTz = UnsetTzClass()
