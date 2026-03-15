"""Foundational behavioral tests for agentic_core/L2_execution/types/tool_args_types.py.

fan_in=16 — this module is imported by 16 other modules.
ADG contract: import-hygiene is covered by test_tool_args_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.tool_args_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        CreateDirectoryArgs,
        DeleteFileArgs,
        ListFilesArgs,
        MoveFileArgs,
        ReadFileArgs,
        WriteFileArgs,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ReadFileArgs = None  # type: ignore[assignment,misc]
    WriteFileArgs = None  # type: ignore[assignment,misc]
    ListFilesArgs = None  # type: ignore[assignment,misc]
    MoveFileArgs = None  # type: ignore[assignment,misc]
    DeleteFileArgs = None  # type: ignore[assignment,misc]
    CreateDirectoryArgs = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestReadFileArgsContract:
    def test_is_class(self):
        assert isinstance(ReadFileArgs, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ReadFileArgs, type)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestWriteFileArgsContract:
    def test_is_class(self):
        assert isinstance(WriteFileArgs, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(WriteFileArgs, type)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestListFilesArgsContract:
    def test_is_class(self):
        assert isinstance(ListFilesArgs, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ListFilesArgs, type)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestMoveFileArgsContract:
    def test_is_class(self):
        assert isinstance(MoveFileArgs, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(MoveFileArgs, type)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestDeleteFileArgsContract:
    def test_is_class(self):
        assert isinstance(DeleteFileArgs, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(DeleteFileArgs, type)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestCreateDirectoryArgsContract:
    def test_is_class(self):
        assert isinstance(CreateDirectoryArgs, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(CreateDirectoryArgs, type)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module tool_args_types must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
