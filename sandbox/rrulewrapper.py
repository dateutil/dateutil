from rrule import *

class rrulewrapper:
    def __init__(self, freq, **kwargs):
        self._construct = kwargs.copy()
        self._construct["freq"] = freq
        self._rrule = rrule(**self._construct)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return getattr(self._rrule, name)
    
    def set(self, **kwargs):
        self._construct.update(kwargs)
        self._rrule = rrule(**self._construct)
