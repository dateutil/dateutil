#!/bin/bash

# This script fixes installation issues with the tzutils module

# First, make sure all Python files have proper permissions
chmod +x install_tzutils.py

# Uninstall any existing installation
pip uninstall -y python-dateutil

# Remove any cached files
find src -name "__pycache__" -type d -exec rm -rf {} +
find tests -name "__pycache__" -type d -exec rm -rf {} +

# Install dev dependencies first
pip install pytest hypothesis freezegun

# Reinstall the package in development mode
pip install -e .

# Run the helper script to fix module imports
python install_tzutils.py

# Reinstall one more time to ensure everything is properly set up
pip install -e .

echo "\nInstallation complete. Now try running the tests:\n"
echo "python -m pytest tests/test_isolated_tzutils.py -v"
