# Third-Party Libraries and Licensing

This package includes the following third-party libraries for Windows compatibility:

## GNU Compiler Collection Runtime Libraries

### Files Included:
- `libgomp-1.dll` - GNU OpenMP runtime library
- `libgcc_s_seh-1.dll` - GCC runtime library (SEH exception handling)

### License: 
GPL-3.0-or-later WITH GCC-exception-3.1

### Redistributability:
These libraries are distributed under the **GCC Runtime Library Exception**, which explicitly permits redistribution with compiled programs, including proprietary software. The exception states:

> "When you use GCC to compile a program, GCC may combine portions of certain GCC header files and runtime libraries with the compiled program. The purpose of this Exception is to allow compilation of non-GPL (including proprietary) programs to use, in this way, the header files and runtime libraries covered by this Exception."

**Conclusion: ✅ REDISTRIBUTABLE** - These libraries can be legally distributed with our package.

## MinGW-w64 Windows POSIX Threads

### Files Included:
- `libwinpthread-1.dll` - POSIX threads implementation for Windows

### License:
MIT AND BSD-3-Clause-Clear

### Redistributability:
Both MIT and BSD-3-Clause-Clear are permissive licenses that allow redistribution for both commercial and non-commercial purposes.

**Conclusion: ✅ REDISTRIBUTABLE** - This library can be legally distributed with our package.

## Summary

All three Windows runtime libraries we're distributing are **legally redistributable**:

1. **libgomp-1.dll** and **libgcc_s_seh-1.dll**: Protected by GCC Runtime Library Exception
2. **libwinpthread-1.dll**: MIT/BSD licensed

This is a common and accepted practice in the Python ecosystem. Many popular packages distribute similar runtime libraries (e.g., NumPy, SciPy, PyTorch all include OpenMP and other runtime libraries).

## Best Practices Followed

- ✅ Only redistributing runtime libraries, not development headers
- ✅ Libraries are required dependencies, not optional
- ✅ Licenses explicitly permit redistribution
- ✅ No modifications made to the original libraries
- ✅ Libraries are placed in package-specific directory (not system-wide)

## References

- [GCC Runtime Library Exception](https://gcc.gnu.org/licenses/)
- [MinGW-w64 Licensing](https://www.mingw-w64.org/)
- [Python Packaging Guide on Binary Extensions](https://packaging.python.org/guides/distributing-packages-using-setuptools/#platform-wheels)
