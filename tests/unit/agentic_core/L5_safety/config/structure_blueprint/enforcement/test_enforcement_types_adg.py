"""ADG-driven tests for L5 structure_blueprint/enforcement/types.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_enforcement_types_adg")
_emit_applies_guardrail("p0", "test_enforcement_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_enforcement_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_enforcement_types_adg", "state_snapshot")
emit_replay_key("p0", "test_enforcement_types_adg")
emit_determinism_digest("p0", "test_enforcement_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
    VERIFIER_VERSION,
    Violation,
    make_result,
)


class TestViolation:
    def test_creates(self):
        v: Violation = {"type": "layer_gravity", "path": "foo.py", "severity": "error", "detail": "upward import"}
        assert v["type"] == "layer_gravity"
        assert v["severity"] == "error"


class TestEnforcementResult:
    def test_make_result_no_violations_passes(self):
        result = make_result("test_check", [], {"files_checked": 10})
        assert result["passed"] is True
        assert result["name"] == "test_check"

    def test_make_result_error_violation_fails(self):
        v: Violation = {"type": "x", "path": "foo.py", "severity": "error", "detail": "bad"}
        result = make_result("test_check", [v], {"files_checked": 1})
        assert result["passed"] is False

    def test_make_result_warning_violation_passes(self):
        v: Violation = {"type": "x", "path": "foo.py", "severity": "warning", "detail": "warn"}
        result = make_result("test_check", [v], {})
        assert result["passed"] is True

    def test_make_result_violations_preserved(self):
        v: Violation = {"type": "x", "path": "foo.py", "severity": "error", "detail": "d"}
        result = make_result("chk", [v], {})
        assert len(result["violations"]) == 1


class TestVerifierVersion:
    def test_is_string(self):
        assert isinstance(VERIFIER_VERSION, str)

    def test_non_empty(self):
        assert len(VERIFIER_VERSION) > 0
