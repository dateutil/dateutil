import pytest

from ._common import (
    TZ_SOURCES,
    set_tzpath,
    tz_source_context,
    tz_source_skip_reason,
)


# Configure pytest to ignore xfailing tests
# See: https://stackoverflow.com/a/53198349/467366
def pytest_collection_modifyitems(items):
    for item in items:
        marker_getter = getattr(item, "get_closest_marker", None)

        # Python 3.3 support
        if marker_getter is None:
            marker_getter = item.get_marker

        marker = marker_getter("xfail")

        # Need to query the args because conditional xfail tests still have
        # the xfail mark even if they are not expected to fail
        if marker and (not marker.args or marker.args[0]):
            item.add_marker(pytest.mark.no_cover)


@pytest.fixture(params=TZ_SOURCES)
def tz_source(request):
    """Runs a test against each source of IANA time zone data in turn.

    With ``"tzpath"``, only the data on TZPATH is used and the tzdata package
    is blocked, so a key that is missing or broken there makes the test fail
    instead of being silently answered by tzdata. With ``"tzdata"``, only the
    tzdata package is used.
    """
    reason = tz_source_skip_reason(request.param)
    if reason is not None:
        pytest.skip(reason)

    with tz_source_context(request.param):
        yield request.param


@pytest.fixture
def block_tzdata():
    """Makes the tzdata package impossible to import."""
    from dateutil import tz

    with set_tzpath(tuple(tz.TZPATH), block_tzdata=True):
        yield
