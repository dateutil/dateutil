from datetime import timedelta
from dateutil.tz.tz import (
    tzoffset,
    tzstr,
    tzutc,
)
from typing import (
    Optional,
    Union,
)


class _TzFactory:
    def instance(cls, *args, **kwargs) -> Union[tzstr, tzoffset]: ...


class _TzOffsetFactory:
    def __call__(cls, name: Optional[str], offset: Union[int, float, timedelta]) -> tzoffset: ...
    def __init__(cls, *args, **kwargs) -> None: ...


class _TzSingleton:
    def __call__(cls) -> tzutc: ...
    def __init__(cls, *args, **kwargs) -> None: ...


class _TzStrFactory:
    def __call__(cls, s: str, posix_offset: bool = False) -> tzstr: ...
    def __init__(cls, *args, **kwargs) -> None: ...
