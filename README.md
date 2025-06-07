# pyomgmatch

[![CI/CD Pipeline](https://github.com/USERNAME/pyomgmatch/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/pyomgmatch/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pyomgmatch.svg)](https://badge.fury.io/py/pyomgmatch)
[![Python versions](https://img.shields.io/pypi/pyversions/pyomgmatch.svg)](https://pypi.org/project/pyomgmatch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

High-performance multi-string matcher with native C backend.

## Cross-Platform Support

This package includes native libraries for Linux, macOS, and Windows. On Windows, the package includes redistributable runtime libraries (OpenMP, GCC runtime) that are licensed under permissive terms. See `THIRD_PARTY_LICENSES.md` for details.

## Installation

### Quick Install

```bash
pip install pyomgmatch
```

### Recommended: Using Virtual Environments

Using a virtual environment is recommended to avoid conflicts with other packages and ensure a clean installation.

#### On Linux/macOS

```bash
# Create a virtual environment
python3 -m venv pyomgmatch-env

# Activate the virtual environment
source pyomgmatch-env/bin/activate

# Install pyomgmatch
pip install pyomgmatch

# Verify installation
python -c "import omg.omg; print('Version:', omg.omg.get_version())"

# When done, deactivate the environment
deactivate
```

#### On Windows

**Using Command Prompt:**
```cmd
# Check available Python versions (optional)
py -0

# Create a virtual environment (using latest Python 3)
py -3 -m venv pyomgmatch-env

# Or specify a specific version if you have multiple
py -3.11 -m venv pyomgmatch-env

# Activate the virtual environment
pyomgmatch-env\Scripts\activate

# Install pyomgmatch
pip install pyomgmatch

# Verify installation
python -c "import omg.omg; print('Version:', omg.omg.get_version())"

# When done, deactivate the environment
deactivate
```

**Using PowerShell:**
```powershell
# Check available Python versions (optional)
py -0

# Create a virtual environment (using latest Python 3)
py -3 -m venv pyomgmatch-env

# Or specify a specific version if you have multiple
py -3.11 -m venv pyomgmatch-env

# Activate the virtual environment
pyomgmatch-env\Scripts\Activate.ps1

# Install pyomgmatch
pip install pyomgmatch

# Verify installation
python -c "import omg.omg; print('Version:', omg.omg.get_version())"

# When done, deactivate the environment
deactivate
```

## Development and Contributing

### Local Development Setup

**On Linux/macOS:**
```bash
# Clone the repository with submodules
git clone --recursive <repository-url>
cd pyomgmatch

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build native libraries and install in development mode
./build.sh

# Run tests
pytest

# Run tests with coverage
pytest --cov=omg --cov-report=html
```

**On Windows:**
```powershell
# Clone the repository with submodules
git clone --recursive <repository-url>
cd pyomgmatch

# Create and activate virtual environment
py -3 -m venv venv
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Build native libraries and install in development mode (requires Git Bash or WSL)
./build.sh

# Run tests
pytest

# Run tests with coverage
pytest --cov=omg --cov-report=html
```

### CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

- **Pull Request Workflow**: Runs tests, linting, and security checks on all supported platforms
- **CI/CD Pipeline**: Builds cross-platform packages and publishes to PyPI on releases
- **Release Workflow**: Creates releases with proper versioning and GitHub releases

#### Setting up CI/CD

1. Fork/clone this repository
2. Set up PyPI API tokens in GitHub Secrets:
   - `PYPI_API_TOKEN` for production releases
   - `TEST_PYPI_API_TOKEN` for testing
3. See [`GITHUB_SETUP.md`](GITHUB_SETUP.md) for detailed setup instructions

#### Creating a Release

```bash
# Create and push a version tag
git tag v0.1.2
git push origin v0.1.2
```

This will automatically trigger the CI/CD pipeline to build and publish the package.

### Code Quality

The project enforces code quality through:
- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking
- **bandit** for security scanning
- **pytest** with coverage reporting

Run quality checks locally:
```bash
# Format code
black omg/ tests/
isort omg/ tests/

# Lint code
flake8 omg/ tests/ --max-line-length=88 --extend-ignore=E203,W503

# Type checking
mypy omg/ --ignore-missing-imports

# Security scan
bandit -r omg/
```

## Quick Start

```python
import omg.omg

# Get library version
print(f"Library version: {omg.omg.get_version()}")

# Create a matcher and add patterns
with omg.omg.Compiler("patterns.omg") as compiler:
    compiler.add_pattern(b"pattern1")
    compiler.add_pattern(b"pattern2")

# Create matcher from compiled patterns
matcher = omg.omg.Matcher("patterns.omg")

# Search for patterns in text
results = matcher.match(b"some text with pattern1 in it")
for result in results:
    print(f"Found: {result.match} at offset {result.offset}")
```

