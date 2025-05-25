#!/usr/bin/env python3
"""
Copy Windows DLL dependencies for the omg library.
This script handles copying the necessary MSYS2/MinGW DLLs to the omg native library directory.
"""

import shutil
import sys
from pathlib import Path


def find_msys2_bin():
    """Find the MSYS2 bin directory."""
    # Windows native paths
    windows_paths = [
        Path("C:/msys64/ucrt64/bin"),
        Path("C:/msys64/mingw64/bin"),
        Path("C:/msys64/clang64/bin"),
    ]

    # WSL paths (accessing Windows drives)
    wsl_paths = [
        Path("/mnt/c/msys64/ucrt64/bin"),
        Path("/mnt/c/msys64/mingw64/bin"),
        Path("/mnt/c/msys64/clang64/bin"),
    ]

    # Try all possible paths
    all_paths = windows_paths + wsl_paths

    for path in all_paths:
        if path.exists():
            return path

    return None


def copy_windows_dependencies():
    """Copy Windows DLL dependencies to the omg native lib directory."""
    # Required DLL dependencies
    required_dlls = ["libgomp-1.dll", "libgcc_s_seh-1.dll", "libwinpthread-1.dll"]

    # Target directory
    target_dir = Path(__file__).parent / "omg" / "native" / "lib"

    if not target_dir.exists():
        print(f"Error: Target directory does not exist: {target_dir}")
        return False

    # Find MSYS2 installation
    msys_bin = find_msys2_bin()
    if not msys_bin:
        print("Warning: MSYS2 installation not found.")
        print("Checked locations:")
        for path in [Path("C:/msys64/ucrt64/bin"), Path("C:/msys64/mingw64/bin")]:
            print(f"  - {path}")
        print("Windows DLL dependencies may be missing.")
        return False

    print(f"Found MSYS2 at: {msys_bin}")

    # Copy each required DLL
    copied_count = 0
    for dll in required_dlls:
        source_path = msys_bin / dll
        target_path = target_dir / dll

        if source_path.exists():
            try:
                shutil.copy2(source_path, target_path)
                print(f"  Copied {dll}")
                copied_count += 1
            except Exception as e:
                print(f"  Error copying {dll}: {e}")
        else:
            print(f"  Warning: {dll} not found in {msys_bin}")

    if copied_count == len(required_dlls):
        print(f"Successfully copied all {copied_count} Windows DLL dependencies.")
        return True
    else:
        print(f"Copied {copied_count}/{len(required_dlls)} Windows DLL dependencies.")
        return False


if __name__ == "__main__":
    # Allow cross-platform execution for package building
    # Only exit early if explicitly requested to skip Windows deps
    if len(sys.argv) > 1 and sys.argv[1] == "--skip":
        print("Skipping Windows DLL copying as requested.")
        sys.exit(0)

    if sys.platform != "win32":
        print("Running on non-Windows platform, checking for Windows dependencies...")
        # Check if MSYS2 is available via WSL/cross-platform access
        if not find_msys2_bin():
            print("MSYS2 not found. Windows DLL dependencies will not be included.")
            print(
                "This is expected when building on non-Windows platforms without Windows access."
            )
            sys.exit(0)

    success = copy_windows_dependencies()
    sys.exit(0 if success else 1)
