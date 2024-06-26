# test_tt_info.py

import pytest
from dateutil.tz.tz import _ttinfo

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

