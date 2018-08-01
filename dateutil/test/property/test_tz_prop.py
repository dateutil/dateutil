from hypothesis import strategies as st
from hypothesis import given, example, assume

from dateutil import tz

from datetime import timedelta

import pytest

#
# Pre-made strategies
#
TZO_NAME_ST = st.one_of(st.none(), st.text())
TZO_OFFSET_ST = st.timedeltas(min_value=timedelta(hours=-24),
                              max_value=timedelta(hours=24))

@pytest.mark.tzoffset
@given(name1=TZO_NAME_ST, off1=TZO_OFFSET_ST,
       name2=TZO_NAME_ST, off2=TZO_OFFSET_ST)
def test_tzoffset_hashable(name1, off1, name2, off2):
    tzo1_td = tz.tzoffset(name1, off1)
    tzo1_se = tz.tzoffset(name1, off1.total_seconds())

    tzo2_td = tz.tzoffset(name2, off2)
    tzo2_se = tz.tzoffset(name2, off2.total_seconds())

    assume(tzo1_td != tzo2_td)

    assert hash(tzo1_td) == hash(tzo1_se)
    assert hash(tzo2_td) == hash(tzo2_se)

    assert hash(tzo1_td) != hash(tzo2_td)
    assert hash(tzo1_se) != hash(tzo2_se)


@pytest.mark.tzoffset
@given(name=TZO_NAME_ST, off=TZO_OFFSET_ST)
def test_tzoffset_in_sets(name, off):
    tzo = tz.tzoffset(name, off)
    s = {tzo}
    assert tzo in s

