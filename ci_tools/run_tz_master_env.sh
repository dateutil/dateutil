#!/usr/bin/env bash

###
# Runs the 'tz' tox test environment, which builds the repo against the master
# branch of the upstream tz database project.

set -e

TMP_DIR=${1}
REPO_DIR=${2}
ORIG_DIR=$(pwd)
CITOOLS_DIR=$REPO_DIR/ci_tools

REPO_TARBALL=${REPO_DIR}/src/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz
TMP_TARBALL=${TMP_DIR}/dateutil-zoneinfo.tar.gz

UPSTREAM_URL="https://github.com/eggert/tz.git"

if [ -n "$TF_BUILD" ]; then
    EXTRA_TEST_ARGS=--junitxml=../unittests/TEST-tz.xml
fi

function cleanup {
    # Since this script modifies the original repo, whether or not
    # it fails we need to restore the original file so as to not
    # overwrite the user's local changes.
    echo "Cleaning up."
    if [ -f $TMP_TARBALL ]; then
        cp -p $TMP_TARBALL $REPO_TARBALL
    fi
}

trap cleanup EXIT

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

# Get the version
make version
VERSION=$(cat version)
TARBALL_NAME=tzdata${VERSION}.tar.gz

# Make the tzdata tarball - deactivate errors because
# I don't know how to make just the .tar.gz and I don't
# care if the others fail
set +e
make traditional_tarballs
set -e

mv $TARBALL_NAME $ORIG_DIR

# Install everything else
make ZFLAGS='-b fat' TOPDIR="$TMP_DIR/tzdir" install

#
# Make the zoneinfo tarball
#
cd $ORIG_DIR

# Put the latest version of zic on the path
PATH=$TMP_DIR/tzdir/usr/sbin:${PATH}

# Stash the old zoneinfo file in the temporary directory
mv $REPO_TARBALL $TMP_TARBALL


# Make the metadata file
ZONEFILE_METADATA_NAME=zonefile_metadata_master.json
${CITOOLS_DIR}/make_zonefile_metadata.py \
    $TARBALL_NAME \
    $VERSION \
    $ZONEFILE_METADATA_NAME

python ${REPO_DIR}/updatezinfo.py $ZONEFILE_METADATA_NAME

# Run the tests
python -m pytest ${REPO_DIR}/tests $EXTRA_TEST_ARGS

