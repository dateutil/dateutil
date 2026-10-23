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

    This is an alias for :py:data:`zoneinfo.TZPATH`.

    .. versionadded:: 3.0.0

Functions
---------

.. autofunction:: gettz

    .. automethod:: gettz.nocache
    .. automethod:: gettz.cache_clear

.. autofunction:: available_iana_timezones

.. py:function:: reset_tzpath(to=None)

    Sets the value of :data:`TZPATH`. This is an alias for
    :py:func:`zoneinfo.reset_tzpath`, and calling it *will* reset the
    search path for both ``dateutil`` and :py:mod:`zoneinfo`.

    :param to:
        A sequence of absolute paths to search for zoneinfo files. If
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


Warnings
--------

.. autoclass:: DeprecatedTzKeyWarning


IANA Time Zone Data
-------------------
``dateutil`` attempts to search for time zone data the same way that the
standard library does. :data:`TZPATH` is a proxy for
:py:data:`zoneinfo.TZPATH` and
:py:func:`reset_tzpath` is an alias for :py:func:`zoneinfo.reset_tzpath`.

The environment variable ``PYTHONTZPATH`` can be used to configure the search
path, as described in the :py:mod:`zoneinfo` documentation.

``dateutil`` also takes an unconditional dependency on the `tzdata
<https://pypi.org/project/tzdata/>`_ package, which provides a self-contained,
up-to-date source of IANA time zone data for Python. This data source is only
used if no system time zone information is found on the search path.
