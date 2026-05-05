from pathlib import Path

import pytest

from coding_agent_python.tools import (
    execute_bash,
    grep,
    handle,
    list_directory,
    read_file,
    write_file,
)


class TestReadFile:
    def test_reads_file_contents(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        assert read_file(str(f)) == "1: hello world"

    def test_prefixes_line_numbers(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("line one\nline two\nline three")
        lines = read_file(str(f)).splitlines()
        assert lines[0] == "1: line one"
        assert lines[1] == "2: line two"
        assert lines[2] == "3: line three"

    def test_start_line(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("a\nb\nc")
        result = read_file(str(f), start_line=2)
        assert result == "2: b\n3: c"

    def test_end_line(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("a\nb\nc")
        result = read_file(str(f), end_line=2)
        assert result == "1: a\n2: b"

    def test_start_and_end_line(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("a\nb\nc\nd")
        result = read_file(str(f), start_line=2, end_line=3)
        assert result == "2: b\n3: c"

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_file(str(tmp_path / "nonexistent.txt"))


class TestWriteFile:
    def test_writes_file_contents(self, tmp_path: Path) -> None:
        path = str(tmp_path / "out.txt")
        write_file(path, "content")
        assert Path(path).read_text() == "content"

    def test_returns_byte_count_message(self, tmp_path: Path) -> None:
        path = str(tmp_path / "out.txt")
        result = write_file(path, "hello")
        assert result == f"Wrote 5 bytes to {path}"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        path = str(tmp_path / "a" / "b" / "c.txt")
        write_file(path, "nested")
        assert Path(path).read_text() == "nested"

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        path = str(tmp_path / "file.txt")
        write_file(path, "first")
        write_file(path, "second")
        assert Path(path).read_text() == "second"

    def test_replaces_line_range(self, tmp_path: Path) -> None:
        path = str(tmp_path / "f.txt")
        write_file(path, "a\nb\nc\nd")
        write_file(path, "X", start_line=2, end_line=3)
        assert Path(path).read_text() == "a\nX\nd"

    def test_replace_single_line(self, tmp_path: Path) -> None:
        path = str(tmp_path / "f.txt")
        write_file(path, "a\nb\nc")
        write_file(path, "B", start_line=2, end_line=2)
        assert Path(path).read_text() == "a\nB\nc"

    def test_replace_returns_range_message(self, tmp_path: Path) -> None:
        path = str(tmp_path / "f.txt")
        write_file(path, "a\nb\nc")
        result = write_file(path, "X", start_line=1, end_line=2)
        assert "1" in result and "2" in result

    def test_replace_only_start_line(self, tmp_path: Path) -> None:
        path = str(tmp_path / "f.txt")
        write_file(path, "a\nb\nc")
        write_file(path, "Z", start_line=3, end_line=3)
        assert Path(path).read_text() == "a\nb\nZ\n"


class TestListDirectory:
    def test_lists_files_and_dirs(self, tmp_path: Path) -> None:
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file.txt").write_text("")
        result = list_directory(str(tmp_path))
        lines = result.split("\n")
        assert "subdir/" in lines
        assert "file.txt" in lines

    def test_dirs_listed_before_files(self, tmp_path: Path) -> None:
        (tmp_path / "afile.txt").write_text("")
        (tmp_path / "zdir").mkdir()
        result = list_directory(str(tmp_path))
        lines = result.split("\n")
        assert lines.index("zdir/") < lines.index("afile.txt")

    def test_files_sorted_alphabetically(self, tmp_path: Path) -> None:
        (tmp_path / "b.txt").write_text("")
        (tmp_path / "a.txt").write_text("")
        result = list_directory(str(tmp_path))
        lines = result.split("\n")
        assert lines.index("a.txt") < lines.index("b.txt")


class TestGrep:
    def test_finds_match_in_file(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("hello world\nfoo bar")
        result = grep("hello", path=str(tmp_path))
        assert "hello" in result

    def test_includes_line_numbers(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("first\nsecond\nthird")
        result = grep("second", path=str(tmp_path))
        assert ":2:" in result

    def test_includes_file_path(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("match here")
        result = grep("match", path=str(tmp_path))
        assert "a.txt" in result

    def test_no_matches_returns_placeholder(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("nothing relevant")
        result = grep("zzznomatch", path=str(tmp_path))
        assert result == "(no matches)"

    def test_searches_recursively(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "deep.txt").write_text("deep match")
        result = grep("deep match", path=str(tmp_path))
        assert "deep.txt" in result

    def test_include_filters_by_extension(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("target")
        (tmp_path / "b.txt").write_text("target")
        result = grep("target", path=str(tmp_path), include="*.py")
        assert "a.py" in result
        assert "b.txt" not in result

    def test_regex_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("foo123\nbar456")
        result = grep(r"[0-9]+", path=str(tmp_path))
        assert "foo123" in result
        assert "bar456" in result


class TestExecuteBash:
    def test_returns_stdout(self) -> None:
        result = execute_bash("echo hello")
        assert "hello" in result

    def test_includes_stderr(self) -> None:
        result = execute_bash("echo err >&2")
        assert "stderr" in result
        assert "err" in result

    def test_no_output_returns_placeholder(self) -> None:
        result = execute_bash("true")
        assert result == "(no output)"

    def test_shell_arithmetic(self) -> None:
        result = execute_bash("echo $((1+1))")
        assert "2" in result


class TestHandle:
    def test_routes_read_file(self, tmp_path: Path) -> None:
        f = tmp_path / "x.txt"
        f.write_text("data")
        assert handle("read_file", {"path": str(f)}) == "1: data"

    def test_routes_write_file(self, tmp_path: Path) -> None:
        path = str(tmp_path / "out.txt")
        result = handle("write_file", {"path": path, "content": "hi"})
        assert "Wrote" in result
        assert Path(path).read_text() == "hi"

    def test_routes_list_directory(self, tmp_path: Path) -> None:
        (tmp_path / "file.txt").write_text("")
        result = handle("list_directory", {"path": str(tmp_path)})
        assert "file.txt" in result

    def test_routes_execute_bash(self) -> None:
        result = handle("execute_bash", {"command": "echo test"})
        assert "test" in result

    def test_unknown_tool_returns_message(self) -> None:
        assert handle("unknown_tool", {}) == "Unknown tool: unknown_tool"

    def test_exception_is_caught_and_returned(self) -> None:
        result = handle("read_file", {"path": "/nonexistent/path/file.txt"})
        assert result.startswith("Error:")
