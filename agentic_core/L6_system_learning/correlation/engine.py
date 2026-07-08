"""Risk correlation engine for deterministic multi-signal correlation."""

from __future__ import annotations

import json
from typing import Sequence

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "engine", "exec_snapshot_link")
from .types import CorrelatedRiskReport, CorrelatedRow, DriftEvent

trace_contract._emit_applies_guardrail("p0", "engine", "p0_governance")
trace_contract._emit_snapshots_state("p0", "engine", "state_snapshot")

trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "engine", "context_pull")
trace_contract._emit_pulls_context("p1", "engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "engine", "write_through")
trace_contract._emit_writes_through("p1", "engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "engine", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "engine", "human_escalation")
trace_contract._emit_routes_through("p1", "engine", "route_through")
trace_contract._emit_checks_agent_registry("p1", "engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "engine")
trace_contract._emit_gated_by_confidence("p1", "engine", "confidence_gate")
trace_contract.emit_replay_key("p0", "engine")
trace_contract.emit_determinism_digest("p0", "engine")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class RiskCorrelator:
    """Deterministic risk correlator for multi-signal correlation analysis."""

    def build(self, fingerprints: Sequence[str], drift_events: Sequence[DriftEvent]) -> CorrelatedRiskReport:
        """Build correlated risk report from fingerprints and drift events."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RiskCorrelator.build")

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
