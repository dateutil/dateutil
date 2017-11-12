"""
Contains information about the dateutil version.
"""

VERSION_MAJOR = 2
VERSION_MINOR = 7
VERSION_PATCH = 0

VERSION_TUPLE = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
VERSION = '.'.join(map(str, VERSION_TUPLE))

# Dev build
VERSION += 'dev0'
