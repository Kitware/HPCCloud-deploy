#!/bin/bash

die () {
    echo >&2 "$@"
    exit 1
}

[ "$#" -eq 1 ] || die "Please provide path to pvpython"

echo "Installing requests ..."

REQUESTS_DIR=`mktemp -d`
curl -Lk https://github.com/kennethreitz/requests/tarball/v2.8.1 -o - | tar xz -C $REQUESTS_DIR
pushd .
cd $REQUESTS_DIR/*requests*
$1 setup.py install
popd
rm -rf $REQUESTS_DIR

echo "Installing requests-toolbelt ..."

# Install setuptools
wget https://bootstrap.pypa.io/ez_setup.py -O - | $1

REQUESTS_TOOLBELT_DIR=`mktemp -d`
curl -Lk https://github.com/sigmavirus24/requests-toolbelt/tarball/0.4.0 -o - | tar xz -C $REQUESTS_TOOLBELT_DIR
pushd .
cd $REQUESTS_TOOLBELT_DIR/*requests-toolbelt*
$1 setup.py install
popd
rm -rf $REQUESTS_TOOLBELT_DIR


