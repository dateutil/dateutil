from __future__ import unicode_literals
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import os
import subprocess
import warnings
import tempfile
import pickle


class WarningTestMixin(object):
    # Based on https://stackoverflow.com/a/12935176/467366
    class _AssertWarnsContext(warnings.catch_warnings):
        def __init__(self, expected_warnings, parent, **kwargs):
            super(WarningTestMixin._AssertWarnsContext, self).__init__(**kwargs)

            self.parent = parent
            try:
                self.expected_warnings = list(expected_warnings)
            except TypeError:
                self.expected_warnings = [expected_warnings]

            self._warning_log = []

        def __enter__(self, *args, **kwargs):
            rv = super(WarningTestMixin._AssertWarnsContext, self).__enter__(*args, **kwargs)

            if self._showwarning is not self._module.showwarning:
                super_showwarning = self._module.showwarning
            else:
                super_showwarning = None

            def showwarning(*args, **kwargs):
                if super_showwarning is not None:
                    super_showwarning(*args, **kwargs)

                self._warning_log.append(warnings.WarningMessage(*args, **kwargs))

            self._module.showwarning = showwarning
            return rv

        def __exit__(self, *args, **kwargs):
            super(WarningTestMixin._AssertWarnsContext, self).__exit__(self, *args, **kwargs)

            self.parent.assertTrue(any(issubclass(item.category, warning)
                                       for warning in self.expected_warnings
                                       for item in self._warning_log))

    def assertWarns(self, warning, callable=None, *args, **kwargs):
        warnings.simplefilter('always')
        context = self.__class__._AssertWarnsContext(warning, self)
        if callable is None:
            return context
        else:
            with context:
                callable(*args, **kwargs)


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

    def assertPicklable(self, obj, asfile=False,
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
        self.assertIsNot(obj, nobj)
        self.assertEqual(obj, nobj)


class TZWinContext(object):
    """ Context manager for changing local time zone on Windows """
    @classmethod
    def tz_change_allowed(cls):
        # Allowing dateutil to change the local TZ is set as a local environment
        # flag.
        return bool(os.environ.get('DATEUTIL_MAY_CHANGE_TZ', False))

    def __init__(self, tzname):
        self.tzname = tzname
        self._old_tz = None

    def __enter__(self):
        if not self.tz_change_allowed():
            raise ValueError('Environment variable DATEUTIL_MAY_CHANGE_TZ ' + 
                             'must be true.')

        self._old_tz = self.get_current_tz()
        self.set_current_tz(self.tzname)

    def __exit__(self, type, value, traceback):
        if self._old_tz is not None:
            self.set_current_tz(self._old_tz)

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

