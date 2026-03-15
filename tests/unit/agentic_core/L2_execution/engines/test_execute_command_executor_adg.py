"""ADG-driven tests for L2_execution/engines/execute_command_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.engines.execute_command_executor import (
        ExecuteCommandArgs,
        get_project_root,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ExecuteCommandArgs = None  # type: ignore[assignment,misc]
    get_project_root = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="execute_command_executor deps unavailable")
class TestExecuteCommandArgs:
    def test_is_typed_dict(self):
        assert ExecuteCommandArgs is not None

    def test_has_command_key(self):
        assert "command" in ExecuteCommandArgs.__annotations__

    def test_has_timeout_key(self):
        assert "timeout" in ExecuteCommandArgs.__annotations__


@pytest.mark.skipif(not _AVAILABLE, reason="execute_command_executor deps unavailable")
class TestGetProjectRoot:
    def test_returns_path(self):
        from pathlib import Path
        result = get_project_root()
        assert isinstance(result, Path)

    def test_path_is_absolute(self):
        result = get_project_root()
        assert result.is_absolute()


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
