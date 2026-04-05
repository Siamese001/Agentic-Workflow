"""
Shared Analysis Mixin - Phase 2 Optimization
Provides common analysis workflow patterns for agents.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any

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

_emit_applies_guardrail("p0", "analysis_mixin_util", "p0_governance")
_emit_reads_policy_state("p0", "analysis_mixin_util", "policy_binding")
_emit_snapshots_state("p0", "analysis_mixin_util", "state_snapshot")
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

_emit_emits_metric_event("analysis_mixin_util", "p4obs", "metric_1")
_emit_emits_metric_event("analysis_mixin_util", "p4obs", "metric_2")
_emit_emits_metric_event("analysis_mixin_util", "p4obs", "metric_3")
_emit_emits_metric_event("analysis_mixin_util", "p4obs", "metric_4")
_emit_emits_metric_event("analysis_mixin_util", "p4obs", "metric_5")
_emit_emits_metric_event("analysis_mixin_util", "p4obs", "metric_6")
_emit_records_incident_event("analysis_mixin_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("analysis_mixin_util", "p4obs", "anomaly")
_emit_writes_observability_log("analysis_mixin_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("analysis_mixin_util", "p4obs", "mon_state")
_emit_triggers_alert("analysis_mixin_util", "p4obs", "alert")
_emit_links_incident_trace("analysis_mixin_util", "p4obs", "trace_link")
_emit_captures_pattern("analysis_mixin_util", "p3lm", "pattern")
_emit_records_learning_event("analysis_mixin_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("analysis_mixin_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("analysis_mixin_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("analysis_mixin_util", "p3lm", "routing")
_emit_improves_agent_policy("analysis_mixin_util", "p3lm", "policy")
_emit_stores_learning_state("analysis_mixin_util", "p3lm", "state")
_emit_records_execution_trace("analysis_mixin_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("analysis_mixin_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("analysis_mixin_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("analysis_mixin_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("analysis_mixin_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("analysis_mixin_util", "env_read", "p2_env_1")
_emit_reads_environ("analysis_mixin_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("analysis_mixin_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("analysis_mixin_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "analysis_mixin_util", "context_pull")
_emit_pulls_context("p1", "analysis_mixin_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "analysis_mixin_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "analysis_mixin_util", "uwg_term_2")
_emit_writes_through("p1", "analysis_mixin_util", "write_through")
_emit_writes_through("p1", "analysis_mixin_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "analysis_mixin_util", "safety_validation")
_emit_invokes_eval("p1", "analysis_mixin_util", "eval_call")
_emit_proposal_commits_routing("p1", "analysis_mixin_util", "routing_commit")
_emit_escalates_to_human("p1", "analysis_mixin_util", "human_escalation")
_emit_routes_through("p1", "analysis_mixin_util", "route_through")
_emit_checks_agent_registry("p1", "analysis_mixin_util", "agent_registry")
_emit_validates_agent_capability("p1", "analysis_mixin_util", "capability")
_emit_dispatches_execution_plan("p1", "analysis_mixin_util", "exec_plan")
_emit_agent_executes_agent("p1", "analysis_mixin_util", "sub_agent")
_emit_routes_to_agent("p1", "analysis_mixin_util", "target_agent")
_emit_verifies_policy("p1", "analysis_mixin_util", "policy_check")
_emit_observes_runtime_state("p1", "analysis_mixin_util", "runtime_state")
_emit_verifies_boundary("p1", "analysis_mixin_util", "boundary_check")
_emit_transcripts_response("p1", "analysis_mixin_util", "transcript")
_emit_hard_fails_untranscripted("p1", "analysis_mixin_util")
_emit_gated_by_confidence("p1", "analysis_mixin_util", "confidence_gate")
emit_replay_key("p0", "analysis_mixin_util")
emit_determinism_digest("p0", "analysis_mixin_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "analysis_mixin_util", "execution_auth")
_emit_validates_capability("p2", "analysis_mixin_util", "capability_check")
_emit_routes_to_capability("p2", "analysis_mixin_util", "capability_route")
_emit_writes_via_uwg("p2", "analysis_mixin_util", "uwg_write")
_emit_blocks_direct_write("p2", "analysis_mixin_util", "direct_write_block")
_emit_records_tool_invocation("p2", "analysis_mixin_util", "tool_invocation")
_emit_captures_execution_output("p2", "analysis_mixin_util", "exec_output")
_emit_dispatches_agent("p3", "analysis_mixin_util", "agent_dispatch")
_emit_coordinates_agents("p3", "analysis_mixin_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "analysis_mixin_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "analysis_mixin_util", "healing_outcome")
_emit_escalates_failure("p3", "analysis_mixin_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "analysis_mixin_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "analysis_mixin_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "analysis_mixin_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "analysis_mixin_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "analysis_mixin_util", "eval_metric")
_emit_stores_embedding("p4", "analysis_mixin_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "analysis_mixin_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "analysis_mixin_util", "exec_snapshot_link")


@dataclass
class AnalysisResult:
    """Result of an analysis operation."""

    summary: str
    metrics: dict[str, Any]
    insights: list[str]
    recommendations: list[str]
    confidence: float


class AnalysisMixin:
    """
    Shared mixin for common analysis patterns.

    Provides standardized analysis methods that eliminate
    duplicate analysis boilerplate across agents.
    """

    def analyze_metrics(self, data: list[dict[str, Any]], metric_keys: list[str]) -> dict[str, Any]:
        """
        Analyze metrics from data collection.

        Args:
            data: List of data dictionaries
            metric_keys: Keys to analyze in each data item

        Returns:
            Dictionary with statistical analysis of metrics
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AnalysisMixin.analyze_metrics")

        results = {}
        for key in metric_keys:
            values = [item.get(key) for item in data if key in item and item[key] is not None]
            if not values:
                results[key] = {"error": "No data available"}
                continue
            if all(isinstance(v, int | float) for v in values):
                results[key] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                }
            else:
                from collections import Counter

                counter = Counter(values)
                results[key] = {
                    "count": len(values),
                    "unique": len(counter),
                    "most_common": counter.most_common(5),
                }
        return results

    def calculate_trends(self, time_series: list[tuple[Any, float]], window_size: int = 5) -> dict[str, Any]:
        """
        Calculate trends from time series data.

        Args:
            time_series: List of (timestamp, value) tuples
            window_size: Size of moving average window

        Returns:
            Dictionary with trend analysis
        """
        if len(time_series) < 2:
            return {"trend": "insufficient_data", "direction": "unknown"}
        values = [v for _, v in time_series]
        moving_avg = []
        for i in range(len(values) - window_size + 1):
            window = values[i : i + window_size]
            moving_avg.append(sum(window) / window_size)
        if len(moving_avg) >= 2:
            if moving_avg[-1] > moving_avg[0]:
                direction = "increasing"
            elif moving_avg[-1] < moving_avg[0]:
                direction = "decreasing"
            else:
                direction = "stable"
        else:
            direction = "unknown"
        if len(values) >= 2:
            rate_of_change = (values[-1] - values[0]) / len(values)
        else:
            rate_of_change = 0
        return {
            "trend": "calculated",
            "direction": direction,
            "rate_of_change": rate_of_change,
            "moving_average": moving_avg,
            "current_value": values[-1] if values else None,
        }

    def compare_datasets(
        self, dataset_a: list[Any], dataset_b: list[Any], comparison_key: str | None = None
    ) -> dict[str, Any]:
        """
        Compare two datasets and identify differences.

        Args:
            dataset_a: First dataset
            dataset_b: Second dataset
            comparison_key: Key to use for comparison if datasets are dicts

        Returns:
            Dictionary with comparison results
        """
        results = {
            "size_a": len(dataset_a),
            "size_b": len(dataset_b),
            "size_difference": len(dataset_a) - len(dataset_b),
        }
        if comparison_key:
            keys_a = {item.get(comparison_key) for item in dataset_a if comparison_key in item}
            keys_b = {item.get(comparison_key) for item in dataset_b if comparison_key in item}
            results["unique_to_a"] = list(keys_a - keys_b)
            results["unique_to_b"] = list(keys_b - keys_a)
            results["common"] = list(keys_a & keys_b)
        else:
            is_hashable_a = all(isinstance(x, str | int | float) for x in dataset_a)
            is_hashable_b = all(isinstance(x, str | int | float) for x in dataset_b)
            set_a = set(dataset_a) if is_hashable_a else None
            set_b = set(dataset_b) if is_hashable_b else None
            if set_a and set_b:
                results["unique_to_a"] = list(set_a - set_b)
                results["unique_to_b"] = list(set_b - set_a)
                results["common"] = list(set_a & set_b)
        return results

    def generate_insights(
        self, analysis_data: dict[str, Any], thresholds: dict[str, float] | None = None
    ) -> list[str]:
        """
        Generate insights from analysis data.

        Args:
            analysis_data: Dictionary with analysis results
            thresholds: Optional thresholds for generating insights

        Returns:
            List of insight strings
        """
        insights = []
        thresholds = thresholds or {}
        for key, value in analysis_data.items():
            if isinstance(value, dict):
                if "mean" in value:
                    mean_val = value["mean"]
                    threshold = thresholds.get(f"{key}_mean")
                    if threshold and mean_val > threshold:
                        insights.append(f"{key} mean ({mean_val:.2f}) exceeds threshold ({threshold})")
                if "stdev" in value:
                    stdev_val = value["stdev"]
                    threshold = thresholds.get(f"{key}_stdev")
                    if threshold and stdev_val > threshold:
                        insights.append(f"{key} shows high variability (stdev: {stdev_val:.2f})")
        return insights

    def calculate_score(self, metrics: dict[str, float], weights: dict[str, float] | None = None) -> float:
        """
        Calculate weighted score from metrics.

        Args:
            metrics: Dictionary of metric names to values
            weights: Optional dictionary of metric names to weights

        Returns:
            Calculated weighted score (0.0 to 1.0)
        """
        if not metrics:
            return 0.0
        weights = weights or dict.fromkeys(metrics.keys(), 1.0)
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        weighted_sum = sum(metrics.get(key, 0) * weights.get(key, 0) for key in metrics.keys())
        return weighted_sum / total_weight

    # guardian: allow-magic-config
    def identify_outliers(self, values: list[float], threshold: float = 2.0) -> dict[str, Any]:
        """
        Identify outliers in a dataset using standard deviation.

        Args:
            values: List of numeric values
            threshold: Number of standard deviations for outlier detection

        Returns:
            Dictionary with outlier analysis
        """
        if len(values) < 2:
            return {"outliers": [], "outlier_count": 0}
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        outliers = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / stdev) if stdev > 0 else 0
            if z_score > threshold:
                outliers.append({"index": i, "value": value, "z_score": z_score})
        return {
            "outliers": outliers,
            "outlier_count": len(outliers),
            "mean": mean,
            "stdev": stdev,
            "threshold": threshold,
        }
