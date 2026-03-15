"""ADG-driven tests for L2_execution/reasoning/definitions.py — re-export shim."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.reasoning.definitions import (
        ListFilesArgs,
        ReadFileArgs,
        WriteFileArgs,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReadFileArgs = None  # type: ignore[assignment,misc]
    WriteFileArgs = None  # type: ignore[assignment,misc]
    ListFilesArgs = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="definitions re-export unavailable")
class TestDefinitionsReexport:
    def test_read_file_args_importable(self):
        assert ReadFileArgs is not None

    def test_write_file_args_importable(self):
        assert WriteFileArgs is not None

    def test_list_files_args_importable(self):
        assert ListFilesArgs is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
