def isoformat(dt, utc_zulu=True):
    """
    Formats the datetime using datetime.isoformat()

    If `utc_zulu` is `True` and `dt` has UTC timezone then the suffix will be
    `'Z'` instead of `'+00:00'`. Otherwise the output is unchanged.
    """
    if dt.tzinfo is not None and dt.tzinfo.tzname(dt) == 'UTC' and utc_zulu:
        return dt.replace(tzinfo=None).isoformat() + 'Z'
    return dt.isoformat()
