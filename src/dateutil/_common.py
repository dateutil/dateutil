"""
Common code used in multiple modules.
"""

from __future__ import annotations


TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Self, TypeVar, cast

    from . import _typing

    _T = TypeVar("_T")
else:

    def cast(typ: object, val: _T) -> _T:
        return val


class weekday:
    __slots__ = ["weekday", "n"]

    def __init__(self, weekday: int, n: int | None = None) -> None:
        self.weekday = weekday
        self.n = n

    def __call__(self, n: int | None) -> Self:
        if n == self.n:
            return self
        else:
            return self.__class__(self.weekday, n)

    def __eq__(self, other: object) -> bool:
        # Equality deliberately accepts unrelated objects with these attributes.
        other_weekday = cast("_typing._Weekday", other)
        try:
            if (
                self.weekday != other_weekday.weekday
                or self.n != other_weekday.n
            ):
                return False
        except AttributeError:
            return False
        return True

    def __hash__(self) -> int:
        return hash((
          self.weekday,
          self.n,
        ))

    def __repr__(self) -> str:
        s = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")[self.weekday]
        if not self.n:
            return s
        else:
            return "%s(%+d)" % (s, self.n)

# vim:ts=4:sw=4:et
