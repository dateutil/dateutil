"""Tests for the deprecated ``dateutil.zoneinfo`` shim."""

import io
import json
import tarfile
import warnings
from datetime import datetime

import pytest

from dateutil import tz

from .test_tzfile import ONE_H, ZERO, ZoneOffset, ZoneTransition, construct_zone

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    from dateutil import zoneinfo


def _legacy_tarball(with_metadata=True):
    """Builds a tarball in the format ``dateutil`` used to ship."""
    STD = ZoneOffset("STD", ZERO)
    DST = ZoneOffset("DST", ONE_H, ONE_H)
    tzif = construct_zone(
        [ZoneTransition(datetime(2010, 3, 14, 2), STD, DST)],
        "STD0DST,M3.2.0,M11.1.0",
    ).read()

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        info = tarfile.TarInfo("Fictional/Liliput")
        info.size = len(tzif)
        tf.addfile(info, io.BytesIO(tzif))

        link = tarfile.TarInfo("Fictional/Link")
        link.type = tarfile.LNKTYPE
        link.linkname = "Fictional/Liliput"
        tf.addfile(link)

        if with_metadata:
            metadata = json.dumps(
                {"metadata_version": "2.0", "tzversion": "1999z"}
            ).encode("utf-8")
            info = tarfile.TarInfo(zoneinfo.METADATA_FN)
            info.size = len(metadata)
            tf.addfile(info, io.BytesIO(metadata))

    buf.seek(0)
    return buf


def test_zoneinfofile_eager_load():
    tzdata = pytest.importorskip("tzdata")
    from dateutil._tzdata_impl import _load_tzdata_keys

    zif = zoneinfo.ZoneInfoFile()

    assert set(zif.zones) == set(_load_tzdata_keys())
    assert zif.metadata == {
        "metadata_version": "3.0",
        "tzversion": tzdata.IANA_VERSION,
    }

    NYC = zif.get("America/New_York")
    assert isinstance(NYC, tz.tzfile)
    assert NYC.key == "America/New_York"
    assert datetime(2020, 7, 1, tzinfo=NYC).tzname() == "EDT"
    assert datetime(2020, 1, 1, tzinfo=NYC).tzname() == "EST"

    assert zif.get("Fictional/Liliput") is None
    assert zif.get("Fictional/Liliput", "default") == "default"


def test_zoneinfofile_no_tzdata(block_tzdata):
    with pytest.raises(ImportError, match="tzdata"):
        zoneinfo.ZoneInfoFile()


@pytest.mark.parametrize("with_metadata", [True, False])
def test_zoneinfofile_legacy_stream(with_metadata):
    zif = zoneinfo.ZoneInfoFile(_legacy_tarball(with_metadata))

    assert set(zif.zones) == {"Fictional/Liliput", "Fictional/Link"}
    assert zif.zones["Fictional/Link"] is zif.zones["Fictional/Liliput"]

    liliput = zif.get("Fictional/Liliput")
    assert isinstance(liliput, tz.tzfile)
    assert datetime(2010, 7, 1, tzinfo=liliput).tzname() == "DST"

    if with_metadata:
        assert zif.metadata == {"metadata_version": "2.0", "tzversion": "1999z"}
    else:
        assert zif.metadata is None


def test_legacy_gettz():
    pytest.importorskip("tzdata")
    with pytest.warns(DeprecationWarning):
        NYC = zoneinfo.gettz("America/New_York")

    assert isinstance(NYC, tz.tzfile)
    assert NYC.key == "America/New_York"

    with pytest.warns(DeprecationWarning):
        assert zoneinfo.gettz("Fictional/Liliput") is None


####
# rebuild
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    from dateutil.zoneinfo import rebuild as zoneinfo_rebuild


def test_rebuild_is_an_error_by_default(tmp_path):
    target = tmp_path / "dateutil-zoneinfo.tar.gz"
    with warnings.catch_warnings():
        warnings.resetwarnings()
        with pytest.raises(zoneinfo_rebuild.RebuildDeprecationWarning):
            zoneinfo_rebuild.rebuild(str(target))

    assert not target.exists()


def test_rebuild_filter_can_be_overridden(tmp_path):
    target = tmp_path / "dateutil-zoneinfo.tar.gz"
    with warnings.catch_warnings(record=True) as record:
        warnings.resetwarnings()
        warnings.simplefilter(
            "always", category=zoneinfo_rebuild.RebuildDeprecationWarning
        )
        assert zoneinfo_rebuild.rebuild(str(target)) is None

    assert len(record) == 1
    assert record[0].category is zoneinfo_rebuild.RebuildDeprecationWarning
    assert record[0].filename == __file__.replace(".pyc", ".py")
    assert not target.exists()


def test_rebuild_can_be_ignored():
    with warnings.catch_warnings():
        warnings.resetwarnings()
        warnings.filterwarnings(
            "ignore", category=zoneinfo_rebuild.RebuildDeprecationWarning
        )
        assert zoneinfo_rebuild.rebuild("unused.tar.gz") is None
