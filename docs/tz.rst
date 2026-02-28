==
tz
==
.. py:currentmodule:: dateutil.tz

.. automodule:: dateutil.tz

Objects
-------
.. py:data:: dateutil.tz.UTC

    A convenience instance of :class:`dateutil.tz.tzutc`.

    .. versionadded:: 2.7.0

.. py:data:: dateutil.tz.TZPATH

    A tuple containing the search path for IANA time zone data files. This
    can be set by the ``PYTHONTZPATH`` environment variable, or updated
    via :func:`reset_tzpath`.

    In Python >= 3.9, this is an alias for ``zoneinfo.TZPATH``.

    .. versionadded:: 3.0.0

Functions
---------

.. autofunction:: gettz

    .. automethod:: gettz.nocache
    .. automethod:: gettz.cache_clear

.. autofunction:: available_iana_timezones

.. autofunction:: reset_tzpath

.. py:function:: reset_tzpath(to)

    Sets the value of :data:`TZPATH`. In Python > 3.9, this is an alias for
    ``zoneinfo.reset_tzpath``, and calling it *will* reset the ``TZPATH`` for
    both ``dateutil`` and ``zoneinfo``.

    :param to:
        A sequence of absolute paths to search for zoneinfo files.  If
        ``None`` (default), the search path is reset to the default search
        path, which is determined by the ``PYTHONTZPATH`` environment
        variable, or a set of platform-specific defaults.

    .. versionadded:: 3.0.0

.. autofunction:: enfold

.. autofunction:: datetime_ambiguous
.. autofunction:: datetime_exists

.. autofunction:: resolve_imaginary


Classes
-------

.. autoclass:: tzutc

.. autoclass:: tzoffset

.. autoclass:: tzlocal

.. autoclass:: tzwinlocal
    :members: display, transitions

    .. note::

        Only available on Windows

.. autoclass:: tzrange

.. autoclass:: tzstr

.. autoclass:: tzical
    :members:

.. autoclass:: tzwin
    :members: display, transitions, list

    .. note::

        Only available on Windows


IANA Time Zone Data
-------------------
``dateutil`` attempts to search for time zone data the same way that the
standard library does. In versions of Python that include the ``zoneinfo``
module, :data:`TZPATH` is a proxy for ``zoneinfo.TZPATH`` and
:function:`reset_tzpath` is an alias for ``zoneinfo.reset_tzpath``.

``dateutil`` also backports the search path logic to Python versions < 3.9, and
the environment variable ``PYTHONTZPATH`` can be used (though there is no
equivalent to the Python compiler option).

``dateutil`` also takes an unconditional dependency on the `tzdata
<https://pypi.org/project/tzdata/>`_ package, which provides a self-contained,
up-to-date source of IANA time zone data for Python. This data source is only
used if no system time zone information is found on the search path.
