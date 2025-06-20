#!/bin/bash

# Script to rebuild dateutil with fixed module structure

# Remove old installation
pip uninstall -y python-dateutil

# Install in development mode
pip install -e .

# Install test dependencies
pip install pytest freezegun hypothesis

echo "Package reinstalled. Try running pytest now."
