"""Golden trace tests for offline replay — Wave 7.0.13.

Validates:
  a) Deterministic replay bundle: identical inputs produce byte-identical JSON.
  b) Drift detection: changing a single event metric_value changes downstream trace_ids.
  c) Fail-closed path: approval=REJECT -> decision=REJECT, change_package/rollout=None.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.config.path_constants import (
    APPS_RG_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_offline_replay_golden")
_emit_applies_guardrail("p0", "test_offline_replay_golden", "p0_governance")
_emit_reads_policy_state("p0", "test_offline_replay_golden", "policy_binding")
_emit_snapshots_state("p0", "test_offline_replay_golden", "state_snapshot")
emit_replay_key("p0", "test_offline_replay_golden")
emit_determinism_digest("p0", "test_offline_replay_golden")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_offline_replay_golden", "execution_auth")
_emit_validates_capability("p2", "test_offline_replay_golden", "capability_check")
_emit_routes_to_capability("p2", "test_offline_replay_golden", "capability_route")
_emit_writes_via_uwg("p2", "test_offline_replay_golden", "uwg_write")
_emit_blocks_direct_write("p2", "test_offline_replay_golden", "direct_write_block")
_emit_records_tool_invocation("p2", "test_offline_replay_golden", "tool_invocation")
_emit_captures_execution_output("p2", "test_offline_replay_golden", "exec_output")
_emit_dispatches_agent("p3", "test_offline_replay_golden", "agent_dispatch")
_emit_coordinates_agents("p3", "test_offline_replay_golden", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_offline_replay_golden", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_offline_replay_golden", "healing_outcome")
_emit_escalates_failure("p3", "test_offline_replay_golden", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_offline_replay_golden", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_offline_replay_golden", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_offline_replay_golden", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_offline_replay_golden", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_offline_replay_golden", "eval_metric")
_emit_stores_embedding("p4", "test_offline_replay_golden", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_offline_replay_golden", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_offline_replay_golden", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from system_learning.types.app_signal_types import (
    AppSignalEventArtifact,
    build_app_signal_event,
)
from system_learning.types.offline_replay_types import (
    OfflineReplayBundle,
    render_offline_replay_bundle,
    replay_aggregate_to_rollout,
    replay_app_signals_to_aggregate,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_offline_replay_golden", "p4obs", "metric_1")
_emit_emits_metric_event("test_offline_replay_golden", "p4obs", "metric_2")
_emit_emits_metric_event("test_offline_replay_golden", "p4obs", "metric_3")
_emit_emits_metric_event("test_offline_replay_golden", "p4obs", "metric_4")
_emit_emits_metric_event("test_offline_replay_golden", "p4obs", "metric_5")
_emit_emits_metric_event("test_offline_replay_golden", "p4obs", "metric_6")
_emit_records_incident_event("test_offline_replay_golden", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_offline_replay_golden", "p4obs", "anomaly")
_emit_writes_observability_log("test_offline_replay_golden", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_offline_replay_golden", "p4obs", "mon_state")
_emit_triggers_alert("test_offline_replay_golden", "p4obs", "alert")
_emit_links_incident_trace("test_offline_replay_golden", "p4obs", "trace_link")
_emit_captures_pattern("test_offline_replay_golden", "p3lm", "pattern")
_emit_records_learning_event("test_offline_replay_golden", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_offline_replay_golden", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_offline_replay_golden", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_offline_replay_golden", "p3lm", "routing")
_emit_improves_agent_policy("test_offline_replay_golden", "p3lm", "policy")
_emit_stores_learning_state("test_offline_replay_golden", "p3lm", "state")
_emit_records_execution_trace("test_offline_replay_golden", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_offline_replay_golden", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_offline_replay_golden", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_offline_replay_golden", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_offline_replay_golden", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_offline_replay_golden", "env_read", "p2_env_1")
_emit_reads_environ("test_offline_replay_golden", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_offline_replay_golden", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_offline_replay_golden", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_offline_replay_golden", "context_pull")
_emit_pulls_context("p1", "test_offline_replay_golden", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_offline_replay_golden", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_offline_replay_golden", "uwg_term_secondary")
_emit_writes_through("p1", "test_offline_replay_golden", "write_through")
_emit_writes_through("p1", "test_offline_replay_golden", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_offline_replay_golden", "safety_validation")
_emit_invokes_eval("p1", "test_offline_replay_golden", "eval_call")
_emit_proposal_commits_routing("p1", "test_offline_replay_golden", "routing_commit")

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


def _make_events(
    values: list[float],
    *,
    prefix: str = "msg",
) -> list[AppSignalEventArtifact]:
    """Helper: build AppSignalEventArtifact list for replay tests."""
    return [
        build_app_signal_event(
            app_id=APPS_RG_DIR,
            run_id="run_golden",
            message_id=f"{prefix}_{i:03d}",
            metric_name="resume_message_response_rate",
            metric_value=v,
            semantic_clock=_CLOCK,
        )
        for i, v in enumerate(values)
    ]


def _build_full_bundle(
    baseline_vals: list[float],
    candidate_vals: list[float],
    *,
    approval_decision: str = "APPROVE",
) -> OfflineReplayBundle:
    """Build a complete replay bundle from baseline/candidate value lists."""
    baseline_events = _make_events(baseline_vals, prefix="bl")
    candidate_events = _make_events(candidate_vals, prefix="cd")
    all_events = baseline_events + candidate_events

    aggregate = replay_app_signals_to_aggregate(
        events=all_events,
        metric_name="resume_message_response_rate",
        app_id=APPS_RG_DIR,
        window_id="w_golden",
        baseline_selector=lambda e: e.message_id.startswith("bl"),
        candidate_selector=lambda e: e.message_id.startswith("cd"),
        evidence_hash="golden_evidence",
        semantic_clock=_CLOCK,
    )

    return replay_aggregate_to_rollout(
        aggregate=aggregate,
        proposer=APPS_RG_DIR,
        target_component="routing_thresholds",
        before={"threshold": 0.5},
        after={"threshold": 0.7},
        evaluator="offline_bench",
        dataset_id="ds_golden",
        eval_evidence_hash="eval_golden",
        approver="human_reviewer",
        approval_decision=approval_decision,
        approval_rationale="Golden trace test.",
        rollout_strategy="ALL_AT_ONCE",
        rollout_invariants=["guardian_green"],
        rollout_max_duration_minutes=60,
        semantic_clock=_CLOCK,
    )


class TestDeterministicReplayBundle:
    def test_identical_inputs_produce_byte_identical_json(self) -> None:
        """Two replay bundles with same inputs produce byte-identical JSON."""
        bundle1 = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.89])
        bundle2 = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.89])

        json1 = render_offline_replay_bundle(bundle1)
        json2 = render_offline_replay_bundle(bundle2)
        assert json1 == json2

        parsed = json.loads(json1)
        assert parsed["proposal"]["artifact_type"] == "META_LEARNING_PROPOSAL"
        assert parsed["decision"]["decision"] == "ALLOW_TO_APPLY"
        assert parsed["rollout_plan"] is not None
        assert parsed["change_package"] is not None
        assert bundle1.rollout_plan is not None
        assert bundle1.rollout_plan.trace_id == bundle2.rollout_plan.trace_id


class TestDriftDetection:
    def test_single_event_change_propagates_trace_ids(self) -> None:
        """Changing a single event metric_value changes downstream trace_ids."""
        bundle_a = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.89])
        bundle_b = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.90])

        assert bundle_a.aggregate.trace_id != bundle_b.aggregate.trace_id
        assert bundle_a.proposal.trace_id != bundle_b.proposal.trace_id
        assert bundle_a.evaluation.trace_id != bundle_b.evaluation.trace_id

        assert bundle_a.change_package is not None
        assert bundle_b.change_package is not None
        assert bundle_a.change_package.trace_id != bundle_b.change_package.trace_id

        assert bundle_a.rollout_plan is not None
        assert bundle_b.rollout_plan is not None
        assert bundle_a.rollout_plan.trace_id != bundle_b.rollout_plan.trace_id


class TestFailClosedPath:
    def test_reject_approval_blocks_change_package_and_rollout(self) -> None:
        """Approval=REJECT -> decision=REJECT, change_package=None, rollout=None."""
        bundle = _build_full_bundle(
            [0.80, 0.82],
            [0.85, 0.87],
            approval_decision="REJECT",
        )
        assert bundle.decision.decision == "REJECT"
        assert bundle.decision.deny_reason == "APPROVAL_REJECTED"
        assert bundle.change_package is None
        assert bundle.rollout_plan is None

        json_str = render_offline_replay_bundle(bundle)
        parsed = json.loads(json_str)
        assert parsed["change_package"] is None
        assert parsed["rollout_plan"] is None
        assert parsed["decision"]["decision"] == "REJECT"

        bundle2 = _build_full_bundle(
            [0.80, 0.82],
            [0.85, 0.87],
            approval_decision="REJECT",
        )
        assert render_offline_replay_bundle(bundle) == render_offline_replay_bundle(bundle2)
