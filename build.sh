#!/usr/bin/env bash
set -euo pipefail

# Change to the script's directory
cd "$(dirname "$0")"

# Detect if Python is MSYS2 or Windows-native
IS_WINDOWS_PYTHON=$(
  python3 -c "
import sys
import platform
if platform.system() == 'Windows' and 'msys' not in sys.executable.lower() and 'ucrt64' not in sys.executable.lower():
    print('yes')
else:
    print('no')
" 2>/dev/null
)

if [[ "$IS_WINDOWS_PYTHON" != "yes" ]]; then
    if grep -qi microsoft /proc/version; then
      echo '🟢 Running under WSL — using native python3'
      PYTHON="python3"
      VENV_PY=".build-venv/bin/python"
      VENV_PIP=".build-venv/bin/pip"
    else
    echo '⚠️  Detected MSYS2 or non-Windows-native Python. Attempting to use py -3...'
    if command -v py &>/dev/null; then
      echo '✅  Found py -3, using it...'
      PYTHON="py -3"
      VENV_PY=".build-venv/Scripts/python"
      VENV_PIP=".build-venv/Scripts/pip"
    else
      echo '❌  Cannot proceed: Please install Python from https://www.python.org/downloads/windows/'
      exit 1
    fi
  fi
else
  PYTHON="python3"
  VENV_PY=".build-venv/bin/python"
  VENV_PIP=".build-venv/bin/pip"
fi

# Clean up previous artifacts and build environment
rm -rf dist build omg/native *.egg-info .build-venv

# Build the native code and copy it to the native omg directory
pushd extern/omgmatch &>/dev/null
./build_all.sh
popd &>/dev/null

# Copy the built native code to the omg directory
echo "Copying built native code to omg native directory..."
cp -ar extern/omgmatch/dist/native omg/native

# Copy Windows DLL dependencies for cross-platform distribution
# Always copy Windows dependencies if the script exists, regardless of current platform
if [[ -f "copy_windows_deps.py" ]]; then
    echo "Copying Windows DLL dependencies for cross-platform distribution..."
    $PYTHON copy_windows_deps.py
else
    echo "⚠️  Windows dependency script not found, skipping Windows DLL copying"
fi

# Recreate virtual environment
echo "Creating pristine virtual environment for the build..."
$PYTHON -m venv .build-venv

# Upgrade pip, setuptools, wheel inside the venv
echo "Upgrading pip, setuptools, and wheel in the virtual environment..."
$VENV_PY -m pip install --upgrade pip setuptools wheel

# Install build and test dependencies
echo "Installing build and test dependencies..."
$VENV_PY -m pip install build pytest pytest-cov cffi

# Try to install twine only if rustc is available
if command -v rustc &>/dev/null && rustup show &>/dev/null; then
    echo "Rust is installed, installing twine..."
    if $VENV_PY -m pip install twine; then
        $VENV_PY -m twine check dist/*
    else
        echo "⚠️  Failed to install twine. Skipping check."
    fi
else
    echo "⚠️  Rust not configured. Skipping twine check."
fi

# Build the wheel and sdist
echo "Building the package..."
$VENV_PY -m build

# Reinstall the built wheel
echo "Reinstalling the built package..."
$VENV_PIP install --force-reinstall dist/pyomgmatch-*.whl

# Run the app test script
echo "Running app test script..."
$VENV_PY app_test.py

# Run pytest with coverage
echo "Running tests with pytest..."
$VENV_PY -m pytest

echo "Build and test completed successfully!"
