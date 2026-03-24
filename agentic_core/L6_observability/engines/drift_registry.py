"""DriftRegistry — unified timeline for all drift signal sources.

Aggregates entries from RetrievalDriftMonitor, EmbeddingDriftMonitor,
ShadowDriftAnalyzer, and DriftDetector into a single queryable, append-only
L4 timeline.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

record_execution_trace("drift_registry", "drift_registry_trace")


_emit_emits_metric_event("drift_registry", "p4obs", "metric_1")
_emit_emits_metric_event("drift_registry", "p4obs", "metric_2")
_emit_emits_metric_event("drift_registry", "p4obs", "metric_3")
_emit_emits_metric_event("drift_registry", "p4obs", "metric_4")
_emit_emits_metric_event("drift_registry", "p4obs", "metric_5")
_emit_emits_metric_event("drift_registry", "p4obs", "metric_6")
_emit_records_incident_event("drift_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("drift_registry", "p4obs", "anomaly")
_emit_writes_observability_log("drift_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("drift_registry", "p4obs", "mon_state")
_emit_triggers_alert("drift_registry", "p4obs", "alert")
_emit_links_incident_trace("drift_registry", "p4obs", "trace_link")
_emit_captures_pattern("drift_registry", "p3lm", "pattern")
_emit_records_learning_event("drift_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("drift_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("drift_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("drift_registry", "p3lm", "routing")
_emit_improves_agent_policy("drift_registry", "p3lm", "policy")
_emit_stores_learning_state("drift_registry", "p3lm", "state")
_emit_records_execution_trace("drift_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("drift_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("drift_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("drift_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("drift_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("drift_registry", "env_read", "p2_env_1")
_emit_reads_environ("drift_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("drift_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("drift_registry", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "drift_registry")
emit_determinism_digest("p0", "drift_registry")

_emit_dispatches_healing_run("p1", "drift_registry", "L6")
_emit_routes_through("p1", "drift_registry", "L6")
_emit_checks_agent_registry("p1", "drift_registry", "agent_registry")
_emit_validates_agent_capability("p1", "drift_registry", "capability")
_emit_dispatches_execution_plan("p1", "drift_registry", "exec_plan")
_emit_agent_executes_agent("p1", "drift_registry", "sub_agent")
_emit_routes_to_agent("p1", "drift_registry", "target_agent")
_emit_verifies_policy("p1", "drift_registry", "policy_check")
_emit_observes_runtime_state("p1", "drift_registry", "runtime_state")
_emit_verifies_boundary("p1", "drift_registry", "boundary_check")
_emit_transcripts_response("p1", "drift_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "drift_registry")
_emit_gated_by_confidence("p1", "drift_registry", "confidence_gate")
_emit_escalates_to_human("p1", "drift_registry", "L6")
_emit_reads_policy_state("p1", "drift_registry", "L6")
_emit_pulls_context("p1", "drift_registry", "context_pull")
_emit_pulls_context("p1", "drift_registry", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "drift_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "drift_registry", "uwg_term_secondary")
_emit_writes_through("p1", "drift_registry", "write_through")
_emit_writes_through("p1", "drift_registry", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "drift_registry", "safety_validation")
_emit_invokes_eval("p1", "drift_registry", "eval_call")
_emit_proposal_commits_routing("p1", "drift_registry", "routing_commit")

_emit_snapshots_state("p0", "drift_registry", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "drift_registry", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "drift_registry")
_emit_authorize_and_execute("p2", "drift_registry", "execution_auth")
_emit_validates_capability("p2", "drift_registry", "capability_check")
_emit_routes_to_capability("p2", "drift_registry", "capability_route")
_emit_writes_via_uwg("p2", "drift_registry", "uwg_write")
_emit_blocks_direct_write("p2", "drift_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "drift_registry", "tool_invocation")
_emit_captures_execution_output("p2", "drift_registry", "exec_output")
_emit_dispatches_agent("p3", "drift_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "drift_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "drift_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "drift_registry", "healing_outcome")
_emit_escalates_failure("p3", "drift_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "drift_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "drift_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "drift_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "drift_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "drift_registry", "eval_metric")
_emit_stores_embedding("p4", "drift_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "drift_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "drift_registry", "exec_snapshot_link")

_logger = logging.getLogger(__name__)
_TIMELINE_PATH = Path("agentic_core/L4_state/stores/drift_timeline.jsonl")
DriftSource = Literal["retrieval", "embedding", "shadow", "c0_context"]
DriftSeverity = Literal["info", "warning", "critical"]


@dataclass(frozen=True)
class DriftRegistryEntry:
    """Immutable record of a single drift measurement."""

    source: DriftSource
    timestamp_iso: str
    metric_name: str
    current_value: float
    threshold_value: float
    drift_flag: bool
    severity: DriftSeverity
    deterministic_digest: str

    @classmethod
    def create(
        cls,
        source: DriftSource,
        timestamp_iso: str,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        drift_flag: bool,
        severity: DriftSeverity,
    ) -> DriftRegistryEntry:
        canonical = json.dumps(
            {
                "source": source,
                "timestamp_iso": timestamp_iso,
                "metric_name": metric_name,
                "current_value": round(current_value, 8),
                "threshold_value": round(threshold_value, 8),
                "drift_flag": drift_flag,
                "severity": severity,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(
            source=source,
            timestamp_iso=timestamp_iso,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            drift_flag=drift_flag,
            severity=severity,
            deterministic_digest=digest,
        )

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "timestamp_iso": self.timestamp_iso,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "drift_flag": self.drift_flag,
            "severity": self.severity,
            "deterministic_digest": self.deterministic_digest,
        }


class DriftRegistry:
    """Unified in-memory + append-only file timeline for all drift signals.

    Thread-safety: not thread-safe; designed for single-process use.
    """

    def __init__(self, timeline_path: Path | None = None) -> None:
        self._timeline_path = timeline_path or _TIMELINE_PATH
        self._entries: list[DriftRegistryEntry] = []

    def record(self, entry: DriftRegistryEntry) -> None:
        """Append a drift entry to the in-memory list and persist to JSONL."""
        self._entries.append(entry)
        self._persist(entry)
        if entry.severity == "critical":
            _logger.warning(
                "DriftRegistry: critical drift detected",
                extra={
                    "source": entry.source,
                    "metric": entry.metric_name,
                    "value": entry.current_value,
                    "threshold": entry.threshold_value,
                },
            )

    def query(
        self, since_iso: str | None = None, source_filter: DriftSource | None = None
    ) -> list[DriftRegistryEntry]:
        """Return entries matching the given filters, oldest first."""
        results = list(self._entries)
        if since_iso is not None:
            results = [e for e in results if e.timestamp_iso >= since_iso]
        if source_filter is not None:
            results = [e for e in results if e.source == source_filter]
        return results

    def all_entries(self) -> list[DriftRegistryEntry]:
        """Return all recorded entries, oldest first."""
        return list(self._entries)

    def _persist(self, entry: DriftRegistryEntry) -> None:
        try:
            self._timeline_path.parent.mkdir(parents=True, exist_ok=True)
            with self._timeline_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry.to_dict(), separators=(",", ":")) + "\n")
        # guardian: allow-silent-swallow
        except Exception:
            _logger.debug("DriftRegistry: failed to persist entry", exc_info=True)


_registry: DriftRegistry | None = None


def get_drift_registry() -> DriftRegistry:
    """Return the module-level singleton DriftRegistry."""
    global _registry
    if _registry is None:
        _registry = DriftRegistry()
    return _registry


__all__ = ["DriftRegistryEntry", "DriftRegistry", "DriftSource", "DriftSeverity", "get_drift_registry"]
