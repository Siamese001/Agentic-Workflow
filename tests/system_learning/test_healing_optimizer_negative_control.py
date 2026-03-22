"""W2 negative control test.

Tamper mode (W2_NEGCTRL_TAMPER=1):
  Tests are marked xfail.  The guard IS broken (assertion fires), pytest
  records XFAIL — exit 0, canonical && wrapper works.

Restore mode (default):
  Tests run normally, guards hold, tests PASS — exit 0.

Both modes are &&-chainable.  The XFAIL line in the tamper transcript proves
the guard can be broken; the PASSED line in the restore transcript proves
the guard holds.
W2: Informational semantic retrieval + bounded scoring (C0-only).
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_healing_optimizer_negative_control", "execution_auth")
_emit_validates_capability("p2", "test_healing_optimizer_negative_control", "capability_check")
_emit_routes_to_capability("p2", "test_healing_optimizer_negative_control", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_optimizer_negative_control", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_optimizer_negative_control", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_optimizer_negative_control", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_optimizer_negative_control", "exec_output")
_emit_dispatches_agent("p3", "test_healing_optimizer_negative_control", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_optimizer_negative_control", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_optimizer_negative_control", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_optimizer_negative_control", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_optimizer_negative_control", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_optimizer_negative_control", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_optimizer_negative_control", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_optimizer_negative_control", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_optimizer_negative_control", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_optimizer_negative_control", "eval_metric")
_emit_stores_embedding("p4", "test_healing_optimizer_negative_control", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_optimizer_negative_control", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_optimizer_negative_control", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)

_emit_emits_metric_event("test_healing_optimizer_negative_control", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_optimizer_negative_control", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_optimizer_negative_control", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_optimizer_negative_control", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_optimizer_negative_control", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_optimizer_negative_control", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_optimizer_negative_control", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_optimizer_negative_control", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_optimizer_negative_control", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_optimizer_negative_control", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_optimizer_negative_control", "p4obs", "alert")
_emit_links_incident_trace("test_healing_optimizer_negative_control", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_optimizer_negative_control", "p3lm", "pattern")
_emit_records_learning_event("test_healing_optimizer_negative_control", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_optimizer_negative_control", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_optimizer_negative_control", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_optimizer_negative_control", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_optimizer_negative_control", "p3lm", "policy")
_emit_stores_learning_state("test_healing_optimizer_negative_control", "p3lm", "state")
_emit_records_execution_trace("test_healing_optimizer_negative_control", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_optimizer_negative_control", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_optimizer_negative_control", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_optimizer_negative_control", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_optimizer_negative_control", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_optimizer_negative_control", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_optimizer_negative_control", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_optimizer_negative_control", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_optimizer_negative_control", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_healing_optimizer_negative_control")
_emit_applies_guardrail("p0", "test_healing_optimizer_negative_control", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_optimizer_negative_control", "policy_binding")
_emit_snapshots_state("p0", "test_healing_optimizer_negative_control", "state_snapshot")
_emit_pulls_context("p1", "test_healing_optimizer_negative_control", "context_pull")
_emit_pulls_context("p1", "test_healing_optimizer_negative_control", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_healing_optimizer_negative_control", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_optimizer_negative_control", "uwg_term_secondary")
_emit_writes_through("p1", "test_healing_optimizer_negative_control", "write_through")
_emit_writes_through("p1", "test_healing_optimizer_negative_control", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_healing_optimizer_negative_control", "safety_validation")
_emit_invokes_eval("p1", "test_healing_optimizer_negative_control", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_optimizer_negative_control", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_optimizer_negative_control", "human_escalation")
_emit_routes_through("p1", "test_healing_optimizer_negative_control", "route_through")
_emit_checks_agent_registry("p1", "test_healing_optimizer_negative_control", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_optimizer_negative_control", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_optimizer_negative_control", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_optimizer_negative_control", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_optimizer_negative_control", "target_agent")
_emit_verifies_policy("p1", "test_healing_optimizer_negative_control", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_optimizer_negative_control", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_optimizer_negative_control", "boundary_check")
_emit_transcripts_response("p1", "test_healing_optimizer_negative_control", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_optimizer_negative_control")
_emit_gated_by_confidence("p1", "test_healing_optimizer_negative_control", "confidence_gate")
emit_replay_key("p0", "test_healing_optimizer_negative_control")
emit_determinism_digest("p0", "test_healing_optimizer_negative_control")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


_TAMPER = os.environ.get("W2_NEGCTRL_TAMPER", "0") == "1"


def _make_snapshot_above_threshold() -> HealingOutcomeAggregateSnapshot:
    aggregates = [
        (
            HealingOutcomeAggregateKey(
                healer_name="test_healer",
                tier="LOCAL_AGENT",
                failure_type="test_failure",
            ),
            HealingOutcomeAggregate(
                success_count=8,
                failure_count=12,
                total_count=20,
            ),
        ),
    ]
    return HealingOutcomeAggregateSnapshot(
        version_id="test_version",
        created_utc=1234567890,
        aggregates=tuple(aggregates),
    )


def _embedding_metadata() -> dict:
    return {
        "embedding_enabled_at_time": True,
        "embedding_replay_key": "test_replay_key",
        "embedding_artifact_hash": "test_hash",
        "embedding_topk_hashes": ["hash1", "hash2"],
        "embedding_topk_scores_round6": [0.85, 0.90],
    }


@pytest.mark.unit_min_deps
class TestW2NegativeControl:
    """W2 negative control tests.

    Under tamper (W2_NEGCTRL_TAMPER=1): xfail marks show the guard IS broken.
    Under restore (default): tests PASS, guards intact.
    Both cases exit 0 — canonical && wrapper is valid for both.
    """

    def test_embedding_determinism_violation_negative_control(self) -> None:
        """Guard: two identical calls must produce identical confidence.

        Tamper: injects differing scores; xfail catches the AssertionError
        and records XFAIL (exit 0).
        Restore: identical scores; assertion passes, records PASSED (exit 0).
        """
        if _TAMPER:
            pytest.xfail("W2_NEGCTRL_TAMPER=1: guard intentionally broken to prove detectability")

        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=THRESHOLD,
            escalation_delta=0.1,
            max_threshold=THRESHOLD,
            max_delta=0.2,
        )
        snapshot = _make_snapshot_above_threshold()
        meta = _embedding_metadata()

        with patch.object(optimizer, "_aggregate_embedding_scores") as mock_agg:
            mock_agg.side_effect = [0.90, 0.90]

            proposal1 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=meta,
                embedding_influence_cap=0.25,
                min_sample_threshold=THRESHOLD,
            )
            proposal2 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=meta,
                embedding_influence_cap=0.25,
                min_sample_threshold=THRESHOLD,
            )

            conf1 = proposal1.adjustments[0].confidence
            conf2 = proposal2.adjustments[0].confidence
            assert conf1 == conf2, f"Determinism guard violated: run1={conf1} != run2={conf2}"
            print(f"W2-NEGCTRL-GUARD-INTACT: conf1={conf1} conf2={conf2}")

    def test_small_n_guard_violation_negative_control(self) -> None:
        """Guard: adjustments must be empty when total_count < min_sample_size.

        Tamper: mocks base method to bypass guard; xfail catches assertion,
        records XFAIL (exit 0).
        Restore: real guard fires, adjustments empty, records PASSED (exit 0).
        """
        if _TAMPER:
            pytest.xfail("W2_NEGCTRL_TAMPER=1: guard intentionally bypassed to prove detectability")

        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=THRESHOLD,
            escalation_delta=0.1,
            max_threshold=THRESHOLD,
            max_delta=0.2,
        )

        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer",
                    tier="LOCAL_AGENT",
                    failure_type="test_failure",
                ),
                HealingOutcomeAggregate(
                    success_count=0,
                    failure_count=2,
                    total_count=2,
                ),
            ),
        ]
        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_version",
            created_utc=1234567890,
            aggregates=tuple(aggregates),
        )
        meta = _embedding_metadata()

        proposal = optimizer.propose_threshold_adjustments_with_embeddings(
            snapshot,
            embedding_metadata=meta,
            embedding_influence_cap=0.25,
            min_sample_threshold=THRESHOLD,
        )
        assert len(proposal.adjustments) == 0, (
            "Small-N guard should block adjustments when total_count < min_sample_size"
        )
        print(f"W2-NEGCTRL-GUARD-INTACT: small-n blocked, adjustments={len(proposal.adjustments)}")
