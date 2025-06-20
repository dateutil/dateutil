import pytest
from datetime import datetime, timedelta
from dateutil.tz import gettz


import pytest
from datetime import datetime, timedelta
from dateutil.tz import gettz

# Skip if tzutils is not available
pytest.importorskip("dateutil.tzutils")


def test_walltimedelta_basic():
    """Basic test for walltimedelta function."""
    # Import within test to ensure package is installed
    from dateutil.tzutils import walltimedelta

    tz = gettz("America/New_York")
    start = datetime(2024, 1, 1, 12, 0, tzinfo=tz)
    end = datetime(2024, 1, 2, 12, 0, tzinfo=tz)
    delta = walltimedelta(start, end)

    # Just test that it's close to 24 hours
    assert abs(delta.total_seconds() - 86400) < 10
