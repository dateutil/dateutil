:orphan:

Parsing a local tzname: Solution
================================

This page contains solutions to the *Parsing a local tzname* exercise in
the :doc:`exercises <../index>`. Each solution reproduces the test script
from the exercise, so it can be run with ``python <solution file>`` or
collected by pytest.


.. _parsing-tzname-p1-solution:

Problem 1: United States, India and Japan
*****************************************

The abbreviations used by these zones are stable, so a fixed mapping from
every abbreviation that can appear to its IANA zone is enough. The
daylight saving variants have to be listed separately, since ``CST`` and
``CDT`` both refer to ``America/Chicago``.

:download:`Download the solution script <parsing_tzname_p1_solution.py>`

.. literalinclude:: parsing_tzname_p1_solution.py
   :language: python3
   :linenos:


.. _parsing-tzname-p2-solution:

Problem 2: India and Israel
***************************

Here the mapping cannot be a dictionary, because ``IST`` is ambiguous.
Passing a callable as ``tzinfos`` gives access to ``tzname`` and
``tzoffset``; ``dateutil`` attaches the offset to the name it found, but
with the sign reversed (``IST+05:30`` is reported as
``tzoffset=-19800``), so the offset is compared by absolute value.
``IDT`` is unambiguous and always maps to Israel.

:download:`Download the solution script <parsing_tzname_p2_solution.py>`

.. literalinclude:: parsing_tzname_p2_solution.py
   :language: python3
   :linenos:
