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

# Build and install the compiled zoneinfo files
make ZFLAGS='-b fat' TOPDIR="${TMP_DIR}/tzdir" install

cd $ORIG_DIR

# dateutil depends on tzdata, but while it is installed, anything missing
# from (or unreadable in) the data we just built is silently looked up in
# the tzdata package instead, so the tests would not be testing tz master.
python -m pip uninstall -y tzdata

# Make sure that the tests will actually see the data we just built.
python - <<'EOF'
import os
import sys

from dateutil import tz

tzpath = os.environ["PYTHONTZPATH"]

try:
    import tzdata
except ImportError:
    pass
else:
    sys.exit("tzdata is still importable from %s" % tzdata.__file__)

if tuple(tz.TZPATH) != (tzpath,):
    sys.exit("Expected TZPATH to be (%r,), got %r" % (tzpath, tz.TZPATH))

with open(os.path.join(tzpath, "tzdata.zi")) as f:
    print("Testing against: %s" % f.readline().strip())

zone = tz.gettz("America/New_York")
if zone is None or not zone._filename.startswith(tzpath):
    sys.exit("America/New_York was not loaded from %s: %r" % (tzpath, zone))
EOF

# Run the tests
python -m pytest ${REPO_DIR}/tests $EXTRA_TEST_ARGS -x --pdb

