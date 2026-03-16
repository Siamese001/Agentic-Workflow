"""ADG contract tests for L5_safety/types/integrity_validation_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_integrity_validation_types_adg")
_emit_applies_guardrail("p0", "test_integrity_validation_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_integrity_validation_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_integrity_validation_types_adg", "state_snapshot")
emit_replay_key("p0", "test_integrity_validation_types_adg")
emit_determinism_digest("p0", "test_integrity_validation_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.integrity_validation_types import IntegrityResult, IntegrityViolation


class TestIntegrityViolation:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(IntegrityViolation)
    def test_creates(self):
        v = IntegrityViolation(rule="r1", severity="error", description="bad")
        assert v.rule == "r1"; assert v.severity == "error"

class TestIntegrityResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(IntegrityResult)
    def test_valid_by_default(self):
        r = IntegrityResult(valid=True)
        assert r.valid is True; assert r.violations == []
