from datetime import (
    date,
    datetime,
    timedelta,
)
from dateutil._common import weekday
from typing import (
    Optional,
    Union,
)



MO: weekday
TU: weekday
WE: weekday
TH: weekday
FR: weekday
SA: weekday
SU: weekday


def _sign(x: Union[int, float]) -> int: ...


class relativedelta:
    def __abs__(self) -> relativedelta: ...
    def __add__(
        self,
        other: Union[date, timedelta, relativedelta]
    ) -> Union[date, relativedelta]: ...
    def __bool__(self) -> bool: ...
    def __div__(self, other: int) -> relativedelta: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        dt1: Optional[date] = None,
        dt2: Optional[date] = None,
        years: Union[int, float] = 0,
        months: Union[int, float] = 0,
        days: Union[int, float] = 0,
        leapdays: int = 0,
        weeks: Union[int, float] = 0,
        hours: Union[int, float] = 0,
        minutes: Union[int, float] = 0,
        seconds: Union[int, float] = 0,
        microseconds: Union[int, float] = 0,
        year: Optional[Union[float, int]] = None,
        month: Optional[Union[float, int]] = None,
        day: Optional[Union[float, int]] = None,
        weekday: Optional[Union[weekday, int]] = None,
        yearday: Optional[int] = None,
        nlyearday: Optional[int] = None,
        hour: Optional[Union[float, int]] = None,
        minute: Optional[Union[float, int]] = None,
        second: Optional[Union[float, int]] = None,
        microsecond: Optional[Union[float, int]] = None
    ) -> None: ...
    def __mul__(self, other: Union[int, float]) -> relativedelta: ...
    def __ne__(self, other: object) -> bool: ...
    def __neg__(self) -> relativedelta: ...
    def __radd__(self, other: date) -> date: ...
    def __repr__(self) -> str: ...
    def __rsub__(self, other: datetime) -> datetime: ...
    def __sub__(self, other: relativedelta) -> relativedelta: ...
    def _fix(self) -> None: ...
    def _set_months(self, months: int) -> None: ...
    def normalized(self) -> relativedelta: ...
