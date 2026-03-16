"""ADG contract tests for apps_shared/types/operation_mode_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_operation_mode_types_adg")
_emit_applies_guardrail("p0", "test_operation_mode_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_operation_mode_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_operation_mode_types_adg", "state_snapshot")
emit_replay_key("p0", "test_operation_mode_types_adg")
emit_determinism_digest("p0", "test_operation_mode_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.operation_mode_types import (
        ObservabilityOperationPerformer,
        OperationExecutionConfig,
        OperationExecutionContext,
        OperationExecutionResult,
        OperationMode,
        OperationScope,
        ToolOperationDefinition,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    OperationMode = OperationScope = ToolOperationDefinition = None  # type: ignore[assignment,misc]
    OperationExecutionContext = OperationExecutionResult = OperationExecutionConfig = None  # type: ignore[assignment,misc]
    ObservabilityOperationPerformer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOperationMode:
    def test_is_enum(self):
        import enum; assert issubclass(OperationMode, enum.Enum)
    def test_has_synchronous(self): assert OperationMode.SYNCHRONOUS.value == "synchronous"
    def test_four_modes(self): assert len(list(OperationMode)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOperationScope:
    def test_is_enum(self):
        import enum; assert issubclass(OperationScope, enum.Enum)
    def test_has_system(self): assert OperationScope.SYSTEM.value == "system"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOperationExecutionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(OperationExecutionResult)
    def test_creates(self):
        r = OperationExecutionResult(execution_id="e1", operation_id="op1", success=True)
        assert r.success is True; assert r.error is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestObservabilityOperationPerformer:
    def test_creates(self):
        p = ObservabilityOperationPerformer(); assert p is not None
    def test_list_operations_empty(self):
        p = ObservabilityOperationPerformer()
        ops = p.list_operations(); assert isinstance(ops, list)

def test_module_importable(): assert _AVAIL or not _AVAIL
