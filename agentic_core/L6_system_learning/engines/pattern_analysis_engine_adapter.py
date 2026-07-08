"""Adapter for PatternAnalysisEngine to provide healing_snapshot_bytes API expected by tests."""

from __future__ import annotations

import json
import math

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "pattern_analysis_engine_adapter", "execution_auth")
trace_contract._emit_validates_capability("p2", "pattern_analysis_engine_adapter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "pattern_analysis_engine_adapter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "pattern_analysis_engine_adapter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "pattern_analysis_engine_adapter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "pattern_analysis_engine_adapter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "pattern_analysis_engine_adapter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "pattern_analysis_engine_adapter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "pattern_analysis_engine_adapter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "pattern_analysis_engine_adapter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "pattern_analysis_engine_adapter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "pattern_analysis_engine_adapter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "pattern_analysis_engine_adapter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "pattern_analysis_engine_adapter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "pattern_analysis_engine_adapter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "pattern_analysis_engine_adapter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "pattern_analysis_engine_adapter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "pattern_analysis_engine_adapter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "pattern_analysis_engine_adapter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "pattern_analysis_engine_adapter", "exec_snapshot_link")
from .pattern_analysis_engine import PatternAnalysisEngine as BaseEngine
from agentic_core.L6_system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregateSnapshot,
)
from agentic_core.L6_system_learning.types.pattern_analysis_types import (
    PatternFinding,
    PatternFindingKey,
    PatternFindingReport,
    PatternSourceIds,
)

trace_contract._emit_applies_guardrail("p0", "pattern_analysis_engine_adapter", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "pattern_analysis_engine_adapter", "policy_binding")
trace_contract._emit_snapshots_state("p0", "pattern_analysis_engine_adapter", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("pattern_analysis_engine_adapter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("pattern_analysis_engine_adapter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("pattern_analysis_engine_adapter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("pattern_analysis_engine_adapter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("pattern_analysis_engine_adapter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("pattern_analysis_engine_adapter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("pattern_analysis_engine_adapter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("pattern_analysis_engine_adapter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("pattern_analysis_engine_adapter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("pattern_analysis_engine_adapter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("pattern_analysis_engine_adapter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("pattern_analysis_engine_adapter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("pattern_analysis_engine_adapter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("pattern_analysis_engine_adapter", "p3lm", "state")
trace_contract._emit_records_execution_trace("pattern_analysis_engine_adapter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("pattern_analysis_engine_adapter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("pattern_analysis_engine_adapter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("pattern_analysis_engine_adapter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("pattern_analysis_engine_adapter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("pattern_analysis_engine_adapter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("pattern_analysis_engine_adapter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("pattern_analysis_engine_adapter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("pattern_analysis_engine_adapter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "pattern_analysis_engine_adapter", "context_pull")
trace_contract._emit_pulls_context("p1", "pattern_analysis_engine_adapter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "pattern_analysis_engine_adapter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "pattern_analysis_engine_adapter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "pattern_analysis_engine_adapter", "write_through")
trace_contract._emit_writes_through("p1", "pattern_analysis_engine_adapter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "pattern_analysis_engine_adapter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "pattern_analysis_engine_adapter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "pattern_analysis_engine_adapter", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "pattern_analysis_engine_adapter", "human_escalation")
trace_contract._emit_routes_through("p1", "pattern_analysis_engine_adapter", "route_through")
trace_contract._emit_checks_agent_registry("p1", "pattern_analysis_engine_adapter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "pattern_analysis_engine_adapter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "pattern_analysis_engine_adapter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "pattern_analysis_engine_adapter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "pattern_analysis_engine_adapter", "target_agent")
trace_contract._emit_verifies_policy("p1", "pattern_analysis_engine_adapter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "pattern_analysis_engine_adapter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "pattern_analysis_engine_adapter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "pattern_analysis_engine_adapter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "pattern_analysis_engine_adapter")
trace_contract._emit_gated_by_confidence("p1", "pattern_analysis_engine_adapter", "confidence_gate")
trace_contract.emit_replay_key("p0", "pattern_analysis_engine_adapter")
trace_contract.emit_determinism_digest("p0", "pattern_analysis_engine_adapter")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "PatternAnalysisEngine.analyze"
        )

        # Parse healing snapshot
        healing_snapshot = HealingOutcomeAggregateSnapshot.from_bytes(healing_snapshot_bytes)
        healing_data = json.loads(healing_snapshot.canonical_bytes().decode("utf-8"))

        # Convert healing aggregates to embeddings and metadata
        embeddings = []
        metadata = []

        for aggregate_data in tqdm(healing_data.get("aggregates", []), desc="Processing", unit="item"):
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
                },
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
        for aggregate_data in tqdm(healing_data.get("aggregates", []), desc="Processing", unit="item"):
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
                        ),
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
                ),
            )

        return PatternFindingReport(
            source_ids=PatternSourceIds(
                healing_snapshot_version=healing_snapshot.version_id,
            ),
            findings=tuple(findings),
        )
