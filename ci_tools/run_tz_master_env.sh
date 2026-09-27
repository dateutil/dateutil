#!/usr/bin/env bash

###
# Runs the 'tz' tox test environment, which builds the repo against the master
# branch of the upstream tz database project.

set -e

TMP_DIR=$(readlink -f ${1})
REPO_DIR=$(readlink -f ${2})
ORIG_DIR=$(pwd)

UPSTREAM_URL="https://github.com/eggert/tz.git"

if [ -n "$TF_BUILD" ]; then
    EXTRA_TEST_ARGS=--junitxml=../unittests/TEST-tz.xml
fi

# Work in a temporary directory
cd $TMP_DIR

# Clone or update the repo
DIR_EXISTS=false
if [ -d tz ]; then
    cd tz
    if [[ $(git remote get-url origin) == ${UPSTREAM_URL} ]]; then
        git fetch origin master
        git reset --hard origin/master
        DIR_EXISTS=true
    else
        cd ..
        rm -rf tz
    fi
fi

if [ "$DIR_EXISTS" = false ]; then
    git clone ${UPSTREAM_URL}
    cd tz
fi

# Build and install the compiled zoneinfo files, as "fat" TZif files unless
# TZ_BLOAT says otherwise
TZ_BLOAT=${TZ_BLOAT:-fat}
make ZFLAGS="-b ${TZ_BLOAT}" TOPDIR="${TMP_DIR}/tzdir" install

cd $ORIG_DIR

# Make sure that the tests will actually see the data we just built. The
# tests that are about the data on TZPATH block the tzdata package
# themselves (see the tz_source fixture), so that anything missing from or
# unreadable in this data fails, rather than being answered by tzdata.
TZ_BLOAT=${TZ_BLOAT} python - <<'EOF'
import os
import struct
import sys

from dateutil import tz

tzpath = os.environ["PYTHONTZPATH"]

if tuple(tz.TZPATH) != (tzpath,):
    sys.exit("Expected TZPATH to be (%r,), got %r" % (tzpath, tz.TZPATH))

with open(os.path.join(tzpath, "tzdata.zi")) as f:
    print("Testing against: %s" % f.readline().strip())

zone = tz.gettz("America/New_York")
if zone is None or not zone._filename.startswith(tzpath):
    sys.exit("America/New_York was not loaded from %s: %r" % (tzpath, zone))

# Slim files have an empty version 1 data block, fat files do not.
with open(zone._filename, "rb") as f:
    v1_timecnt = struct.unpack(">6l", f.read(44)[20:])[3]

bloat = "fat" if v1_timecnt else "slim"
if bloat != os.environ["TZ_BLOAT"]:
    sys.exit("Expected %s TZif files, got %s" % (os.environ["TZ_BLOAT"], bloat))
print("Using %s TZif files" % bloat)
EOF

# Run the tests
python -m pytest ${REPO_DIR}/tests $EXTRA_TEST_ARGS -x --pdb

