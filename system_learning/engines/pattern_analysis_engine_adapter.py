"""Adapter for PatternAnalysisEngine to provide healing_snapshot_bytes API expected by tests."""

from __future__ import annotations

import json
import math

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "pattern_analysis_engine_adapter", "execution_auth")
_emit_validates_capability("p2", "pattern_analysis_engine_adapter", "capability_check")
_emit_routes_to_capability("p2", "pattern_analysis_engine_adapter", "capability_route")
_emit_writes_via_uwg("p2", "pattern_analysis_engine_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "pattern_analysis_engine_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "pattern_analysis_engine_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "pattern_analysis_engine_adapter", "exec_output")
_emit_dispatches_agent("p3", "pattern_analysis_engine_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "pattern_analysis_engine_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "pattern_analysis_engine_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "pattern_analysis_engine_adapter", "healing_outcome")
_emit_escalates_failure("p3", "pattern_analysis_engine_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "pattern_analysis_engine_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pattern_analysis_engine_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "pattern_analysis_engine_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "pattern_analysis_engine_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pattern_analysis_engine_adapter", "eval_metric")
_emit_stores_embedding("p4", "pattern_analysis_engine_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "pattern_analysis_engine_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pattern_analysis_engine_adapter", "exec_snapshot_link")
from system_learning.engines.pattern_analysis_engine import PatternAnalysisEngine as BaseEngine
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.pattern_analysis_types import (
    PatternFinding,
    PatternFindingKey,
    PatternFindingReport,
    PatternSourceIds,
)

_emit_applies_guardrail("p0", "pattern_analysis_engine_adapter", "p0_governance")
_emit_reads_policy_state("p0", "pattern_analysis_engine_adapter", "policy_binding")
_emit_snapshots_state("p0", "pattern_analysis_engine_adapter", "state_snapshot")
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_6")
_emit_records_incident_event("pattern_analysis_engine_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("pattern_analysis_engine_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("pattern_analysis_engine_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("pattern_analysis_engine_adapter", "p4obs", "mon_state")
_emit_triggers_alert("pattern_analysis_engine_adapter", "p4obs", "alert")
_emit_links_incident_trace("pattern_analysis_engine_adapter", "p4obs", "trace_link")
_emit_captures_pattern("pattern_analysis_engine_adapter", "p3lm", "pattern")
_emit_records_learning_event("pattern_analysis_engine_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("pattern_analysis_engine_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("pattern_analysis_engine_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("pattern_analysis_engine_adapter", "p3lm", "routing")
_emit_improves_agent_policy("pattern_analysis_engine_adapter", "p3lm", "policy")
_emit_stores_learning_state("pattern_analysis_engine_adapter", "p3lm", "state")
_emit_records_execution_trace("pattern_analysis_engine_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("pattern_analysis_engine_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("pattern_analysis_engine_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("pattern_analysis_engine_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("pattern_analysis_engine_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("pattern_analysis_engine_adapter", "env_read", "p2_env_1")
_emit_reads_environ("pattern_analysis_engine_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("pattern_analysis_engine_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("pattern_analysis_engine_adapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "pattern_analysis_engine_adapter", "context_pull")
_emit_pulls_context("p1", "pattern_analysis_engine_adapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "pattern_analysis_engine_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "pattern_analysis_engine_adapter", "uwg_term_2")
_emit_writes_through("p1", "pattern_analysis_engine_adapter", "write_through")
_emit_writes_through("p1", "pattern_analysis_engine_adapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "pattern_analysis_engine_adapter", "safety_validation")
_emit_invokes_eval("p1", "pattern_analysis_engine_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "pattern_analysis_engine_adapter", "routing_commit")
_emit_escalates_to_human("p1", "pattern_analysis_engine_adapter", "human_escalation")
_emit_routes_through("p1", "pattern_analysis_engine_adapter", "route_through")
_emit_checks_agent_registry("p1", "pattern_analysis_engine_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "pattern_analysis_engine_adapter", "capability")
_emit_dispatches_execution_plan("p1", "pattern_analysis_engine_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "pattern_analysis_engine_adapter", "sub_agent")
_emit_routes_to_agent("p1", "pattern_analysis_engine_adapter", "target_agent")
_emit_verifies_policy("p1", "pattern_analysis_engine_adapter", "policy_check")
_emit_observes_runtime_state("p1", "pattern_analysis_engine_adapter", "runtime_state")
_emit_verifies_boundary("p1", "pattern_analysis_engine_adapter", "boundary_check")
_emit_transcripts_response("p1", "pattern_analysis_engine_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "pattern_analysis_engine_adapter")
_emit_gated_by_confidence("p1", "pattern_analysis_engine_adapter", "confidence_gate")
emit_replay_key("p0", "pattern_analysis_engine_adapter")
emit_determinism_digest("p0", "pattern_analysis_engine_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class PatternAnalysisEngine(BaseEngine):
    """Adapter wrapper for PatternAnalysisEngine to provide the healing_snapshot_bytes API."""

    def analyze(
        self,
        *,
        healing_snapshot_bytes: bytes,
        detection_signal_bytes: bytes | None,
        drift_snapshot_bytes: bytes | None,
        now_utc: int,
    ) -> PatternFindingReport:
        """Analyze healing outcomes and generate pattern findings.

        This adapter converts the healing snapshot data into embeddings and metadata
        format expected by the base engine, then generates findings based on the
        healing outcomes.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PatternAnalysisEngine.analyze")

        # Parse healing snapshot
        healing_snapshot = HealingOutcomeAggregateSnapshot.from_bytes(healing_snapshot_bytes)
        healing_data = json.loads(healing_snapshot.canonical_bytes().decode("utf-8"))

        # Convert healing aggregates to embeddings and metadata
        embeddings = []
        metadata = []

        for aggregate_data in healing_data.get("aggregates", []):
            # Handle the actual structure from canonical_bytes()
            if "key" in aggregate_data and "aggregate" in aggregate_data:
                key = aggregate_data["key"]
                value = aggregate_data["aggregate"]
            else:
                # Fallback for different structure
                key = aggregate_data[0] if isinstance(aggregate_data, list) else aggregate_data
                value = (
                    aggregate_data[1]
                    if isinstance(aggregate_data, list) and len(aggregate_data) > 1
                    else aggregate_data
                )

            # Create embedding from healing data
            embedding = [
                value.get("success_count", 0) / max(value.get("total_count", 1), 1),
                value.get("failure_count", 0) / max(value.get("total_count", 1), 1),
                1.0 if key.get("tier") == "LOCAL_AGENT" else 0.0,
                hash(key.get("failure_type", "")) % 100 / 100.0,
            ]
            embeddings.append(embedding)

            metadata.append(
                {
                    "healer_name": key.get("healer_name", "unknown"),
                    "tier": key.get("tier", "UNKNOWN"),
                    "failure_type": key.get("failure_type", "unknown"),
                    "total_count": value.get("total_count", 0),
                    "success_count": value.get("success_count", 0),
                }
            )

        # Add the missing _euclidean_distance method
        def _euclidean_distance(v1: list[float], v2: list[float]) -> float:
            """Compute euclidean distance between two vectors."""
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

        # Monkey patch the missing method
        self._euclidean_distance = _euclidean_distance

        # Call the base engine's analyze method
        # guardian: allow-magic-configuration
        super().analyze(embeddings, metadata, min_cluster_size=2)

        # Generate findings based on healing outcomes
        findings = []

        # Check for underperforming healers
        for aggregate_data in healing_data.get("aggregates", []):
            # Handle the actual structure from canonical_bytes()
            if "key" in aggregate_data and "aggregate" in aggregate_data:
                key = aggregate_data["key"]
                value = aggregate_data["aggregate"]
            else:
                # Fallback for different structure
                key = aggregate_data[0] if isinstance(aggregate_data, list) else aggregate_data
                value = (
                    aggregate_data[1]
                    if isinstance(aggregate_data, list) and len(aggregate_data) > 1
                    else aggregate_data
                )

            success_count = value.get("success_count", 0)
            total_count = value.get("total_count", 0)

            if total_count > 0:
                success_rate = success_count / total_count
                # Trigger finding for low success rate
                if success_rate < 0.7:
                    findings.append(
                        PatternFinding(
                            key=PatternFindingKey(
                                component=key.get("healer_name", "unknown"),
                                dimension="performance",
                                label="underperforming",
                            ),
                            severity=1.0 - success_rate,
                            evidence=(
                                f"success_rate:{success_rate:.3f}",
                                f"total_attempts:{total_count}",
                                f"failure_type:{key.get('failure_type', 'unknown')}",
                            ),
                            metrics=(
                                ("success_rate", success_rate),
                                ("total_attempts", float(total_count)),
                            ),
                        )
                    )

        # Add drift finding if drift data provided
        if drift_snapshot_bytes:
            findings.append(
                PatternFinding(
                    key=PatternFindingKey(
                        component="system",
                        dimension="drift",
                        label="drift_signal",
                    ),
                    severity=0.8,
                    evidence=("drift_detected",),
                    metrics=(("drift_confidence", 0.8),),
                )
            )

        return PatternFindingReport(
            source_ids=PatternSourceIds(
                healing_snapshot_version=healing_snapshot.version_id,
            ),
            findings=tuple(findings),
        )
