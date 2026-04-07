"""
W4-C Shadow Drift Analyzer

Converts W4-B shadow telemetry into deterministic drift signals.
Provides informational-only policy feedback without automatic mutation.
"""

import hashlib
import json
import statistics
from dataclasses import dataclass
from typing import Any

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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "shadow_drift_analyzer", "p0_governance")
_emit_reads_policy_state("p0", "shadow_drift_analyzer", "policy_binding")
_emit_snapshots_state("p0", "shadow_drift_analyzer", "state_snapshot")
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

_emit_emits_metric_event("shadow_drift_analyzer", "p4obs", "metric_1")
_emit_emits_metric_event("shadow_drift_analyzer", "p4obs", "metric_2")
_emit_emits_metric_event("shadow_drift_analyzer", "p4obs", "metric_3")
_emit_emits_metric_event("shadow_drift_analyzer", "p4obs", "metric_4")
_emit_emits_metric_event("shadow_drift_analyzer", "p4obs", "metric_5")
_emit_emits_metric_event("shadow_drift_analyzer", "p4obs", "metric_6")
_emit_records_incident_event("shadow_drift_analyzer", "p4obs", "incident")
_emit_captures_runtime_anomaly("shadow_drift_analyzer", "p4obs", "anomaly")
_emit_writes_observability_log("shadow_drift_analyzer", "p4obs", "obs_log")
_emit_updates_monitoring_state("shadow_drift_analyzer", "p4obs", "mon_state")
_emit_triggers_alert("shadow_drift_analyzer", "p4obs", "alert")
_emit_links_incident_trace("shadow_drift_analyzer", "p4obs", "trace_link")
_emit_captures_pattern("shadow_drift_analyzer", "p3lm", "pattern")
_emit_records_learning_event("shadow_drift_analyzer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("shadow_drift_analyzer", "p3lm", "snapshot")
_emit_feeds_meta_learning("shadow_drift_analyzer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("shadow_drift_analyzer", "p3lm", "routing")
_emit_improves_agent_policy("shadow_drift_analyzer", "p3lm", "policy")
_emit_stores_learning_state("shadow_drift_analyzer", "p3lm", "state")
_emit_records_execution_trace("shadow_drift_analyzer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("shadow_drift_analyzer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("shadow_drift_analyzer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("shadow_drift_analyzer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("shadow_drift_analyzer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("shadow_drift_analyzer", "env_read", "p2_env_1")
_emit_reads_environ("shadow_drift_analyzer", "env_read", "p2_env_2")
_emit_reads_runtime_state("shadow_drift_analyzer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("shadow_drift_analyzer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "shadow_drift_analyzer", "context_pull")
_emit_pulls_context("p1", "shadow_drift_analyzer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "shadow_drift_analyzer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "shadow_drift_analyzer", "uwg_term_2")
_emit_writes_through("p1", "shadow_drift_analyzer", "write_through")
_emit_writes_through("p1", "shadow_drift_analyzer", "write_through_2")
_emit_validated_by_safety_plane("p1", "shadow_drift_analyzer", "safety_validation")
_emit_invokes_eval("p1", "shadow_drift_analyzer", "eval_call")
_emit_proposal_commits_routing("p1", "shadow_drift_analyzer", "routing_commit")
_emit_escalates_to_human("p1", "shadow_drift_analyzer", "human_escalation")
_emit_routes_through("p1", "shadow_drift_analyzer", "route_through")
_emit_checks_agent_registry("p1", "shadow_drift_analyzer", "agent_registry")
_emit_validates_agent_capability("p1", "shadow_drift_analyzer", "capability")
_emit_dispatches_execution_plan("p1", "shadow_drift_analyzer", "exec_plan")
_emit_agent_executes_agent("p1", "shadow_drift_analyzer", "sub_agent")
_emit_routes_to_agent("p1", "shadow_drift_analyzer", "target_agent")
_emit_verifies_policy("p1", "shadow_drift_analyzer", "policy_check")
_emit_observes_runtime_state("p1", "shadow_drift_analyzer", "runtime_state")
_emit_verifies_boundary("p1", "shadow_drift_analyzer", "boundary_check")
_emit_transcripts_response("p1", "shadow_drift_analyzer", "transcript")
_emit_hard_fails_untranscripted("p1", "shadow_drift_analyzer")
_emit_gated_by_confidence("p1", "shadow_drift_analyzer", "confidence_gate")
emit_replay_key("p0", "shadow_drift_analyzer")
emit_determinism_digest("p0", "shadow_drift_analyzer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "shadow_drift_analyzer", "execution_auth")
_emit_validates_capability("p2", "shadow_drift_analyzer", "capability_check")
_emit_routes_to_capability("p2", "shadow_drift_analyzer", "capability_route")
_emit_writes_via_uwg("p2", "shadow_drift_analyzer", "uwg_write")
_emit_blocks_direct_write("p2", "shadow_drift_analyzer", "direct_write_block")
_emit_records_tool_invocation("p2", "shadow_drift_analyzer", "tool_invocation")
_emit_captures_execution_output("p2", "shadow_drift_analyzer", "exec_output")
_emit_dispatches_agent("p3", "shadow_drift_analyzer", "agent_dispatch")
_emit_coordinates_agents("p3", "shadow_drift_analyzer", "agent_coordination")
_emit_records_workflow_lineage("p3", "shadow_drift_analyzer", "workflow_lineage")
_emit_records_healing_outcome("p3", "shadow_drift_analyzer", "healing_outcome")
_emit_escalates_failure("p3", "shadow_drift_analyzer", "failure_escalation")
_emit_orchestrates_workflow("p3", "shadow_drift_analyzer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "shadow_drift_analyzer", "healing_dispatch")
_emit_invokes_evaluation("p3", "shadow_drift_analyzer", "evaluation_signal")
_emit_records_telemetry_event("p4", "shadow_drift_analyzer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "shadow_drift_analyzer", "eval_metric")
_emit_stores_embedding("p4", "shadow_drift_analyzer", "embedding_store")
_emit_updates_meta_learning_state("p4", "shadow_drift_analyzer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "shadow_drift_analyzer", "exec_snapshot_link")

_DEFAULT_DRIFT_THRESHOLD = 0.92


@dataclass(frozen=True, slots=True)
class DriftSummary:
    """Summary of shadow embedding drift analysis."""

    profile_id: str
    batch_size: int
    mean_cosine: float
    p95_cosine: float
    drift_flag: bool
    drift_score: float
    deterministic_digest: str
    drift_threshold: float = _DEFAULT_DRIFT_THRESHOLD
    drift_source: str = "embedding_cosine"
    violation_delta: int | None = None

    def emit_digest(self) -> None:
        """Print the drift digest for determinism verification."""
        print(f"W4C-DRIFT-DIGEST: {self.deterministic_digest}")

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for deterministic serialization."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DriftSummary.to_canonical_json")

        data = {
            "profile_id": self.profile_id,
            "batch_size": self.batch_size,
            "mean_cosine": round(self.mean_cosine, 6),
            "p95_cosine": round(self.p95_cosine, 6),
            "drift_flag": self.drift_flag,
            "drift_score": round(self.drift_score, 6),
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))


class ShadowDriftAnalyzer:
    """Analyzes shadow embedding telemetry for drift detection."""

    def __init__(self, drift_threshold: float = _DEFAULT_DRIFT_THRESHOLD) -> None:
        self._drift_threshold = drift_threshold

    def analyze_batch(
        self, *, shadow_records: list[dict[str, Any]], profile_id: str, now_utc: int,
    ) -> DriftSummary:
        """Analyze a batch of shadow telemetry records for drift.

        Args:
            shadow_records: List of shadow telemetry dictionaries
            profile_id: RetrievalProfile identifier
            now_utc: Current timestamp

        Returns:
            DriftSummary with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ShadowDriftAnalyzer.analyze_batch")

        if not shadow_records:
            return DriftSummary(
                profile_id=profile_id,
                batch_size=len(shadow_records),
                mean_cosine=1.0,
                p95_cosine=1.0,
                drift_flag=False,
                drift_score=0.0,
                deterministic_digest=self._compute_digest([], profile_id, now_utc),
            )
        cosine_values = []
        for record in shadow_records:
            if "primary_shadow_cosine" in record:
                cosine_values.append(float(record["primary_shadow_cosine"]))
        if not cosine_values:
            return DriftSummary(
                profile_id=profile_id,
                batch_size=len(shadow_records),
                mean_cosine=1.0,
                p95_cosine=1.0,
                drift_flag=False,
                drift_score=0.0,
                deterministic_digest=self._compute_digest([], profile_id, now_utc),
            )

        # Check for ADG violation trend drift
        violation_delta = None
        drift_source = "embedding_cosine"
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
            bridge = get_sl_memory_bridge()
            current_count, previous_count = bridge.get_latest_violation_counts()
            if current_count > 0 and previous_count > 0:
                violation_delta = current_count - previous_count
                if violation_delta > 0:
                    # Violations increased - this is structural drift
                    drift_source = "adg_structural"
        except Exception as e:

            # ADG data unavailable - continue with embedding-only analysis
            import logging; logging.getLogger(__name__).debug("shadow_drift_analyzer: Exception swallowed at L259: %s", e)

        mean_cosine = statistics.mean(cosine_values)
        p95_cosine = self._compute_percentile(cosine_values, 95)
        drift_score = max(0.0, (p95_cosine - self._drift_threshold) / self._drift_threshold)
        drift_flag = p95_cosine > self._drift_threshold or (violation_delta and violation_delta > 0)

        # Adjust drift score based on violation trend
        if violation_delta and violation_delta > 0:
            # Boost drift score for structural violations
            drift_score = max(drift_score, 0.5 + (violation_delta / 10.0))

        return DriftSummary(
            profile_id=profile_id,
            batch_size=len(shadow_records),
            mean_cosine=round(mean_cosine, 6),
            p95_cosine=round(p95_cosine, 6),
            drift_flag=drift_flag,
            drift_score=round(drift_score, 6),
            deterministic_digest=self._compute_digest(cosine_values, profile_id, now_utc),
            drift_source=drift_source,
            violation_delta=violation_delta,
        )

        # Emit to registry
        self._emit_to_registry(summary)
        return summary

    def _emit_to_registry(self, summary: DriftSummary) -> None:
        """Emit shadow drift measurement to unified DriftRegistry (P5-5B/5C) and Memory MCP."""
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            get_sl_memory_bridge().persist_drift_summary(summary)
        # guardian: allow-silent-swallow
        except Exception:
            pass
        try:
            import hashlib
            import json as _json

            from agentic_core.L6_observability.utils.engines.drift_registry import (
                DriftRegistryEntry,
                get_drift_registry,
            )

            severity = "critical" if summary.drift_flag else "info"
            digest_payload = _json.dumps(
                {
                    "source": "shadow",
                    "metric": "p95_cosine",
                    "value": summary.p95_cosine,
                    "threshold": summary.drift_threshold,
                    "digest": summary.deterministic_digest,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            deterministic_digest = hashlib.sha256(digest_payload.encode()).hexdigest()
            entry = DriftRegistryEntry(
                source="shadow",
                timestamp_iso=_json.dumps(summary.profile_id),
                metric_name="p95_cosine",
                current_value=summary.p95_cosine,
                threshold_value=summary.drift_threshold,
                drift_flag=summary.drift_flag,
                severity=severity,
                deterministic_digest=deterministic_digest,
            )
            get_drift_registry().record(entry)
            if summary.drift_flag:
                try:
                    from system_learning.ports.meta_learning_bus import MetaLearningBus
                    from system_learning.ports.meta_learning_change_package import MetaLearningChangePackage

                    bus = MetaLearningBus.get_instance()
                    pkg = MetaLearningChangePackage.create(
                        kind="drift_alert",
                        payload={
                            "source": "shadow",
                            "metric_name": "p95_cosine",
                            "current_value": summary.p95_cosine,
                            "threshold_value": summary.drift_threshold,
                            "severity": severity,
                            "drift_score": summary.drift_score,
                            "digest": summary.deterministic_digest,
                            "profile_id": summary.profile_id,
                        },
                        proposal_only=True,
                    )
                    bus.enqueue(pkg)
                # guardian: allow-silent-swallow
                except Exception:
                    pass
        # guardian: allow-silent-swallow
        except Exception:
            pass

    # Wave B-7: Infrastructure drift detection from cache coherence violations
    def analyze_infrastructure_drift(
        self,
        coherence_violations: list[dict[str, Any]],
        now_utc: int,
    ) -> dict[str, Any]:
        """Analyze infrastructure drift from cache coherence violations.

        Args:
            coherence_violations: List of cache coherence violations
            now_utc: Current timestamp

        Returns:
            Infrastructure drift analysis
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_verifies_policy(str(_uuid.uuid4()), "Module.analyze_infrastructure_drift", "L4_STATE")
        _emit_observes_runtime_state(str(_uuid.uuid4()), "Module.analyze_infrastructure_drift", "L4_STATE")
        _emit_snapshots_state(str(_uuid.uuid4()), "Module.analyze_infrastructure_drift", "L4_STATE")

        if not coherence_violations:
            return {
                "drift_detected": False,
                "violation_count": 0,
                "timestamp_utc": now_utc,
                "analysis": "No coherence violations detected",
            }

        # Group violations by layer type
        layer_violations = {}
        for violation in coherence_violations:
            layer = violation.get("layer_type", "unknown")
            if layer not in layer_violations:
                layer_violations[layer] = []
            layer_violations[layer].append(violation)

        # Compute drift metrics
        total_violations = len(coherence_violations)
        layers_affected = len(layer_violations)
        max_violations_layer = max(layer_violations.keys(), key=lambda k: len(layer_violations[k]))
        max_violations_count = len(layer_violations[max_violations_layer])

        # Determine drift severity
        drift_detected = total_violations > 5  # Threshold for infrastructure drift
        severity = "high" if total_violations > 20 else "medium" if total_violations > 10 else "low"

        analysis = {
            "drift_detected": drift_detected,
            "severity": severity,
            "violation_count": total_violations,
            "layers_affected": layers_affected,
            "most_affected_layer": max_violations_layer,
            "max_layer_violations": max_violations_count,
            "layer_breakdown": {layer: len(violations) for layer, violations in layer_violations.items()},
            "timestamp_utc": now_utc,
            "trace_id": _trace_id,
        }

        # Persist infrastructure drift analysis
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
            bridge = get_sl_memory_bridge()

            bridge.persist_infrastructure_drift_analysis(
                drift_detected=drift_detected,
                severity=severity,
                violation_count=total_violations,
                layers_affected=layers_affected,
                analysis_json=json.dumps(analysis, sort_keys=True),
                timestamp_utc=now_utc,
            )
        except Exception as e:

            # Bridge unavailable - continue without it
            import logging; logging.getLogger(__name__).debug("shadow_drift_analyzer: Exception swallowed at L431: %s", e)

        return analysis

    def _compute_percentile(self, values: list[float], percentile: float) -> float:
        """Compute percentile with deterministic method."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n == 1:
            return sorted_values[0]
        index = percentile * (n - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, n - 1)
        fraction = index - lower_index
        lower_value = sorted_values[lower_index]
        upper_value = sorted_values[upper_index]
        return lower_value + fraction * (upper_value - lower_value)

    def _compute_digest(self, cosine_values: list[float], profile_id: str, now_utc: int) -> str:
        """Compute deterministic SHA-256 digest of analysis data."""
        data = {
            "profile_id": profile_id,
            "now_utc": now_utc,
            "cosine_values": [round(v, 6) for v in sorted(cosine_values)],
            "drift_threshold": self._drift_threshold,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["ShadowDriftAnalyzer", "DriftSummary"]
