"""ADG-driven tests for agentic_core/L2_execution/types/tool_enforcement_types.py — fan_in=2.

Contract tests: LawSlotOutcome, ToolEnforcementArtifact, ToolPolicyBlocked.
"""
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

_emit_records_execution_trace("p0", "evidence", "test_tool_enforcement_types_adg")
_emit_applies_guardrail("p0", "test_tool_enforcement_types_adg", "p0_governance")
_emit_snapshots_state("p0", "test_tool_enforcement_types_adg", "state_snapshot")
emit_replay_key("p0", "test_tool_enforcement_types_adg")
emit_determinism_digest("p0", "test_tool_enforcement_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_tool_enforcement_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_tool_enforcement_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_tool_enforcement_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_tool_enforcement_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_tool_enforcement_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_tool_enforcement_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_tool_enforcement_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_tool_enforcement_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_tool_enforcement_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_tool_enforcement_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_tool_enforcement_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_tool_enforcement_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_tool_enforcement_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_tool_enforcement_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_tool_enforcement_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_tool_enforcement_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_tool_enforcement_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_tool_enforcement_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_tool_enforcement_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_tool_enforcement_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.tool_enforcement_types import (
    LawSlotOutcome,
    ToolEnforcementArtifact,
    ToolPolicyBlocked,
)


def _make_artifact(**kw) -> ToolEnforcementArtifact:
    return ToolEnforcementArtifact(
        enforcement_id=kw.get("enforcement_id", "eid-001"),
        timestamp_utc=kw.get("timestamp_utc", "2024-01-01T00:00:00Z"),
        trace_id=kw.get("trace_id", "trace-001"),
        agent_id=kw.get("agent_id", "TestAgent"),
        tool_name=kw.get("tool_name", "write_file"),
        outcome=kw.get("outcome", LawSlotOutcome.PASS),
        applied_law_slots=kw.get("applied_law_slots", ("slot_a",)),
        rationale=kw.get("rationale", "Policy satisfied"),
        original_args_hash=kw.get("original_args_hash", "abc123"),
        modified_args_hash=kw.get("modified_args_hash", ""),
        policy_context_hash=kw.get("policy_context_hash", ""),
    )


class TestLawSlotOutcome:
    def test_pass_value(self):
        assert LawSlotOutcome.PASS.value == "pass"

    def test_block_value(self):
        assert LawSlotOutcome.BLOCK.value == "block"

    def test_modify_value(self):
        assert LawSlotOutcome.MODIFY.value == "modify"

    def test_all_three_members(self):
        assert len(LawSlotOutcome) == 3


class TestToolEnforcementArtifact:
    def test_valid_pass_artifact(self):
        a = _make_artifact()
        assert a.outcome == LawSlotOutcome.PASS
        assert a.tool_name == "write_file"

    def test_frozen(self):
        a = _make_artifact()
        with pytest.raises(Exception):
            a.tool_name = "other"  # type: ignore[misc]

    def test_empty_enforcement_id_raises(self):
        with pytest.raises(ValueError, match="enforcement_id"):
            _make_artifact(enforcement_id="")

    def test_empty_trace_id_raises(self):
        with pytest.raises(ValueError, match="trace_id"):
            _make_artifact(trace_id="")

    def test_empty_tool_name_raises(self):
        with pytest.raises(ValueError, match="tool_name"):
            _make_artifact(tool_name="")

    def test_wrong_outcome_type_raises(self):
        with pytest.raises(TypeError, match="outcome"):
            _make_artifact(outcome="pass")  # type: ignore[arg-type]

    def test_modify_without_modified_hash_raises(self):
        with pytest.raises(ValueError, match="modified_args_hash"):
            _make_artifact(outcome=LawSlotOutcome.MODIFY, modified_args_hash="")

    def test_modify_with_modified_hash_ok(self):
        a = _make_artifact(outcome=LawSlotOutcome.MODIFY, modified_args_hash="def456")
        assert a.outcome == LawSlotOutcome.MODIFY
        assert a.modified_args_hash == "def456"

    def test_block_outcome_ok(self):
        a = _make_artifact(outcome=LawSlotOutcome.BLOCK)
        assert a.outcome == LawSlotOutcome.BLOCK

    def test_empty_original_args_hash_raises(self):
        with pytest.raises(ValueError, match="original_args_hash"):
            _make_artifact(original_args_hash="")


class TestToolPolicyBlocked:
    def test_is_exception(self):
        assert issubclass(ToolPolicyBlocked, Exception)

    def test_attributes_stored(self):
        artifact = _make_artifact(outcome=LawSlotOutcome.BLOCK)
        err = ToolPolicyBlocked(
            tool_name="write_file",
            rationale="Blocked by policy",
            artifact=artifact,
        )
        assert err.tool_name == "write_file"
        assert err.rationale == "Blocked by policy"
        assert err.artifact is artifact

    def test_message_contains_tool_name(self):
        artifact = _make_artifact(outcome=LawSlotOutcome.BLOCK)
        err = ToolPolicyBlocked("my_tool", "some reason", artifact)
        assert "my_tool" in str(err)

    def test_can_be_raised(self):
        artifact = _make_artifact(outcome=LawSlotOutcome.BLOCK)
        with pytest.raises(ToolPolicyBlocked):
            raise ToolPolicyBlocked("t", "blocked", artifact)
