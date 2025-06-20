#!/bin/bash

# This script installs dateutil in development mode
# and installs all test dependencies

# Install the package in development mode
pip install -e .

# Install test dependencies
pip install pytest freezegun hypothesis

# Skip property tests if hypothesis is not installed
python skip_property_tests.py

echo "Ready to run tests with: python -m pytest tests/test_isolated_tzutils.py -v"
