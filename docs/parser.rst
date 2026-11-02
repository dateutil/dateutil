======
parser
======

.. automodule:: dateutil.parser

Functions
---------

.. automethod:: dateutil.parser.parse

The general parser also recognizes EXIF dates such as
``2009:03:29 12:30:23``. Their ``YYYY:MM:DD`` field order is fixed,
regardless of ``dayfirst`` or ``yearfirst``. The year must contain four
digits and exceed 23, and the month and day must each contain two digits.
This preserves the interpretation of valid times with padded hours, such
as ``0009:03:29``.

.. automethod:: dateutil.parser.isoparse


Classes
-------

.. autoclass:: dateutil.parser.parserinfo
  :members:
  :undoc-members:


Warnings and Exceptions
-----------------------

.. autoclass:: dateutil.parser.ParserError

.. autoclass:: dateutil.parser.UnknownTimezoneWarning
