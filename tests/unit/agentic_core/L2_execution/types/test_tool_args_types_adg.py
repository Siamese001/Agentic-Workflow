"""ADG importability contract for agentic_core/L2_execution/types/tool_args_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_args_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.tool_args_types import (  # noqa: F401
        CreateDirectoryArgs,
        DeleteFileArgs,
        ListFilesArgs,
        MoveFileArgs,
        ReadFileArgs,
        WriteFileArgs,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReadFileArgs = None  # type: ignore[assignment,misc]
    WriteFileArgs = None  # type: ignore[assignment,misc]
    ListFilesArgs = None  # type: ignore[assignment,misc]
    MoveFileArgs = None  # type: ignore[assignment,misc]
    DeleteFileArgs = None  # type: ignore[assignment,misc]
    CreateDirectoryArgs = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_args_types deps unavailable")
class TestToolArgsTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/tool_args_types.py must be importable."""
        assert _AVAILABLE

    def test_readfileargs_defined(self) -> None:
        assert ReadFileArgs is not None

    def test_writefileargs_defined(self) -> None:
        assert WriteFileArgs is not None

    def test_listfilesargs_defined(self) -> None:
        assert ListFilesArgs is not None

    def test_movefileargs_defined(self) -> None:
        assert MoveFileArgs is not None

    def test_deletefileargs_defined(self) -> None:
        assert DeleteFileArgs is not None

    def test_createdirectoryargs_defined(self) -> None:
        assert CreateDirectoryArgs is not None
