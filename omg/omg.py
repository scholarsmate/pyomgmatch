# omg.py

import platform
from dataclasses import dataclass
from typing import List, Literal, Optional

from cffi import FFI

ffi = FFI()
ffi.cdef(
    """
typedef struct oa_matcher_t oa_matcher_t;
typedef struct oa_matcher_compiler_struct oa_matcher_compiler_t;

typedef struct {
    size_t offset;
    uint32_t len;
    const uint8_t* match;
} oa_match_result_t;

typedef struct {
    size_t count;
    oa_match_result_t* matches;
} oa_match_results_t;

typedef struct {
    uint64_t total_input_bytes;
    uint64_t total_stored_bytes;
    uint32_t stored_pattern_count;
    uint32_t short_pattern_count;
    uint32_t duplicate_patterns;
    uint32_t smallest_pattern_length;
    uint32_t largest_pattern_length;
} oa_match_pattern_store_stats_t;

typedef struct {
    uint64_t total_hits;
    uint64_t total_misses;
    uint64_t total_filtered;
    uint64_t total_attempts;
    uint64_t total_comparisons;
} oa_match_stats_t;

oa_matcher_compiler_t* oa_matcher_compiler_create(const char* compiled_file, int case_insensitive,
                                                  int ignore_punctuation, int elide_whitespace);
int oa_matcher_compiler_add_pattern(oa_matcher_compiler_t* compiler, const uint8_t* pattern, uint32_t len);
const oa_match_pattern_store_stats_t* oa_matcher_compiler_get_pattern_store_stats(const oa_matcher_compiler_t* compiler);
int oa_matcher_compiler_destroy(oa_matcher_compiler_t* compiler);

int oa_matcher_is_compiled(const char* compiled_file);
int oa_matcher_emit_header_info(const oa_matcher_t* matcher, FILE* fp);

int oa_matcher_compile_patterns(const char* compiled_file, const uint8_t* patterns_buf,
                                uint64_t patterns_buf_size, int case_insensitive, int ignore_punctuation,
                                int elide_whitespace, oa_match_pattern_store_stats_t* pattern_store_stats);
int oa_matcher_compile_patterns_filename(const char* compiled_file, const char* patterns_file,
                                         int case_insensitive, int ignore_punctuation, int elide_whitespace,
                                         oa_match_pattern_store_stats_t* pattern_store_stats);

oa_matcher_t* oa_matcher_create_from_buffer(const char* compiled_file, const uint8_t* patterns_buffer,
                                            uint64_t patterns_buffer_size, int case_insensitive, int ignore_punctuation,
                                            int elide_whitespace, oa_match_pattern_store_stats_t* stats);
oa_matcher_t* oa_matcher_create(const char* compiled_or_patterns_file, int case_insensitive,
                                int ignore_punctuation, int elide_whitespace,
                                oa_match_pattern_store_stats_t* stats);

int oa_matcher_add_stats(oa_matcher_t* matcher, oa_match_stats_t* stats);
int oa_matcher_destroy(oa_matcher_t* matcher);

oa_match_results_t* oa_matcher_match(const oa_matcher_t* matcher,
                                     const uint8_t* haystack,
                                     size_t haystack_size,
                                     int no_overlap,
                                     int longest_only,
                                     int word_boundary);
void oa_match_results_destroy(oa_match_results_t* results);

uint8_t* oa_matcher_map_file(FILE* file, size_t* size, int prefetch_sequential);
uint8_t* oa_matcher_map_filename(const char* filename, size_t* size, int prefetch_sequential);
int oa_matcher_unmap_file(const uint8_t* addr, size_t size);

int oa_matcher_set_num_threads(oa_matcher_t* matcher, int threads);
int oa_matcher_get_num_threads(const oa_matcher_t* matcher);
int oa_matcher_set_chunk_size(oa_matcher_t* matcher, int chunk);
int oa_matcher_get_chunk_size(const oa_matcher_t* matcher);

const char* oa_matcher_version();
"""
)

