"""Structural interfaces used by dateutil's annotations."""

from __future__ import annotations

import datetime
import types
from collections.abc import Iterator
from typing import Protocol, Self, TypeVar

_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)


class _SizedReader(Protocol[_T_co]):
    def read(self, size: int, /) -> _T_co: ...


class _Reader(_SizedReader[_T_co], Protocol[_T_co]):
    def read(self, size: int = -1, /) -> _T_co: ...


class _ReadAll(Protocol[_T_co]):
    def read(self) -> _T_co: ...


class _SeekableReader(_Reader[_T_co], Protocol[_T_co]):
    def seek(self, offset: int, whence: int = 0, /) -> int: ...
    def readline(self, size: int = -1, /) -> _T_co: ...


class _ArchiveReader(_Reader[_T_co], Protocol[_T_co]):
    def seek(self, offset: int, whence: int = 0, /) -> int: ...
    def tell(self) -> int: ...


class _ResourceReader(_Reader[_T_co], Protocol[_T_co]):
    def __iter__(self) -> Iterator[_T_co]: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> bool | None: ...


class _TotalSeconds(Protocol):
    def total_seconds(self) -> float: ...


class _RAddable(Protocol[_T_contra, _T_co]):
    def __radd__(self, other: _T_contra, /) -> _T_co: ...


class _Gettable(Protocol[_T_contra, _T_co]):
    def get(self, key: _T_contra, /) -> _T_co | None: ...


class _ContainsGet(_Gettable[_T_contra, _T_co], Protocol[_T_contra, _T_co]):
    def __contains__(self, key: object, /) -> bool: ...


class _Weekday(Protocol):
    @property
    def weekday(self) -> int: ...

    @property
    def n(self) -> int | None: ...


class _WithTimezone(Protocol):
    @property
    def tzinfo(self) -> datetime.tzinfo | None: ...

    def replace(self, *, tzinfo: datetime.tzinfo | None) -> Self: ...


class _Delta(Protocol):
    def __abs__(self) -> Self: ...
    def __neg__(self) -> Self: ...
    def __le__(self, other: Self, /) -> bool: ...


class _Subtractable(Protocol[_T_contra, _T_co]):
    def __sub__(self, other: _T_contra, /) -> _T_co: ...
