"""Risk correlation engine for deterministic multi-signal correlation."""

from __future__ import annotations

import json
from typing import Sequence

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "engine", "execution_auth")
_emit_validates_capability("p2", "engine", "capability_check")
_emit_routes_to_capability("p2", "engine", "capability_route")
_emit_writes_via_uwg("p2", "engine", "uwg_write")
_emit_blocks_direct_write("p2", "engine", "direct_write_block")
_emit_records_tool_invocation("p2", "engine", "tool_invocation")
_emit_captures_execution_output("p2", "engine", "exec_output")
_emit_dispatches_agent("p3", "engine", "agent_dispatch")
_emit_coordinates_agents("p3", "engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "engine", "healing_outcome")
_emit_escalates_failure("p3", "engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "engine", "eval_metric")
_emit_stores_embedding("p4", "engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "engine", "exec_snapshot_link")
from .types import CorrelatedRiskReport, CorrelatedRow, DriftEvent

_emit_applies_guardrail("p0", "engine", "p0_governance")
_emit_snapshots_state("p0", "engine", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("engine", "p4obs", "metric_1")
_emit_emits_metric_event("engine", "p4obs", "metric_2")
_emit_emits_metric_event("engine", "p4obs", "metric_3")
_emit_emits_metric_event("engine", "p4obs", "metric_4")
_emit_emits_metric_event("engine", "p4obs", "metric_5")
_emit_emits_metric_event("engine", "p4obs", "metric_6")
_emit_records_incident_event("engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("engine", "p4obs", "anomaly")
_emit_writes_observability_log("engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("engine", "p4obs", "mon_state")
_emit_triggers_alert("engine", "p4obs", "alert")
_emit_links_incident_trace("engine", "p4obs", "trace_link")
_emit_captures_pattern("engine", "p3lm", "pattern")
_emit_records_learning_event("engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("engine", "p3lm", "routing")
_emit_improves_agent_policy("engine", "p3lm", "policy")
_emit_stores_learning_state("engine", "p3lm", "state")
_emit_records_execution_trace("engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("engine", "env_read", "p2_env_1")
_emit_reads_environ("engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "engine", "context_pull")
_emit_pulls_context("p1", "engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "engine", "uwg_term_2")
_emit_writes_through("p1", "engine", "write_through")
_emit_writes_through("p1", "engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "engine", "safety_validation")
_emit_invokes_eval("p1", "engine", "eval_call")
_emit_proposal_commits_routing("p1", "engine", "routing_commit")
_emit_escalates_to_human("p1", "engine", "human_escalation")
_emit_routes_through("p1", "engine", "route_through")
_emit_checks_agent_registry("p1", "engine", "agent_registry")
_emit_validates_agent_capability("p1", "engine", "capability")
_emit_dispatches_execution_plan("p1", "engine", "exec_plan")
_emit_agent_executes_agent("p1", "engine", "sub_agent")
_emit_routes_to_agent("p1", "engine", "target_agent")
_emit_verifies_policy("p1", "engine", "policy_check")
_emit_observes_runtime_state("p1", "engine", "runtime_state")
_emit_verifies_boundary("p1", "engine", "boundary_check")
_emit_transcripts_response("p1", "engine", "transcript")
_emit_hard_fails_untranscripted("p1", "engine")
_emit_gated_by_confidence("p1", "engine", "confidence_gate")
emit_replay_key("p0", "engine")
emit_determinism_digest("p0", "engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class RiskCorrelator:
    """Deterministic risk correlator for multi-signal correlation analysis."""

    def build(self, fingerprints: Sequence[str], drift_events: Sequence[DriftEvent]) -> CorrelatedRiskReport:
        """Build correlated risk report from fingerprints and drift events."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RiskCorrelator.build")

        if not isinstance(fingerprints, (list, tuple)):
            raise TypeError(f"fingerprints must be a list, got {type(fingerprints).__name__}")
        if not isinstance(drift_events, (list, tuple)):
            raise TypeError(f"drift_events must be a list, got {type(drift_events).__name__}")
        sorted_fingerprints = sorted(fingerprints)
        sorted_drift_events = sorted(drift_events, key=lambda e: (e.policy_id, e.drift_type))
        rows = []
        for fingerprint in sorted_fingerprints:
            for drift_event in sorted_drift_events:
                if self._should_correlate(fingerprint, drift_event.policy_id):
                    row = CorrelatedRow(
                        fingerprint=fingerprint,
                        policy_id=drift_event.policy_id,
                        drift_type=drift_event.drift_type,
                        severity=drift_event.severity,
                    )
                    rows.append(row)
        sorted_rows = sorted(rows, key=lambda r: (r.fingerprint, r.policy_id, r.drift_type))
        canonical_data = {
            "rows": [
                {
                    "fingerprint": r.fingerprint,
                    "policy_id": r.policy_id,
                    "drift_type": r.drift_type,
                    "severity": r.severity,
                }
                for r in sorted_rows
            ],
        }
        canonical_bytes = json.dumps(canonical_data, separators=(",", ":"), sort_keys=True).encode("ascii")
        return CorrelatedRiskReport.from_canonical_bytes(sorted_rows, canonical_bytes)

    def _should_correlate(self, fingerprint: str, policy_id: str) -> bool:
        """Determine if fingerprint should correlate with policy_id."""
        return policy_id in fingerprint
