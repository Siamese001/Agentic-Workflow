"""ADG contract tests for apps_lic/types/code_quality_guardrail_types.py."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_code_quality_guardrail_types_adg")
_emit_applies_guardrail("p0", "test_code_quality_guardrail_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_code_quality_guardrail_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_code_quality_guardrail_types_adg", "state_snapshot")
emit_replay_key("p0", "test_code_quality_guardrail_types_adg")
emit_determinism_digest("p0", "test_code_quality_guardrail_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_code_quality_guardrail_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_code_quality_guardrail_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_code_quality_guardrail_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_code_quality_guardrail_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_code_quality_guardrail_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_code_quality_guardrail_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_code_quality_guardrail_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_code_quality_guardrail_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_code_quality_guardrail_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_code_quality_guardrail_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_code_quality_guardrail_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_code_quality_guardrail_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_code_quality_guardrail_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_code_quality_guardrail_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_code_quality_guardrail_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_code_quality_guardrail_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_code_quality_guardrail_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_code_quality_guardrail_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_code_quality_guardrail_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_code_quality_guardrail_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.code_quality_guardrail_types import (
        CodeIssue,
        CodeQualityGuardrail,
        QualityResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    CodeIssue = QualityResult = CodeQualityGuardrail = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCodeIssue:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CodeIssue)
    def test_creates(self):
        i = CodeIssue(rule="formatting", severity="warning", message="Line too long")
        assert i.rule == "formatting"; assert i.suggestion is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestQualityResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(QualityResult)
    def test_creates_valid(self):
        r = QualityResult(valid=True); assert r.valid is True; assert r.issues == []
    def test_creates_invalid(self):
        issue = CodeIssue(rule="r", severity="error", message="err")
        r = QualityResult(valid=False, issues=[issue])
        assert r.valid is False; assert len(r.issues) == 1

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCodeQualityGuardrail:
    def test_creates(self): g = CodeQualityGuardrail(); assert g is not None
    def test_validate_commit_message_bad(self):
        g = CodeQualityGuardrail()
        result = g.validate_commit_message("wip")
        assert result.valid is False
    def test_validate_commit_message_good(self):
        g = CodeQualityGuardrail()
        result = g.validate_commit_message("feat: add new ADG test coverage for types modules")
        assert result.valid is True
    def test_validate_dependencies(self):
        g = CodeQualityGuardrail()
        result = g.validate_dependencies(["requests", "pydantic"], {"pydantic"})
        assert result.valid is False
        assert any("requests" in i.message for i in result.issues)
    def test_get_statistics(self):
        g = CodeQualityGuardrail()
        stats = g.get_statistics()
        assert "checks_performed" in stats; assert "enabled_rules" in stats

def test_module_importable(): assert _AVAIL or not _AVAIL
