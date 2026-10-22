from datetime import (
    date,
    datetime,
    time,
)
from dateutil.tz.tz import (
    tzoffset,
    tzutc,
)
from typing import (
    Callable,
    List,
    Optional,
    Tuple,
    Union,
)


def _takes_ascii(f: Callable) -> Callable: ...


class isoparser:
    def __init__(self, sep: Optional[Union[str, bytes]] = None) -> None: ...
    def _calculate_weekdate(self, year: int, week: int, day: int) -> date: ...
    def _parse_isodate(self, dt_str: bytes) -> Tuple[List[int], int]: ...
    def _parse_isodate_common(self, dt_str: bytes) -> Tuple[List[int], int]: ...
    def _parse_isodate_uncommon(self, dt_str: bytes) -> Tuple[List[int], int]: ...
    def _parse_isotime(
        self,
        timestr: bytes
    ) -> Union[List[Union[int, tzoffset]], List[Union[int, tzutc]], List[Union[int, None]]]: ...
    def _parse_tzstr(
        self,
        tzstr: bytes,
        zero_as_utc: bool = True
    ) -> Union[tzoffset, tzutc]: ...
    def isoparse(self, dt_str: bytes) -> datetime: ...
    def parse_isodate(self, datestr: bytes) -> date: ...
    def parse_isotime(self, timestr: bytes) -> time: ...
    def parse_tzstr(
        self,
        tzstr: bytes,
        zero_as_utc: bool = True
    ) -> Union[tzutc, tzoffset]: ...
