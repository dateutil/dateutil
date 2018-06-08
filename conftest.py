import sys

collect_ignore = []
if sys.platform != 'win32':
    collect_ignore += [
        'dateutil/tzwin.py',
        'dateutil/tz/win.py',
    ]
