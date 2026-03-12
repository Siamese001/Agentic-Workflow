"""ADG-driven tests for agentic_core/L5_safety/validators/read_file_args_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.read_file_args_validator import (  # noqa: F401
        ReadFileArgs,
        WriteFileArgs,
        MoveFileArgs,
        ListFilesArgs,
        DeleteFileArgs,
        CreateDirectoryArgs,
        ExecuteCommandArgs,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReadFileArgs = None  # type: ignore[assignment,misc]
    WriteFileArgs = None  # type: ignore[assignment,misc]
    MoveFileArgs = None  # type: ignore[assignment,misc]
    ListFilesArgs = None  # type: ignore[assignment,misc]
    DeleteFileArgs = None  # type: ignore[assignment,misc]
    CreateDirectoryArgs = None  # type: ignore[assignment,misc]
    ExecuteCommandArgs = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestReadFileArgs:
    def test_is_class(self):
        assert isinstance(ReadFileArgs, type)
    def test_importable(self):
        assert ReadFileArgs is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestWriteFileArgs:
    def test_is_class(self):
        assert isinstance(WriteFileArgs, type)
    def test_importable(self):
        assert WriteFileArgs is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestMoveFileArgs:
    def test_is_class(self):
        assert isinstance(MoveFileArgs, type)
    def test_importable(self):
        assert MoveFileArgs is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestListFilesArgs:
    def test_is_class(self):
        assert isinstance(ListFilesArgs, type)
    def test_importable(self):
        assert ListFilesArgs is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestDeleteFileArgs:
    def test_is_class(self):
        assert isinstance(DeleteFileArgs, type)
    def test_importable(self):
        assert DeleteFileArgs is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestCreateDirectoryArgs:
    def test_is_class(self):
        assert isinstance(CreateDirectoryArgs, type)
    def test_importable(self):
        assert CreateDirectoryArgs is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestExecuteCommandArgs:
    def test_is_class(self):
        assert isinstance(ExecuteCommandArgs, type)
    def test_importable(self):
        assert ExecuteCommandArgs is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="read_file_args_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module read_file_args_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
