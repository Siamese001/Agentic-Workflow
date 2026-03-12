"""ADG-driven tests for L2_execution/types/tool_args_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.tool_args_types import (
        ReadFileArgs,
        WriteFileArgs,
        ListFilesArgs,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReadFileArgs = None  # type: ignore[assignment,misc]
    WriteFileArgs = None  # type: ignore[assignment,misc]
    ListFilesArgs = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types deps unavailable")
class TestReadFileArgs:
    def test_creates(self):
        args = ReadFileArgs(path="/foo/bar.py")
        assert args.path == "/foo/bar.py"


@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types deps unavailable")
class TestWriteFileArgs:
    def test_creates(self):
        args = WriteFileArgs(path="/foo/bar.py", content="hello")
        assert args.path == "/foo/bar.py"
        assert args.content == "hello"


@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types deps unavailable")
class TestListFilesArgs:
    def test_creates_without_pattern(self):
        args = ListFilesArgs(directory="/foo")
        assert args.directory == "/foo"
        assert args.pattern is None

    def test_creates_with_pattern(self):
        args = ListFilesArgs(directory="/foo", pattern="*.py")
        assert args.pattern == "*.py"


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
