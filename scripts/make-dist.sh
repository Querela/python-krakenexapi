#!/bin/bash

# NOTE: requires that a venv is already activated with
#   python3 -m venv venv
#   source venv/bin/activate
#   pip install -U pip setuptools wheel

# list tags:
#   git show-ref --tags -s | xargs -i -exec git describe --tags '{}'
#   git tag --list
# get last tag:
#   git describe --tags `git rev-list --tags --max-count=1`
# git all tags (with commits between):
#   git rev-list --tags | xargs -i -exec git describe --tags '{}'

# check tag exists
#   git describe --tags <tag> 2>&1 >/dev/null
#   EXITCODE=$?

VERSION="${1:-master}"

HERE="$(pwd)"
DIST_DIR="${HERE}/dist"
TMP_DIR=temp_dist

echo "Make dist for version: $VERSION"

if [[ "$VERSION" == "latest" ]]; then
    VERSION=$(git describe --tags `git rev-list --tags --max-count=1`)
    echo "Got latest version: $VERSION"
fi

# make temp dir
mkdir $TMP_DIR
cd $TMP_DIR

# get source for tag
git clone https://github.com/Querela/python-transformer-discord-notifier.git
cd python-transformer-discord-notifier
# checkout version if provided
if [[ "$VERSION" != "master" ]]; then
    echo "Checkout specified version"
    git checkout tags/$VERSION -b ${VERSION}-branch
fi

# checks
check-manifest
flake8 src

# make dists
python setup.py clean --all bdist_wheel sdist
# check dist
twine check dist/*.{whl,gz}

# copy results
mv dist/* ${DIST_DIR}/

# remove temp dir
cd "$HERE"
rm -rf $TMP_DIR
