from __future__ import annotations

import _thread
import weakref
from collections import OrderedDict
from datetime import timedelta

from .._common import cast

TYPE_CHECKING = False

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TypeVar

    from .. import _typing

    _T = TypeVar("_T")


class _TzSingleton(type):
    def __init__(cls, *args: object, **kwargs: object) -> None:
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls: type[_T]) -> _T:
        factory = cast("_TzSingleton", cls)
        if factory.__instance is None:
            factory.__instance = super(_TzSingleton, factory).__call__()
        return factory.__instance


class _TzFactory(type):
    def instance(cls: type[_T], *args: object, **kwargs: object) -> _T:
        """Alternate constructor that returns a fresh instance"""
        return type.__call__(cls, *args, **kwargs)


class _TzOffsetFactory(_TzFactory):
    def __init__(cls, *args: object, **kwargs: object) -> None:
        cls.__instances = weakref.WeakValueDictionary()
        cls.__strong_cache = OrderedDict()
        cls.__strong_cache_size = 8

        cls._cache_lock = _thread.allocate_lock()

    def __call__(
        cls: type[_T], name: str | None, offset: float | _typing._TotalSeconds
    ) -> _T:
        factory = cast("_TzOffsetFactory", cls)
        if isinstance(offset, timedelta):
            key = (name, offset.total_seconds())
        else:
            key = (name, offset)

        instance = factory.__instances.get(key, None)
        if instance is None:
            instance = factory.__instances.setdefault(
                key, cast("Callable[..., _T]", factory.instance)(name, offset)
            )

        # This lock may not be necessary in Python 3. See GH issue #901
        with factory._cache_lock:
            factory.__strong_cache[key] = factory.__strong_cache.pop(
                key, instance
            )

            # Remove an item if the strong cache is overpopulated
            if len(factory.__strong_cache) > factory.__strong_cache_size:
                factory.__strong_cache.popitem(last=False)

        return instance


class _TzStrFactory(_TzFactory):
    def __init__(cls, *args: object, **kwargs: object) -> None:
        cls.__instances = weakref.WeakValueDictionary()
        cls.__strong_cache = OrderedDict()
        cls.__strong_cache_size = 8

        cls.__cache_lock = _thread.allocate_lock()

    def __call__(cls: type[_T], s: str, posix_offset: bool = False) -> _T:
        factory = cast("_TzStrFactory", cls)
        key = (s, posix_offset)
        instance = factory.__instances.get(key, None)

        if instance is None:
            instance = factory.__instances.setdefault(
                key,
                cast("Callable[..., _T]", factory.instance)(s, posix_offset),
            )

        # This lock may not be necessary in Python 3. See GH issue #901
        with factory.__cache_lock:
            factory.__strong_cache[key] = factory.__strong_cache.pop(
                key, instance
            )

            # Remove an item if the strong cache is overpopulated
            if len(factory.__strong_cache) > factory.__strong_cache_size:
                factory.__strong_cache.popitem(last=False)

        return instance
