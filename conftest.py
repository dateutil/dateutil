import sys

collect_ignore = []
if sys.platform != 'win32':
    collect_ignore += [
        'dateutil/tzwin.py',
        'dateutil/tz/win.py',
    ]

# We would like to use --doctest-continue-on-failure. However this option was
# added in pytest 3.5.0, and pytest >= 3.3.0 does not support Python 3.3.
# Therefore we enable the feature here.

def pytest_configure(config):
    if config.getvalue('doctestmodules'):
        config.option.doctest_continue_on_failure = True
