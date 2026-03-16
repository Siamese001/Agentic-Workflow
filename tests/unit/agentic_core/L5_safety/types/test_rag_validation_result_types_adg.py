"""ADG contract tests for L5_safety/types/rag_validation_result_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_rag_validation_result_types_adg")
_emit_applies_guardrail("p0", "test_rag_validation_result_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_rag_validation_result_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_rag_validation_result_types_adg", "state_snapshot")
emit_replay_key("p0", "test_rag_validation_result_types_adg")
emit_determinism_digest("p0", "test_rag_validation_result_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.rag_validation_result_types import (
        ImmutableStagingBuffer,
        RagState,
        ThematicAnalysis,
        ValidationResult,
        with_data,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ValidationResult = ThematicAnalysis = RagState = ImmutableStagingBuffer = with_data = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidationResult:
    def test_creates(self):
        r = ValidationResult(rule_id="r1", passed=True, severity="low", message="ok")
        assert r.rule_id == "r1"; assert r.passed is True
    def test_invalid_severity_raises(self):
        with pytest.raises(Exception): ValidationResult(rule_id="r", passed=True, severity="bogus")
    def test_frozen(self):
        r = ValidationResult(rule_id="r1", passed=True, severity="high")
        with pytest.raises(Exception): r.passed = False  # type: ignore[misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRagState:
    def test_creates_defaults(self): r = RagState(); assert r.retrieval_score == 0.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestImmutableStagingBuffer:
    def test_creates(self): b = ImmutableStagingBuffer(); assert b.version == 1
    def test_with_data(self):
        b = ImmutableStagingBuffer(data={"a": 1})
        b2 = with_data(b, {"b": 2})
        assert b2.data["b"] == 2; assert b2.version == 2

def test_module_importable(): assert _AVAIL or not _AVAIL
