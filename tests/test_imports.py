import importlib.metadata
import os
import subprocess
import sys

import pytest

MODULE_TYPE = type(sys)


@pytest.fixture(scope="function")
def clean_import():
    """Create a somewhat clean import base for lazy import tests"""
    du_modules = {
        mod_name: mod
        for mod_name, mod in sys.modules.items()
        if mod_name.startswith("dateutil")
    }

    other_modules = {
        mod_name for mod_name in sys.modules if mod_name not in du_modules
    }

    for mod_name in du_modules:
        del sys.modules[mod_name]

    yield

    # Delete anything that wasn't in the origin sys.modules list
    for mod_name in list(sys.modules):
        if mod_name not in other_modules:
            del sys.modules[mod_name]

    # Restore original modules
    for mod_name, mod in du_modules.items():
        sys.modules[mod_name] = mod


@pytest.mark.parametrize(
    "module",
    ["easter", "parser", "relativedelta", "rrule", "tz", "utils"],
)
def test_lazy_import(clean_import, module):
    """Test that dateutil.[submodule] loads lazily"""

    import importlib

    import dateutil


    mod_obj = getattr(dateutil, module, None)
    assert isinstance(mod_obj, MODULE_TYPE)

    mod_imported = importlib.import_module("dateutil.%s" % module)
    assert mod_obj is mod_imported


def assert_warned_from_this_file(record):
    """The zoneinfo deprecation warning is attributed to the importing code."""
    filenames = [
        os.path.normcase(os.path.splitext(w.filename)[0])
        for w in record
        if issubclass(w.category, DeprecationWarning)
    ]
    assert filenames == [os.path.normcase(os.path.splitext(__file__)[0])]


def test_lazy_import_zoneinfo(clean_import):
    """Test that zoneinfo raises a DeprecationWarning when imported lazily."""

    import dateutil

    with pytest.warns(DeprecationWarning) as record:
        assert dateutil.zoneinfo is not None

    assert_warned_from_this_file(record)


HOST_IS_WINDOWS = sys.platform.startswith('win')


def test_import_version_str():
    """ Test that dateutil.__version__ can be imported"""
    from dateutil import __version__


def test_import_version_root():
    import dateutil
    assert hasattr(dateutil, '__version__')


def test_version_matches_distribution_metadata() -> None:
    import dateutil

    assert dateutil.__version__ == importlib.metadata.version("python-dateutil")


# Test that dateutil.easter-related imports work properly
def test_import_easter_direct():
    import dateutil.easter


def test_import_easter_from():
    from dateutil import easter


def test_import_easter_start():
    from dateutil.easter import easter


#  Test that dateutil.parser-related imports work properly
def test_import_parser_direct():
    import dateutil.parser


def test_import_parser_from():
    from dateutil import parser


def test_import_parser_all():
    # All interface
    # Other public classes
    from dateutil.parser import parse, parser, parserinfo

    for var in (parse, parserinfo, parser):
        assert var is not None


# Test that dateutil.relativedelta-related imports work properly
def test_import_relative_delta_direct():
    import dateutil.relativedelta


def test_import_relative_delta_from():
    from dateutil import relativedelta

def test_import_relative_delta_all():
    from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta

    for var in (relativedelta, MO, TU, WE, TH, FR, SA, SU):
        assert var is not None

    # In the public interface but not in all
    from dateutil.relativedelta import weekday
    assert weekday is not  None


# Test that dateutil.rrule related imports work properly
def test_import_rrule_direct():
    import dateutil.rrule


def test_import_rrule_from():
    from dateutil import rrule


def test_import_rrule_all():
    from dateutil.rrule import (
        DAILY,
        FR,
        HOURLY,
        MINUTELY,
        MO,
        MONTHLY,
        SA,
        SECONDLY,
        SU,
        TH,
        TU,
        WE,
        WEEKLY,
        YEARLY,
        rrule,
        rruleset,
        rrulestr,
    )

    rr_all = (rrule, rruleset, rrulestr,
              YEARLY, MONTHLY, WEEKLY, DAILY,
              HOURLY, MINUTELY, SECONDLY,
              MO, TU, WE, TH, FR, SA, SU)

    for var in rr_all:
       assert var is not None

    # In the public interface but not in all
    from dateutil.rrule import weekday
    assert weekday is not None


# Test that dateutil.tz related imports work properly
def test_import_tztest_direct():
    import dateutil.tz


def test_import_tz_from():
    from dateutil import tz


def test_import_tz_all():
    from dateutil.tz import (
        UTC,
        datetime_ambiguous,
        datetime_exists,
        gettz,
        resolve_imaginary,
        tzfile,
        tzical,
        tzlocal,
        tzoffset,
        tzrange,
        tzstr,
        tzutc,
        tzwin,
        tzwinlocal,
    )

    tz_all = ["tzutc", "tzoffset", "tzlocal", "tzfile", "tzrange",
              "tzstr", "tzical", "gettz", "datetime_ambiguous",
              "datetime_exists", "resolve_imaginary", "UTC"]

    tz_all += ["tzwin", "tzwinlocal"] if sys.platform.startswith("win") else []
    lvars = locals()

    for var in tz_all:
        assert lvars[var] is not None

# Test that dateutil.tzwin related imports work properly
@pytest.mark.skipif(not HOST_IS_WINDOWS, reason="Requires Windows")
def test_import_tz_windows_direct():
    import dateutil.tzwin


@pytest.mark.skipif(not HOST_IS_WINDOWS, reason="Requires Windows")
def test_import_tz_windows_from():
    from dateutil import tzwin


@pytest.mark.skipif(not HOST_IS_WINDOWS, reason="Requires Windows")
def test_import_tz_windows_star():
    from dateutil.tzwin import tzwin, tzwinlocal

    tzwin_all = [tzwin, tzwinlocal]

    for var in tzwin_all:
        assert var is not None


# Test imports of Zone Info
def test_import_zone_info_direct(clean_import):
    with pytest.warns(DeprecationWarning) as record:
        import dateutil.zoneinfo

    assert_warned_from_this_file(record)


def test_import_zone_info_from(clean_import):
    with pytest.warns(DeprecationWarning) as record:
        from dateutil import zoneinfo

    assert_warned_from_this_file(record)


def test_import_zone_info_star(clean_import):
    with pytest.warns(DeprecationWarning) as record:
        from dateutil.zoneinfo import gettz, gettz_db_metadata, rebuild

    assert_warned_from_this_file(record)

    zi_all = (gettz, gettz_db_metadata, rebuild)

    for var in zi_all:
        assert var is not None


def test_import_without_six() -> None:
    """Imports the public modules with six unavailable."""
    code = """
import sys
import warnings
sys.modules["six"] = None
from dateutil import easter, parser, relativedelta, rrule, tz, utils
if sys.platform == "win32":
    from dateutil import tzwin
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from dateutil import zoneinfo
"""
    subprocess.run([sys.executable, "-c", code], check=True)
