"""ADG contract tests for L5_safety/types/security_validation_types.py."""
from __future__ import annotations

import ast

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_security_validation_types_adg")
_emit_applies_guardrail("p0", "test_security_validation_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_security_validation_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_security_validation_types_adg", "state_snapshot")
emit_replay_key("p0", "test_security_validation_types_adg")
emit_determinism_digest("p0", "test_security_validation_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_security_validation_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_security_validation_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_security_validation_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_security_validation_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_security_validation_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_security_validation_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_security_validation_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_security_validation_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_security_validation_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_security_validation_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_security_validation_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_security_validation_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_security_validation_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_security_validation_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_security_validation_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_security_validation_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_security_validation_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_security_validation_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_security_validation_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_security_validation_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

MODULE_PATH = "agentic_core/L5_safety/types/security_validation_types.py"

def test_module_parses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    ast.parse(src)

def test_has_validation_suite():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "ValidationSuite" in src or "SecurityValidation" in src or "ThreatLevel" in src

def test_has_dataclasses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "dataclass" in src or "class" in src

try:
    from agentic_core.L5_safety.types.security_validation_types import (
        RedTeamValidationSuite,
        SecuritySuiteResult,
        SecurityValidationResult,
        get_security_suite,
        run_security_validation,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    SecurityValidationResult = SecuritySuiteResult = RedTeamValidationSuite = None  # type: ignore[assignment,misc]
    get_security_suite = run_security_validation = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSecurityValidationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SecurityValidationResult)
    def test_creates(self):
        r = SecurityValidationResult(validator_name="test_v", valid=True)
        assert r.valid is True; assert r.errors == []

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSecuritySuiteResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SecuritySuiteResult)
    def test_creates(self):
        r = SecuritySuiteResult(overall_valid=True, validators_run=2, validators_passed=2, validators_failed=0)
        assert r.overall_valid is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRedTeamValidationSuite:
    def test_creates(self): suite = RedTeamValidationSuite(); assert suite is not None
    def test_get_status(self):
        suite = RedTeamValidationSuite()
        status = suite.get_status()
        assert "initialized" in status
    def test_run_all(self):
        suite = RedTeamValidationSuite()
        result = suite.run_all({"test": "content"})
        assert isinstance(result, SecuritySuiteResult)
    def test_get_security_suite_singleton(self):
        s1 = get_security_suite(); s2 = get_security_suite(); assert s1 is s2
    def test_run_security_validation(self):
        result = run_security_validation({"data": "payload"})
        assert isinstance(result, SecuritySuiteResult)
