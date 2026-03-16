"""Contract tests for HumanDecisionArtifact (Path D spec [5])."""

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

_emit_records_execution_trace("p0", "evidence", "test_human_decision_artifact")
_emit_applies_guardrail("p0", "test_human_decision_artifact", "p0_governance")
_emit_snapshots_state("p0", "test_human_decision_artifact", "state_snapshot")
emit_replay_key("p0", "test_human_decision_artifact")
emit_determinism_digest("p0", "test_human_decision_artifact")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_human_decision_artifact", "execution_auth")
_emit_validates_capability("p2", "test_human_decision_artifact", "capability_check")
_emit_routes_to_capability("p2", "test_human_decision_artifact", "capability_route")
_emit_writes_via_uwg("p2", "test_human_decision_artifact", "uwg_write")
_emit_blocks_direct_write("p2", "test_human_decision_artifact", "direct_write_block")
_emit_records_tool_invocation("p2", "test_human_decision_artifact", "tool_invocation")
_emit_captures_execution_output("p2", "test_human_decision_artifact", "exec_output")
_emit_dispatches_agent("p3", "test_human_decision_artifact", "agent_dispatch")
_emit_coordinates_agents("p3", "test_human_decision_artifact", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_human_decision_artifact", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_human_decision_artifact", "healing_outcome")
_emit_escalates_failure("p3", "test_human_decision_artifact", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_human_decision_artifact", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_human_decision_artifact", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_human_decision_artifact", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_human_decision_artifact", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_human_decision_artifact", "eval_metric")
_emit_stores_embedding("p4", "test_human_decision_artifact", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_human_decision_artifact", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_human_decision_artifact", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps
from agentic_core.L5_safety.types.human_decision_artifact_types import (
    HumanDecisionArtifact,
    HumanDecisionViolation,
)

SECRET = b"test-l5-secret"


def _make(**kwargs) -> HumanDecisionArtifact:
    defaults = {
        "trace_id": "t1",
        "policy_hash": "ph1",
        "reviewer_id": "r1",
        "action": "APPROVE",
        "structured_patch_schema": {},
        "original_plan_hash": "default-plan-hash",
    }
    return HumanDecisionArtifact(**{**defaults, **kwargs})


def test_approve_roundtrip():
    art = _make().sign(SECRET)
    art.verify(SECRET)  # must not raise
    assert art.action == "APPROVE"


def test_reject_roundtrip():
    art = _make(action="REJECT").sign(SECRET)
    art.verify(SECRET)
    assert art.action == "REJECT"


def test_modify_diff_empty_patch_schema_rejected():
    with pytest.raises(HumanDecisionViolation, match="structured_patch_schema"):
        _make(action="MODIFY_DIFF", structured_patch_schema={})


def test_modify_diff_roundtrip():
    art = _make(
        action="MODIFY_DIFF",
        structured_patch_schema={"file": "x.py", "patch": "@@..."},
    ).sign(SECRET)
    art.verify(SECRET)
    assert art.l5_reclear_required


def test_tampered_sig_rejected():
    art = _make().sign(SECRET)
    tampered = HumanDecisionArtifact(
        trace_id=art.trace_id,
        policy_hash=art.policy_hash,
        reviewer_id=art.reviewer_id,
        action=art.action,
        original_plan_hash=art.original_plan_hash,
        structured_patch_schema=art.structured_patch_schema,
        reviewer_sig="deadbeef" * 8,
    )
    with pytest.raises(HumanDecisionViolation, match="mismatch"):
        tampered.verify(SECRET)


def test_empty_trace_id_rejected():
    with pytest.raises(HumanDecisionViolation, match="trace_id"):
        _make(trace_id="")


def test_approve_does_not_set_reclear():
    art = _make(action="APPROVE")
    assert not art.l5_reclear_required


def test_plan_hash_mismatch_raises():
    art = _make(original_plan_hash="plan-A")
    with pytest.raises(HumanDecisionViolation, match="original_plan_hash"):
        art.assert_plan_hash_matches("plan-B")
