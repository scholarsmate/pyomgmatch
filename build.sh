#!/usr/bin/env bash
set -euo pipefail

# Change to the script's directory
cd "$(dirname "$0")"

# Clean up previous artifacts
rm -rf dist build *.egg-info .build-venv

# Recreate virtual environment
python3 -m venv .build-venv
source .build-venv/bin/activate

# Upgrade pip, setuptools, wheel explicitly
python -m pip install --upgrade pip

python -m pip install --upgrade setuptools wheel pytest pytest-cov

# Install dependencies for build
pip install build

# Build the package
python -m build

# Check the package
twine check dist/*

# Force reinstall the new package
pip install --force-reinstall dist/omgmatcher-*.whl

# Run the test script
python app_test.py

# Run the tests
pytest
