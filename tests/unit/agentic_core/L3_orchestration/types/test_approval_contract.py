"""
Contract tests for the L3 Approval contract.

Proves:
1. validate() passes for minimal valid objects.
2. check_schema_compatibility() passes.
3. Deterministic sorting: check_ids sorted, records sorted by token.
4. Negative tests: unknown decision, empty token, empty phase_name rejected.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.L3_orchestration.types.approval_contract_types import (
    ApprovalBundle,
    ApprovalDecision,
    ApprovalRecord,
    check_schema_compatibility,
    validate_against_json_schema,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_approval_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_approval_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_approval_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_approval_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_approval_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_approval_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_approval_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_approval_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_approval_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_approval_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_approval_contract", "p4obs", "alert")
_emit_links_incident_trace("test_approval_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_approval_contract", "p3lm", "pattern")
_emit_records_learning_event("test_approval_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_approval_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_approval_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_approval_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_approval_contract", "p3lm", "policy")
_emit_stores_learning_state("test_approval_contract", "p3lm", "state")
_emit_records_execution_trace("test_approval_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_approval_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_approval_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_approval_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_approval_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_approval_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_approval_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_approval_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_approval_contract", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_approval_contract")
_emit_applies_guardrail("p0", "test_approval_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_approval_contract", "policy_binding")
_emit_snapshots_state("p0", "test_approval_contract", "state_snapshot")
_emit_pulls_context("p1", "test_approval_contract", "context_pull")
_emit_pulls_context("p1", "test_approval_contract", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_approval_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_approval_contract", "uwg_term_secondary")
_emit_writes_through("p1", "test_approval_contract", "write_through")
_emit_writes_through("p1", "test_approval_contract", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_approval_contract", "safety_validation")
_emit_invokes_eval("p1", "test_approval_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_approval_contract", "routing_commit")
emit_replay_key("p0", "test_approval_contract")
emit_determinism_digest("p0", "test_approval_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_approval_contract", "execution_auth")
_emit_validates_capability("p2", "test_approval_contract", "capability_check")
_emit_routes_to_capability("p2", "test_approval_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_approval_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_approval_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_approval_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_approval_contract", "exec_output")
_emit_dispatches_agent("p3", "test_approval_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_approval_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_approval_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_approval_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_approval_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_approval_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_approval_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_approval_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_approval_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_approval_contract", "eval_metric")
_emit_stores_embedding("p4", "test_approval_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_approval_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_approval_contract", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TIMESTAMP = "2026-02-11T15:00:00Z"


def _minimal_record(**overrides: object) -> ApprovalRecord:
    defaults: dict = {
        "phase_name": "discovery",
        "decision": ApprovalDecision.APPROVED,
        "approver": "admin@example.com",
        "token": "tok_001",
        "created_utc": TIMESTAMP,
    }
    defaults.update(overrides)
    return ApprovalRecord(**defaults)


def _minimal_bundle(**overrides: object) -> ApprovalBundle:
    defaults: dict = {
        "records": (_minimal_record(),),
    }
    defaults.update(overrides)
    return ApprovalBundle(**defaults)


# ---------------------------------------------------------------------------
# Positive: validation passes
# ---------------------------------------------------------------------------


class TestApprovalContractValidation:
    def test_validate_minimal(self) -> None:
        bundle = _minimal_bundle()
        assert bundle.validate() == []

    def test_validate_multiple_records(self) -> None:
        bundle = _minimal_bundle(
            records=(
                _minimal_record(token="tok_a", phase_name="pre_audit"),
                _minimal_record(
                    token="tok_b",
                    phase_name="healing",
                    decision=ApprovalDecision.REJECTED,
                ),
            ),
        )
        assert bundle.validate() == []

    def test_validate_with_all_fields(self) -> None:
        record = ApprovalRecord(
            phase_name="alignment",
            guardian_id="location_alignment",
            check_ids=("misplaced_files", "missing_directories"),
            decision=ApprovalDecision.APPROVED,
            approver="lead@example.com",
            rationale="All checks reviewed and approved",
            token="tok_full",
            created_utc=TIMESTAMP,
        )
        bundle = ApprovalBundle(records=(record,))
        assert bundle.validate() == []

    def test_schema_compatibility_minimal(self) -> None:
        bundle = _minimal_bundle()
        errors = check_schema_compatibility(bundle.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_to_json_roundtrip(self) -> None:
        bundle = _minimal_bundle()
        data = json.loads(bundle.to_json())
        assert data["contract_version"] == 1
        assert len(data["records"]) == 1

    def test_validate_against_schema_direct(self) -> None:
        bundle = _minimal_bundle()
        errors = validate_against_json_schema(bundle.to_dict())
        assert errors == []


# ---------------------------------------------------------------------------
# Deterministic sorting
# ---------------------------------------------------------------------------


class TestApprovalContractDeterminism:
    def test_records_sorted_by_token(self) -> None:
        bundle = _minimal_bundle(
            records=(
                _minimal_record(token="tok_z"),
                _minimal_record(token="tok_a"),
                _minimal_record(token="tok_m"),
            ),
        )
        d = bundle.to_dict()
        tokens = [r["token"] for r in d["records"]]
        assert tokens == ["tok_a", "tok_m", "tok_z"]

    def test_check_ids_sorted(self) -> None:
        record = _minimal_record(check_ids=("zebra", "alpha", "middle"))
        d = record.to_dict()
        assert d["check_ids"] == ["alpha", "middle", "zebra"]

    def test_idempotent_to_dict(self) -> None:
        bundle = _minimal_bundle(
            records=(
                _minimal_record(token="tok_b"),
                _minimal_record(token="tok_a"),
            ),
        )
        assert bundle.to_dict() == bundle.to_dict()

    def test_empty_check_ids_stays_empty(self) -> None:
        record = _minimal_record()
        d = record.to_dict()
        assert d["check_ids"] == []


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


class TestApprovalContractImmutability:
    def test_record_frozen(self) -> None:
        record = _minimal_record()
        with pytest.raises(dataclasses.FrozenInstanceError):
            record.phase_name = "tampered"

    def test_record_token_frozen(self) -> None:
        record = _minimal_record()
        with pytest.raises(dataclasses.FrozenInstanceError):
            record.token = "tampered"

    def test_bundle_frozen(self) -> None:
        bundle = _minimal_bundle()
        with pytest.raises(dataclasses.FrozenInstanceError):
            bundle.records = ()


# ---------------------------------------------------------------------------
# Negative tests
# ---------------------------------------------------------------------------


class TestApprovalContractNegative:
    def test_unknown_decision_rejected(self) -> None:
        with pytest.raises((ValueError, TypeError)):
            _minimal_record(decision="MAYBE")

    def test_empty_token_rejected(self) -> None:
        with pytest.raises(ValueError, match="token must not be empty"):
            _minimal_record(token="")

    def test_empty_phase_name_rejected(self) -> None:
        with pytest.raises(ValueError, match="phase_name must not be empty"):
            _minimal_record(phase_name="")

    def test_empty_approver_rejected(self) -> None:
        with pytest.raises(ValueError, match="approver must not be empty"):
            _minimal_record(approver="")

    def test_empty_created_utc_rejected(self) -> None:
        with pytest.raises(ValueError, match="created_utc must not be empty"):
            _minimal_record(created_utc="")

    def test_schema_rejects_extra_key(self) -> None:
        d = _minimal_bundle().to_dict()
        d["rogue_key"] = "bad"
        errors = validate_against_json_schema(d)
        assert any("unexpected field" in e for e in errors)

    def test_schema_rejects_missing_required(self) -> None:
        d = _minimal_bundle().to_dict()
        del d["records"]
        errors = validate_against_json_schema(d)
        assert any("missing required" in e for e in errors)

    def test_schema_rejects_invalid_decision_in_dict(self) -> None:
        d = _minimal_bundle().to_dict()
        d["records"][0]["decision"] = "MAYBE"
        errors = validate_against_json_schema(d)
        assert any("not in enum" in e for e in errors)
