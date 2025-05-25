# pyomgmatch
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

### Development Installation

If you want to install from source for development:

**On Linux/macOS:**
```bash
# Clone the repository
git clone <repository-url>
cd pyomgmatch

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest
```

**On Windows:**
```cmd
# Clone the repository
git clone <repository-url>
cd pyomgmatch

# Create and activate virtual environment
py -3 -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest
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

