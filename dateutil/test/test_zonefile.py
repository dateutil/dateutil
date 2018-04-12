import os

import pytest

from dateutil import zoneinfo

NO_ZONEINFO_TARBALL = os.environ.get('NO_ZONEINFO_TARBALL', False)


@pytest.mark.zoneinfo
@pytest.mark.parameterize('cached', [True, False])
def test_zonefile_instance_warns_appropriately(cached):
    for i in range(2):
        # Run this twice to ensure that the warning is raised both times
        with pytest.warns(zoneinfo.ZoneInfoTarballMissingWarning) as record:
            zoneinfo.get_zonefile_instance(new_instance=not cached)

            if NO_ZONEINFO_TARBALL:
                assert len(record) == 1
            else:
                assert len(record) == 0
