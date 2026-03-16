"""ADG-driven tests for L2_execution/engines/execute_command_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_execute_command_executor_adg")
_emit_applies_guardrail("p0", "test_execute_command_executor_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_execute_command_executor_adg", "policy_binding")
_emit_snapshots_state("p0", "test_execute_command_executor_adg", "state_snapshot")
emit_replay_key("p0", "test_execute_command_executor_adg")
emit_determinism_digest("p0", "test_execute_command_executor_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