# C library FFI handle
C = None


@dataclass
class PatternStoreStats:
    total_input_bytes: int
    total_stored_bytes: int
    stored_pattern_count: int
    short_pattern_count: int
    duplicate_patterns: int
    smallest_pattern_length: int
    largest_pattern_length: int


@dataclass
class MatchStats:
    total_hits: int
    total_misses: int
    total_filtered: int
    total_attempts: int
    total_comparisons: int


@dataclass
class MatchResult:
    offset: int
    match: bytes


def _load_library() -> Optional[ffi.CData]:
    import os
    import sys

    override = os.getenv("OMG_LIB_PATH")
    if override:
        return ffi.dlopen(override)

    system = sys.platform
    arch = platform.machine().lower()

    if arch in {"x86_64", "amd64"}:
        arch = "x64"
    elif arch in {"aarch64", "arm64"}:
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {arch}")

    if system.startswith("linux"):
        lib_name = f"libomg-linux-{arch}.so"
    elif system in {"win32", "cygwin"}:
        lib_name = f"libomg-windows-{arch}.dll"
    elif system == "darwin":
        lib_name = f"libomg-macos-{arch}.dylib"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    lib_path = os.path.join(os.path.dirname(__file__), "native", "lib", lib_name)

    if not os.path.exists(lib_path):
        raise RuntimeError(f"Native library not found: {lib_path}")

    return ffi.dlopen(lib_path)


def _get_library() -> ffi.CData:
    global C
    if C is None:
        try:
            C = _load_library()
        except OSError as e:
            raise RuntimeError("Failed to load native library: " + str(e))
    return C


def get_version() -> str:
    version = _get_library().oa_matcher_version()
    if version == ffi.NULL:
        raise RuntimeError("Failed to get version")
    return ffi.string(version).decode("utf-8")


class Compiler:
    def __init__(self, compiled_file: str, case_insensitive: bool = False,
                 ignore_punctuation: bool = False, elide_whitespace: bool = False) -> None:
        lib = _get_library()
        self._lib = lib
        self._compiler = lib.oa_matcher_compiler_create(
            compiled_file.encode("utf-8"),
            int(case_insensitive),
            int(ignore_punctuation),
            int(elide_whitespace),
        )
        if self._compiler == ffi.NULL:
            raise RuntimeError("Failed to create compiler")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def __del__(self):
        self.destroy()

    def add_pattern(self, pattern: bytes) -> None:
        if not isinstance(pattern, (bytes, bytearray)):
            raise TypeError("Pattern must be bytes")
        if self._lib.oa_matcher_compiler_add_pattern(self._compiler, pattern, len(pattern)) != 0:
            raise ValueError("Failed to add pattern")

    def get_stats(self) -> PatternStoreStats:
        stats_ptr = self._lib.oa_matcher_compiler_get_pattern_store_stats(self._compiler)
        if stats_ptr == ffi.NULL:
            raise RuntimeError("Failed to retrieve stats")
        return PatternStoreStats(
            **{k: getattr(stats_ptr, k) for k in PatternStoreStats.__annotations__}
        )

    def destroy(self) -> None:
        if hasattr(self, "_compiler") and self._compiler and C is not None:
            self._lib.oa_matcher_compiler_destroy(self._compiler)
            self._compiler = ffi.NULL

    @staticmethod
    def compile_from_filename(
        compiled_file: str,
        patterns_file: str,
        case_insensitive: bool = False,
        ignore_punctuation: bool = False,
        elide_whitespace: bool = False,
    ) -> PatternStoreStats:
        stats = ffi.new("oa_match_pattern_store_stats_t*")
        if (
            _get_library().oa_matcher_compile_patterns_filename(
                compiled_file.encode("utf-8"),
                patterns_file.encode("utf-8"),
                int(case_insensitive),
                int(ignore_punctuation),
                int(elide_whitespace),
                stats,
            )
            != 0
        ):
            raise RuntimeError("Compilation failed")
        return PatternStoreStats(
            **{k: getattr(stats, k) for k in PatternStoreStats.__annotations__}
        )

    @staticmethod
    def compile_from_buffer(
        compiled_file: str,
        patterns_buf: bytes,
        case_insensitive: bool = False,
        ignore_punctuation: bool = False,
        elide_whitespace: bool = False,
    ) -> PatternStoreStats:
        stats = ffi.new("oa_match_pattern_store_stats_t*")
        if (
            _get_library().oa_matcher_compile_patterns(
                compiled_file.encode("utf-8"),
                patterns_buf,
                len(patterns_buf),
                int(case_insensitive),
                int(ignore_punctuation),
                int(elide_whitespace),
                stats,
            )
            != 0
        ):
            raise RuntimeError("Compilation failed")
        return PatternStoreStats(
            **{k: getattr(stats, k) for k in PatternStoreStats.__annotations__}
        )


