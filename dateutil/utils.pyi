from datetime import (
    datetime,
    timedelta,
)
from dateutil.tz.tz import (
    tzfile,
    tzutc,
)
from freezegun.api import FakeDatetime
from typing import (
    Optional,
    Union,
)


def default_tzinfo(dt: datetime, tzinfo: tzfile) -> datetime: ...


def today(tzinfo: Optional[Union[tzfile, tzutc]] = None) -> FakeDatetime: ...


def within_delta(dt1: datetime, dt2: datetime, delta: timedelta) -> bool: ...
