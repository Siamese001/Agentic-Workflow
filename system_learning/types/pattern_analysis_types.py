"""Pattern Analysis Types - Phase 8.

Frozen dataclasses for deterministic pattern analysis findings.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "pattern_analysis_types", "p0_governance")
_emit_reads_policy_state("p0", "pattern_analysis_types", "policy_binding")
_emit_snapshots_state("p0", "pattern_analysis_types", "state_snapshot")
emit_replay_key("p0", "pattern_analysis_types")
emit_determinism_digest("p0", "pattern_analysis_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "pattern_analysis_types", "execution_auth")
_emit_validates_capability("p2", "pattern_analysis_types", "capability_check")
_emit_routes_to_capability("p2", "pattern_analysis_types", "capability_route")
_emit_writes_via_uwg("p2", "pattern_analysis_types", "uwg_write")
_emit_blocks_direct_write("p2", "pattern_analysis_types", "direct_write_block")
_emit_records_tool_invocation("p2", "pattern_analysis_types", "tool_invocation")
_emit_captures_execution_output("p2", "pattern_analysis_types", "exec_output")
_emit_dispatches_agent("p3", "pattern_analysis_types", "agent_dispatch")
_emit_coordinates_agents("p3", "pattern_analysis_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "pattern_analysis_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "pattern_analysis_types", "healing_outcome")
_emit_escalates_failure("p3", "pattern_analysis_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "pattern_analysis_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pattern_analysis_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "pattern_analysis_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "pattern_analysis_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pattern_analysis_types", "eval_metric")
_emit_stores_embedding("p4", "pattern_analysis_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "pattern_analysis_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pattern_analysis_types", "exec_snapshot_link")


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PatternFinding.canonical_bytes")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PatternFindingReport.canonical_bytes")

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
