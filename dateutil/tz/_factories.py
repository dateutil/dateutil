import os
import weakref
from datetime import timedelta


class _TzSingleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super(_TzSingleton, cls).__init__(*args, **kwargs)

    def __call__(cls):
        if cls.__instance is None:
            cls.__instance = super(_TzSingleton, cls).__call__()
        return cls.__instance


class _TzChangeSingleton(type):

    """
    A :class: `_Tzlocalsingleton`
               Singleton metaclass to return same instance
               if 'TZ' env variable is unchanged
    """

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        cls.__tz = os.environ.get('TZ')
        super(_TzChangeSingleton, cls).__init__(*args, **kwargs)

    def __call__(cls):
        current_tz = os.environ.get('TZ')
        if cls.__instance is None or cls.__tz != current_tz:
            cls.__tz = current_tz
            cls.__instance = super(_TzChangeSingleton, cls).__call__()
        return cls.__instance


class _TzFactory(type):
    def instance(cls, *args, **kwargs):
        """Alternate constructor that returns a fresh instance"""
        return type.__call__(cls, *args, **kwargs)


class _TzOffsetFactory(_TzFactory):
    def __init__(cls, *args, **kwargs):
        cls.__instances = weakref.WeakValueDictionary()

    def __call__(cls, name, offset):
        if isinstance(offset, timedelta):
            key = (name, offset.total_seconds())
        else:
            key = (name, offset)

        instance = cls.__instances.get(key, None)
        if instance is None:
            instance = cls.__instances.setdefault(key,
                                                  cls.instance(name, offset))
        return instance


class _TzStrFactory(_TzFactory):
    def __init__(cls, *args, **kwargs):
        cls.__instances = weakref.WeakValueDictionary()

    def __call__(cls, s, posix_offset=False):
        key = (s, posix_offset)
        instance = cls.__instances.get(key, None)

        if instance is None:
            instance = cls.__instances.setdefault(key,
                cls.instance(s, posix_offset))
        return instance