class Matcher:
    def __init__(
        self,
        compiled_or_patterns_file: str,
        case_insensitive: bool = False,
        ignore_punctuation: bool = False,
        elide_whitespace: bool = False,
    ) -> None:
        lib = _get_library()
        pat_stats = ffi.new("oa_match_pattern_store_stats_t*")
        m = lib.oa_matcher_create(
            compiled_or_patterns_file.encode("utf-8"),
            int(case_insensitive),
            int(ignore_punctuation),
            int(elide_whitespace),
            pat_stats,
        )
        if m == ffi.NULL:
            raise RuntimeError("Failed to create matcher")
        self._matcher = m

        self._match_stats = ffi.new("oa_match_stats_t*")
        if lib.oa_matcher_add_stats(self._matcher, self._match_stats) != 0:
            raise RuntimeError("Failed to attach stats to matcher")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def __del__(self):
        self.destroy()

    def match(
        self,
        haystack: bytes,
        no_overlap: Literal[True, False] = False,
        longest_only: Literal[True, False] = False,
        word_boundary: Literal[True, False] = False,
    ) -> List[MatchResult]:
        if not isinstance(haystack, (bytes, bytearray)):
            raise TypeError("haystack must be bytes or bytearray")
        lib = _get_library()
        buf = ffi.new("uint8_t[]", haystack)
        res = lib.oa_matcher_match(
            self._matcher,
            buf,
            len(haystack),
            int(no_overlap),
            int(longest_only),
            int(word_boundary),
        )
        if res == ffi.NULL:
            return []

        out: List[MatchResult] = []
        for i in range(res.count):
            m = res.matches[i]
            out.append(
                MatchResult(offset=m.offset, match=bytes(ffi.buffer(m.match, m.len)))
            )
        lib.oa_match_results_destroy(res)
        return out

    def get_match_stats(self) -> MatchStats:
        ms = self._match_stats
        return MatchStats(
            **{k: int(getattr(ms, k)) for k in MatchStats.__annotations__}
        )

    def reset_match_stats(self) -> None:
        ms = self._match_stats
        for k in MatchStats.__annotations__:
            setattr(ms, k, 0)

    def set_threads(self, threads: int) -> None:
        if _get_library().oa_matcher_set_num_threads(self._matcher, threads) != 0:
            raise ValueError(f"Invalid thread count: {threads}")

    def get_threads(self) -> int:
        return _get_library().oa_matcher_get_num_threads(self._matcher)

    def set_chunk_size(self, chunk: int) -> None:
        if _get_library().oa_matcher_set_chunk_size(self._matcher, chunk) != 0:
            raise ValueError(f"Invalid chunk size: {chunk}")

    def get_chunk_size(self) -> int:
        return _get_library().oa_matcher_get_chunk_size(self._matcher)

    def destroy(self) -> None:
        if hasattr(self, "_matcher") and self._matcher and C is not None:
            _get_library().oa_matcher_destroy(self._matcher)
            self._matcher = ffi.NULL
