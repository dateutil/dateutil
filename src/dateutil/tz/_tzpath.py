import zoneinfo

reset_tzpath = zoneinfo.reset_tzpath
InvalidTZPathWarning = zoneinfo.InvalidTZPathWarning

def __getattr__(name):
    if name == "TZPATH":
        return zoneinfo.TZPATH
    else:
        raise AttributeError(
            "Module %s has no attribute %s" % (repr(__name__), repr(name))
        )
