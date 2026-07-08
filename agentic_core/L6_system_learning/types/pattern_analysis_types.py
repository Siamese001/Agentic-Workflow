"""Pattern Analysis Types - Phase 8.

Frozen dataclasses for deterministic pattern analysis findings.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "pattern_analysis_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "pattern_analysis_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "pattern_analysis_types", "state_snapshot")

trace_contract._emit_emits_metric_event("pattern_analysis_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("pattern_analysis_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("pattern_analysis_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("pattern_analysis_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("pattern_analysis_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("pattern_analysis_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("pattern_analysis_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("pattern_analysis_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("pattern_analysis_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("pattern_analysis_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("pattern_analysis_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("pattern_analysis_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("pattern_analysis_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("pattern_analysis_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("pattern_analysis_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("pattern_analysis_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("pattern_analysis_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("pattern_analysis_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("pattern_analysis_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("pattern_analysis_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("pattern_analysis_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("pattern_analysis_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("pattern_analysis_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("pattern_analysis_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("pattern_analysis_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("pattern_analysis_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("pattern_analysis_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("pattern_analysis_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "pattern_analysis_types", "context_pull")
trace_contract._emit_pulls_context("p1", "pattern_analysis_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "pattern_analysis_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "pattern_analysis_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "pattern_analysis_types", "write_through")
trace_contract._emit_writes_through("p1", "pattern_analysis_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "pattern_analysis_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "pattern_analysis_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "pattern_analysis_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "pattern_analysis_types", "human_escalation")
trace_contract._emit_routes_through("p1", "pattern_analysis_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "pattern_analysis_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "pattern_analysis_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "pattern_analysis_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "pattern_analysis_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "pattern_analysis_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "pattern_analysis_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "pattern_analysis_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "pattern_analysis_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "pattern_analysis_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "pattern_analysis_types")
trace_contract._emit_gated_by_confidence("p1", "pattern_analysis_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "pattern_analysis_types")
trace_contract.emit_determinism_digest("p0", "pattern_analysis_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "pattern_analysis_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "pattern_analysis_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "pattern_analysis_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "pattern_analysis_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "pattern_analysis_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "pattern_analysis_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "pattern_analysis_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "pattern_analysis_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "pattern_analysis_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "pattern_analysis_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "pattern_analysis_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "pattern_analysis_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "pattern_analysis_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "pattern_analysis_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "pattern_analysis_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "pattern_analysis_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "pattern_analysis_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "pattern_analysis_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "pattern_analysis_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "pattern_analysis_types", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class PatternSourceIds:
    """Identifiers for source data used in pattern analysis."""

    healing_snapshot_version: str
    detection_signal_version: str | None = None
    drift_snapshot_version: str | None = None


@dataclass(frozen=True, slots=True)
class PatternFindingKey:
    """Key for a pattern finding."""

    component: str
    dimension: str
    label: str


@dataclass(frozen=True, slots=True)
class PatternFinding:
    """A single pattern finding with deterministic evidence."""

    key: PatternFindingKey
    severity: float
    evidence: tuple[str, ...]
    metrics: tuple[tuple[str, float], ...]

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "PatternFinding.canonical_bytes"
        )

        data = {
            "component": self.key.component,
            "dimension": self.key.dimension,
            "label": self.key.label,
            "severity": round(self.severity, 6),
            "evidence": tuple(sorted(self.evidence)),
            "metrics": tuple(((name, round(value, 6)) for name, value in sorted(self.metrics))),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA256 hash of canonical content."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class PatternFindingReport:
    """Complete pattern analysis report."""

    source_ids: PatternSourceIds
    findings: tuple[PatternFinding, ...]

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "PatternFindingReport.canonical_bytes"
        )

        data = {
            "healing_snapshot_version": self.source_ids.healing_snapshot_version,
            "detection_signal_version": self.source_ids.detection_signal_version,
            "drift_snapshot_version": self.source_ids.drift_snapshot_version,
            "findings": [
                {
                    "component": f.key.component,
                    "dimension": f.key.dimension,
                    "label": f.key.label,
                    "severity": round(f.severity, 6),
                    "evidence": tuple(sorted(f.evidence)),
                    "metrics": tuple(((name, round(value, 6)) for name, value in sorted(f.metrics))),
                }
                for f in self.findings
            ],
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA256 hash of canonical content."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
