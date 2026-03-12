"""ADG-driven tests for L2 execution file_io_impl — fan_in=1."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.tools.file_io_impl import FileIo


class TestFileIoInit:
    def test_creates(self):
        fio = FileIo()
        assert fio is not None

    def test_has_read_file(self):
        assert hasattr(FileIo, "read_file")

    def test_has_save_file(self):
        assert hasattr(FileIo, "save_file")


class TestFileIoReadFile:
    def setup_method(self):
        self.fio = FileIo()

    def test_read_missing_file_returns_error_str(self):
        result = self.fio.read_file("/nonexistent_xyz/foo.txt")
        assert isinstance(result, str)
        assert "Error" in result or "error" in result.lower()

    def test_read_existing_text_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("hello world")
            tmp = f.name
        try:
            result = self.fio.read_file(tmp)
            assert result == "hello world"
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_read_md_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Title\ncontent")
            tmp = f.name
        try:
            result = self.fio.read_file(tmp)
            assert "Title" in result
        finally:
            Path(tmp).unlink(missing_ok=True)


class TestFileIoSaveFile:
    def setup_method(self):
        self.fio = FileIo()

    def test_save_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "output.txt")
            result = self.fio.save_file("test content", path)
            assert isinstance(result, str)
            assert Path(path).exists()

    def test_save_writes_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "out.txt")
            self.fio.save_file("saved content", path)
            assert Path(path).read_text(encoding="utf-8") == "saved content"
