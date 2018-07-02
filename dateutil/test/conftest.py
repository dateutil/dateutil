import os


def set_tzpath():
    """
    Sets the TZPATH variable if it's specified in an environment variable.
    """
    tzpath = os.environ.get('DATEUTIL_TZPATH', None)

    if tzpath is None:
        return

    path_components = tzpath.split(':')

    print("Setting TZPATH to {}".format(path_components))

    from dateutil import tz
    tz.TZPATHS.clear()
    tz.TZPATHS.extend(path_components)


set_tzpath()
