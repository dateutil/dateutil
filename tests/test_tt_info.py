import pytest

class _ttinfo(object):
    __slots__ = ["offset", "delta", "isdst", "abbr",
                 "isstd", "isgmt", "dstoffset"]

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    branch_coverage = {
        'for_loop_entered': False,
        'if_statement_entered': False
    }

    def __repr__(self):
        l = []
        for attr in self.__slots__:
            self.branch_coverage['for_loop_entered'] = True
            value = getattr(self, attr)
            if value is not None:
                self.branch_coverage['if_statement_entered'] = True
                l.append("%s=%s" % (attr, repr(value)))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(l))

    def __eq__(self, other):
        if not isinstance(other, _ttinfo):
            return NotImplemented

        return (self.offset == other.offset and
                self.delta == other.delta and
                self.isdst == other.isdst and
                self.abbr == other.abbr and
                self.isstd == other.isstd and
                self.isgmt == other.isgmt and
                self.dstoffset == other.dstoffset)

    __hash__ = None

    def __ne__(self, other):
        return not (self == other)

    def __getstate__(self):
        state = {}
        for name in self.__slots__:
            state[name] = getattr(self, name, None)
        return state

    def __setstate__(self, state):
        for name in self.__slots__:
            if name in state:
                setattr(self, name, state[name])

@pytest.fixture(scope="session", autouse=True)

def print_branch_coverage(request):
    yield
    print("\nBranch Coverage:")
    for branch, state in _ttinfo.branch_coverage.items():
        print(f"{branch}: {state}")
    branch_coverage_percentage = sum(_ttinfo.branch_coverage.values()) / len(_ttinfo.branch_coverage) * 100
    if(int(branch_coverage_percentage) == 100):
        print("\n\033[32mBranch coverage is 100%\033[0m")
    else:
        print(f"\n\033[31mBranch coverage is {branch_coverage_percentage}%\033[0m")

def test_repr_all_none():
    # Case where all attributes are None
    obj = _ttinfo()
    assert repr(obj) == "_ttinfo()"

def test_repr_some_none():
    # Case where some attributes are None
    obj = _ttinfo()
    obj.offset = 3600
    obj.abbr = 'UTC'
    assert repr(obj) == "_ttinfo(offset=3600, abbr='UTC')"

def test_repr_none_none():
    # Case where no attributes are None
    obj = _ttinfo()
    obj.offset = 3600
    obj.delta = 7200
    obj.isdst = True
    obj.abbr = 'UTC'
    obj.isstd = False
    obj.isgmt = False
    obj.dstoffset = 3600
    expected_repr = ("_ttinfo(offset=3600, delta=7200, isdst=True, abbr='UTC', "
                     "isstd=False, isgmt=False, dstoffset=3600)")
    assert repr(obj) == expected_repr

def test_always_true():
    assert True

if __name__ == '__main__':
    pytest.main()