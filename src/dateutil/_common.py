"""
Common code used in multiple modules.
"""


class weekday:
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

    def __getstate__(self):
        # PyPy will not pickle a slots class that has no __getstate__.
        # This is the (instance dict, slot dict) pair CPython already produces.
        slotstate = {}
        for name in self.__slots__:
            slotstate[name] = getattr(self, name)
        inst_dict = getattr(self, "__dict__", None)
        if inst_dict:
            inst_dict = inst_dict.copy()
        else:
            inst_dict = None
        return (inst_dict, slotstate)

    def __repr__(self):
        s = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")[self.weekday]
        if not self.n:
            return s
        else:
            return "%s(%+d)" % (s, self.n)

# vim:ts=4:sw=4:et
