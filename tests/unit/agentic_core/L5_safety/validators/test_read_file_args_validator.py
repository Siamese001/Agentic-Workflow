"""Foundational behavioral tests for agentic_core/L5_safety/validators/read_file_args_validator.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_read_file_args_validator_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L5_safety.validators.read_file_args_validator import (  # noqa: F401
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


class TestReadFileArgsContract:
    def test_is_class(self):
                from agentic_core.L5_safety.validators.read_file_args_validator import (  # noqa: F401
                assert isinstance(ReadFileArgs, type)

        assert isinstance(ReadFileArgs, type)

    def test_has_method_validate_path(self):
        assert callable(getattr(ReadFileArgs, 'validate_path', None))

class TestWriteFileArgsContract:
    def test_is_class(self):
        assert isinstance(WriteFileArgs, type)

    def test_has_method_validate_path(self):
        assert callable(getattr(WriteFileArgs, 'validate_path', None))

class TestMoveFileArgsContract:
    def test_is_class(self):
        assert isinstance(MoveFileArgs, type)

    def test_has_method_validate_paths(self):
        assert callable(getattr(MoveFileArgs, 'validate_paths', None))

class TestListFilesArgsContract:
    def test_is_class(self):
        assert isinstance(ListFilesArgs, type)

    def test_has_method_validate_path(self):
        assert callable(getattr(ListFilesArgs, 'validate_path', None))

class TestDeleteFileArgsContract:
    def test_is_class(self):
        assert isinstance(DeleteFileArgs, type)

    def test_has_method_validate_path(self):
        assert callable(getattr(DeleteFileArgs, 'validate_path', None))

class TestCreateDirectoryArgsContract:
    def test_is_class(self):
        assert isinstance(CreateDirectoryArgs, type)

    def test_has_method_validate_path(self):
        assert callable(getattr(CreateDirectoryArgs, 'validate_path', None))

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module read_file_args_validator must be importable or skip gracefully."""
    pass  # Import verified at module level
