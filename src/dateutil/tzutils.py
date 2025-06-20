# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.tz import resolve_imaginary, UTC


def walltimedelta(start: datetime, end: datetime, tz=None) -> datetime.timedelta:
    """
    Calculate the wall time difference between two datetime objects, accounting for DST.

    This function computes the actual elapsed time between two datetime objects while
    properly handling daylight saving time (DST) transitions. It does this by converting
    both datetime objects to UTC before calculating the difference.

    Args:
        start: The start datetime object.
        end: The end datetime object.
        tz: Optional timezone to apply if start or end is naive.

    Returns:
        A timedelta object representing the wall time difference.

    Raises:
        ValueError: If some datetime is naive and no timezone is provided, or if datetimes
                    are in different timezones.

    Examples:
        >>> from datetime import datetime
        >>> from dateutil.tz import gettz
        >>> from dateutil.tzutils import walltimedelta
        >>> 
        >>> # DST transition (spring forward loses 1 hour)
        >>> tz = gettz("America/New_York")
        >>> start = datetime(2024, 3, 10, 1, 30, tzinfo=tz)  # before DST transition
        >>> end = datetime(2024, 3, 10, 3, 30, tzinfo=tz)    # after DST transition
        >>> walltimedelta(start, end)  # only 1 hour difference in wall time
        datetime.timedelta(seconds=3600)
    """
    if tz is None:
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError('Some datetime is naive and no timezone provided.')
        elif start.tzinfo is not end.tzinfo:
            raise ValueError('Datetimes are in different timezones.')
    else:
        start = start.replace(tzinfo=tz) if start.tzinfo is None else start
        end = end.replace(tzinfo=tz) if end.tzinfo is None else end

    # Convert to UTC to handle DST transitions correctly
    start = resolve_imaginary(start).astimezone(UTC)
    end = resolve_imaginary(end).astimezone(UTC)

    return end - start
