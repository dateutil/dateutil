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

    .. versionadded:: 2.9.0

Functions
---------

.. autofunction:: gettz

    .. automethod:: gettz.nocache
    .. automethod:: gettz.cache_clear

.. autofunction:: available_iana_timezones

.. autofunction:: reset_tzpath

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
By default, ``dateutil`` looks for IANA time zone data in a variety of
different places. It starts with the search path defined in :data:`TZPATH`,
which is populated from the ``PYTHONTZPATH`` environment variable, or if that
is not set, it defaults to common system locations (e.g.
``/usr/share/zoneinfo``).

If no data is found on the search path, ``dateutil`` will look for the
`tzdata <https://pypi.org/project/tzdata/>`_ package, which provides a
self-contained, up-to-date source of IANA time zone data for Python. This is
the recommended way to ensure consistent and up-to-date time zone information
across all platforms.

If the search path and ``tzdata`` are both empty or unavailable, ``dateutil``
can also use Windows-specific zone information on Windows systems via the
:class:`tzwin` and :class:`tzwinlocal` classes.

You can customize the search path by setting the ``PYTHONTZPATH`` environment
variable before starting your Python process, or by calling
:func:`reset_tzpath` at runtime.
