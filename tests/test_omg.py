# tests/test_omg.py

import pytest

from omg.omg import (Compiler, Matcher, MatchStats, PatternStoreStats,
                     get_version)


def write_file(path, lines):
    path.write_text("\n".join(lines), encoding="utf-8")


def test_get_version():
    version = get_version()
    assert isinstance(version, str)
    assert len(version) > 0
    assert version.count(".") == 2
    major, minor, patch = map(int, version.split("."))
    assert major == 1
    assert minor == 0
    assert patch == 0


def test_compiler_add_patterns(tmp_path):
    output_path = str(tmp_path / "manual_add.omg")
    with Compiler(output_path, case_insensitive=True) as compiler:
        compiler.add_pattern(b"Alpha")
        compiler.add_pattern(b"Beta")
        stats = compiler.get_stats()
        assert isinstance(stats, PatternStoreStats)
        assert stats.stored_pattern_count == 1
        assert stats.short_pattern_count == 1
        assert stats.total_input_bytes == 9
        assert stats.total_stored_bytes == 5
        assert stats.smallest_pattern_length == 4
        assert stats.largest_pattern_length == 5

    # Load the compiled matcher and match
    with Matcher(output_path, case_insensitive=True) as m:
        hay = b"alpha beta gamma"
        results = m.match(hay)
        assert len(results) == 2
        assert results[0].match.lower() in [b"alpha", b"beta"]


def test_compile_and_match(tmp_path):
    patterns = ["foo", "bar", "bazinga"]
    pat_file = tmp_path / "patterns.txt"
    write_file(pat_file, patterns)

    compiled_file = str(tmp_path / "matcher.omg")
    ps_stats = Compiler.compile_from_filename(compiled_file, str(pat_file))
    assert isinstance(ps_stats, PatternStoreStats)
    assert ps_stats.smallest_pattern_length == 3
    assert ps_stats.largest_pattern_length == 7
    assert ps_stats.stored_pattern_count == 1
    assert ps_stats.short_pattern_count == 2
    assert ps_stats.total_input_bytes == 13
    assert ps_stats.total_stored_bytes == 7

    with Matcher(compiled_file) as m2:
        haystack = b"xx foobar yy foo zz bar"
        results = m2.match(haystack)
        offsets = [r.offset for r in results]
        matches = [r.match for r in results]
        assert offsets == [3, 6, 13, 20]
        assert matches == [b"foo", b"bar", b"foo", b"bar"]

        m_stats = m2.get_match_stats()
        assert isinstance(m_stats, MatchStats)
        assert m_stats.total_hits == len(matches)
        m2.reset_match_stats()
        assert m2.get_match_stats() == MatchStats(0, 0, 0, 0, 0)


def test_compile_from_buffer_and_match(tmp_path):
    pattern_buffer = b"foo\nbar\nbazinga"
    compiled_file = str(tmp_path / "matcher.omg")
    ps_stats = Compiler.compile_from_buffer(compiled_file, pattern_buffer)
    assert isinstance(ps_stats, PatternStoreStats)
    assert ps_stats.smallest_pattern_length == 3
    assert ps_stats.largest_pattern_length == 7
    assert ps_stats.stored_pattern_count == 1
    assert ps_stats.short_pattern_count == 2
    assert ps_stats.total_input_bytes == 13
    assert ps_stats.total_stored_bytes == 7

    with Matcher(compiled_file) as m2:
        haystack = b"xx foobar yy foo zz bar"
        results = m2.match(haystack)
        offsets = [r.offset for r in results]
        matches = [r.match for r in results]
        assert offsets == [3, 6, 13, 20]
        assert matches == [b"foo", b"bar", b"foo", b"bar"]

        m_stats = m2.get_match_stats()
        assert isinstance(m_stats, MatchStats)
        assert m_stats.total_hits == len(matches)
        m2.reset_match_stats()
        assert m2.get_match_stats() == MatchStats(0, 0, 0, 0, 0)


def test_case_insensitive_matching(tmp_path):
    patterns = ["Foo", "BaR"]
    pat_file = tmp_path / "patterns.txt"
    write_file(pat_file, patterns)
    with Matcher(str(pat_file), case_insensitive=True) as m:
        hay = b"foo BAR Baz fooBar"
        results = m.match(hay)
        offsets = [r.offset for r in results]
        matches = [r.match for r in results]
        assert offsets == [0, 4, 12, 15]
        assert matches == [b"foo", b"BAR", b"foo", b"Bar"]


def test_ignore_punctuation_and_case(tmp_path):
    pattern_buffer = b"f'oo\nbar\n"
    compiled_file = str(tmp_path / "matcher.omg")
    Compiler.compile_from_buffer(compiled_file, pattern_buffer, ignore_punctuation=True, case_insensitive=True)
    with Matcher(str(compiled_file)) as m:
        hay = b"f'oo BAR Baz fooBar"
        results = m.match(hay)
        offsets = [r.offset for r in results]
        matches = [r.match for r in results]
        assert offsets == [0, 5, 13, 16]
        assert matches == [b"f'oo", b"BAR", b"foo", b"Bar"]


def test_no_overlap_and_longest_only(tmp_path):
    patterns = ["abc", "abcd"]
    pat_file = tmp_path / "patterns.txt"
    write_file(pat_file, patterns)
    with Matcher(str(pat_file)) as m:
        hay = b"xxabcdyy"
        res = m.match(hay)
        assert any(r.match == b"abc" for r in res)
        assert any(r.match == b"abcd" for r in res)

        res2 = m.match(hay, longest_only=True)
        assert all(r.match == b"abcd" for r in res2)

        res3 = m.match(hay, no_overlap=True)
        assert all(r.match == b"abcd" for r in res3)


def test_word_boundary(tmp_path):
    patterns = ["in", "and"]
    pat_file = tmp_path / "patterns.txt"
    write_file(pat_file, patterns)
    with Matcher(str(pat_file)) as m:
        hay = b"land and inland"
        res_all = m.match(hay)
        assert any(r.match == b"in" for r in res_all)
        assert any(r.match == b"and" for r in res_all)

        res_wb = m.match(hay, word_boundary=True)
        assert len(res_wb) == 1
        assert res_wb[0].match == b"and"
        assert res_wb[0].offset == 5


def test_set_threads(tmp_path):
    patterns = ["foo", "bar"]
    pat_file = tmp_path / "patterns.txt"
    write_file(pat_file, patterns)
    with Matcher(str(pat_file)) as m:
        m.set_threads(4)
        assert m.get_threads() == 4
        m.set_chunk_size(1024)
        assert m.get_chunk_size() == 1024

        haystack = b"xx foobar yy foo zz bar"
        results = m.match(haystack)
        offsets = [r.offset for r in results]
        matches = [r.match for r in results]
        assert offsets == [3, 6, 13, 20]
        assert matches == [b"foo", b"bar", b"foo", b"bar"]

        m.set_threads(0)
        assert m.get_threads() > 0
        m.set_chunk_size(0)
        assert m.get_chunk_size() == 4096

        with pytest.raises(ValueError):
            m.set_threads(-1)
        with pytest.raises(ValueError):
            m.set_chunk_size(-1)
