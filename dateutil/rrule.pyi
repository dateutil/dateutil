from datetime import (
    date,
    datetime,
    time,
)
from dateutil._common import weekday as weekdaybase
from dateutil.tz.tz import tzfile
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)


YEARLY: int
MONTHLY: int
WEEKLY: int
DAILY: int
HOURLY: int
MINUTELY: int
SECONDLY: int

MO: weekday
TU: weekday
WE: weekday
TH: weekday
FR: weekday
SA: weekday
SU: weekday


def _invalidates_cache(f: Callable) -> Callable: ...


class _iterinfo:
    def __init__(self, rrule: rrule) -> None: ...
    def ddayset(self, year: int, month: int, day: int) -> Tuple[List[Union[int, None]], int, int]: ...
    def htimeset(self, hour: int, minute: int, second: int) -> List[time]: ...
    def mdayset(self, year: int, month: int, day: int) -> Tuple[List[Union[int, None]], int, int]: ...
    def mtimeset(self, hour: int, minute: int, second: int) -> List[time]: ...
    def rebuild(self, year: int, month: int) -> None: ...
    def stimeset(self, hour: int, minute: int, second: int) -> Tuple[time]: ...
    def wdayset(self, year: int, month: int, day: int) -> Tuple[List[Union[int, None]], int, int]: ...
    def ydayset(self, year: int, month: int, day: int) -> Tuple[List[int], int, int]: ...


class _rrulestr:
    def __call__(self, s: str, **kwargs) -> Union[rrule, rruleset]: ...
    def _handle_BYWEEKDAY(
        self,
        rrkwargs: Dict[str, Union[int, datetime, List[int]]],
        name: str,
        value: str,
        **kwargs
    ) -> None: ...
    def _handle_FREQ(self, rrkwargs: Dict[Any, Any], name: str, value: str, **kwargs) -> None: ...
    def _handle_UNTIL(self, rrkwargs: Dict[str, int], name: str, value: str, **kwargs) -> None: ...
    def _handle_WKST(self, rrkwargs: Dict[str, int], name: str, value: str, **kwargs) -> None: ...
    def _handle_int(self, rrkwargs: Dict[str, int], name: str, value: str, **kwargs) -> None: ...
    def _handle_int_list(
        self,
        rrkwargs: Dict[str, Union[int, List[int], List[weekday]]],
        name: str,
        value: str,
        **kwargs
    ) -> None: ...
    def _parse_rfc(
        self,
        s: str,
        dtstart: Optional[datetime] = None,
        cache: bool = False,
        unfold: bool = False,
        forceset: bool = False,
        compatible: bool = False,
        ignoretz: bool = False,
        tzids: Optional[Union[Dict[str, tzfile], Callable]] = None,
        tzinfos: None = None
    ) -> Union[rrule, rruleset]: ...
    def _parse_rfc_rrule(
        self,
        line: str,
        dtstart: Optional[datetime] = None,
        cache: bool = False,
        ignoretz: bool = False,
        tzinfos: None = None
    ) -> rrule: ...


rrulestr: _rrulestr


class rrule:
    def __init__(
        self,
        freq: int,
        dtstart: Optional[date] = None,
        interval: int = 1,
        wkst: Optional[Union[weekday, int]] = None,
        count: Optional[int] = None,
        until: Optional[date] = None,
        bysetpos: Optional[Union[Tuple[int, int, int], List[int], int, Tuple[int, int]]] = None,
        bymonth: Optional[Union[Tuple[int, int], List[int], int]] = None,
        bymonthday: Optional[Union[Tuple[int, int], List[int], int]] = None,
        byyearday: Optional[Union[List[int], Tuple[int, int, int, int]]] = None,
        byeaster: Optional[Union[List[int], int]] = None,
        byweekno: Optional[Union[List[int], int]] = None,
        byweekday: Optional[Union[weekday, Tuple[weekday, weekday], List[weekday]]] = None,
        byhour: Optional[Union[Tuple[int, int], List[int], Tuple[int, int, int, int]]] = None,
        byminute: Optional[Any] = None,
        bysecond: Optional[Any] = None,
        cache: bool = False
    ) -> None: ...
    def __str__(self) -> str: ...
    def _iter(self) -> Iterator[datetime]: ...
    def replace(self, **kwargs) -> rrule: ...


class rrulebase:
    def __contains__(self, item: datetime) -> bool: ...
    def __getitem__(self, item: Union[int, slice]) -> Union[List[datetime], datetime]: ...
    def __init__(self, cache: bool = False) -> None: ...
    def __iter__(self) -> Iterator[Any]: ...
    def _invalidate_cache(self) -> None: ...
    def _iter_cached(self) -> Iterator[datetime]: ...
    def after(self, dt: datetime, inc: bool = False) -> datetime: ...
    def before(self, dt: datetime, inc: bool = False) -> datetime: ...
    def between(
        self,
        after: datetime,
        before: datetime,
        inc: bool = False,
        count: int = 1
    ) -> List[datetime]: ...
    def count(self) -> int: ...
    def xafter(
        self,
        dt: datetime,
        count: Optional[int] = None,
        inc: bool = False
    ) -> Iterator[datetime]: ...


class rruleset:
    class _genitem:
        def __init__(self, genlist: List[rruleset._genitem], gen: Iterator[Any]) -> None: ...
        def __lt__(self, other: object) -> bool: ...
        def __ne__(self, other: object) -> bool: ...
        def __next__(self) -> None: ...
    def __init__(self, cache: bool = False) -> None: ...
    def _iter(self) -> Iterator[datetime]: ...


class weekday(weekdaybase):
    def __init__(self, wkday: int, n: Optional[int] = None) -> None: ...
