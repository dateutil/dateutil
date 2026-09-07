"""
Common code used in multiple modules.
"""


class weekday(object):
    __slots__ = ["weekday", "n"]

    def __init__(self, weekday, n=None):
        self.weekday = weekday
        self.n = n

    def __call__(self, n):
        if n == self.n:
            return self
        else:
            return self.__class__(self.weekday, n)

    def __eq__(self, other):
        try:
            if self.weekday != other.weekday or self.n != other.n:
                return False
        except AttributeError:
            return False
        return True

    def __hash__(self):
        return hash((
          self.weekday,
          self.n,
        ))

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        s = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")[self.weekday]
        if not self.n:
            return s
        else:
            return "%s(%+d)" % (s, self.n)

    # A class using `__slots__` without a `__dict__` cannot be pickled with
    # protocol 0 or 1 unless it spells out its state, and protocol 0 is still
    # the default on Python 2.  Without this, neither the `MO`..`SU`
    # constants nor any `relativedelta` carrying a weekday could be pickled
    # at those protocols.
    def __getstate__(self):
        return {name: getattr(self, name, None) for name in self.__slots__}

    def __setstate__(self, state):
        for name in self.__slots__:
            if name in state:
                setattr(self, name, state[name])

# vim:ts=4:sw=4:et
